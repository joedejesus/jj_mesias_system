from __future__ import annotations

"""Cliente web ligero y seguro para enriquecer respuestas de Mesias."""

import re
import socket
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = "MesiasBot/1.0 (+https://local.mesias)"
DEFAULT_CONNECTIVITY_TEST_URL = "https://www.who.int/"
DEFAULT_PREFERRED_DOMAINS = (
    "wikipedia.org",
    "wikidata.org",
    "britannica.com",
    "who.int",
    "nih.gov",
    "nasa.gov",
    "noaa.gov",
    "un.org",
    "europa.eu",
)
PREFERRED_DOMAIN_SUFFIXES = (".gov", ".edu", ".org")


class _HTMLTextExtractor(HTMLParser):
    """Extrae titulo y texto visible de HTML para el contexto web de Mesias."""

    def __init__(self) -> None:
        super().__init__()
        self._title_parts: List[str] = []
        self._text_parts: List[str] = []
        self._inside_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        elif tag == "title":
            self._inside_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text or self._skip_depth > 0:
            return
        if self._inside_title:
            self._title_parts.append(text)
        self._text_parts.append(text)

    @property
    def title(self) -> str:
        return " ".join(self._title_parts).strip()

    @property
    def text(self) -> str:
        text = " ".join(self._text_parts)
        return re.sub(r"\s+", " ", text).strip()


@dataclass
class WebDocument:
    """Documento web ya descargado y reducido al contenido util para Mesias."""
    url: str
    title: str
    content: str
    domain: str


@dataclass
class WebFetchError:
    """Representa un error de descarga web que Mesias puede reportar sin romperse."""
    url: str
    error: str


@dataclass
class WebConnectivityStatus:
    """Estado resumido de conectividad web que usa el diagnostico de Mesias."""
    dns_ok: bool
    http_ok: bool
    checked_url: str
    detail: str


class WebClient:
    """Cliente web ligero para recuperar texto util desde URLs en Mesias."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = 15,
        retries: int = 2,
        preferred_domains: Optional[Iterable[str]] = None,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.retries = max(1, retries)
        preferred = preferred_domains or DEFAULT_PREFERRED_DOMAINS
        self.preferred_domains = tuple(
            domain.lower().lstrip(".") for domain in preferred if domain
        )

    def fetch(self, url: str, max_chars: int = 4000) -> WebDocument:
        """Descarga una URL valida y devuelve un documento listo para Mesias."""
        self._validate_url(url)
        raw_html = self._read_url_text(url)

        parser = _HTMLTextExtractor()
        parser.feed(raw_html)
        parsed_url = urlparse(url)
        content = parser.text[:max_chars].strip()
        title = parser.title or parsed_url.netloc
        return WebDocument(
            url=url,
            title=title,
            content=content,
            domain=parsed_url.netloc,
        )

    def fetch_many(self, urls: Iterable[str], max_chars: int = 4000) -> List[WebDocument]:
        """Descarga varias URLs y falla si cualquiera de ellas no puede leerse."""
        documents: List[WebDocument] = []
        for url in urls:
            documents.append(self.fetch(url, max_chars=max_chars))
        return documents

    def search(self, query: str, max_results: int = 3) -> List[str]:
        """Descubre URLs HTTPS publicas relevantes a partir de una consulta."""
        normalized_query = self._build_search_query(query)
        if not normalized_query:
            raise RuntimeError("La consulta web no puede estar vacia.")
        query_terms = set(normalized_query.split())

        search_url = (
            "https://www.bing.com/search?format=rss"
            f"&q={quote_plus(normalized_query)}"
        )
        payload = self._read_url_text(search_url)
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise RuntimeError(
                "La fuente de descubrimiento web devolvio un formato no valido."
            ) from exc
        ranked_results: List[tuple[int, str]] = []
        for item in root.findall("./channel/item"):
            link = (item.findtext("link") or "").strip()
            if not link:
                continue
            parsed_link = urlparse(link)
            if parsed_link.scheme != "https" or not parsed_link.netloc:
                continue
            title = (item.findtext("title") or "").strip().lower()
            description = (item.findtext("description") or "").strip().lower()
            score = self._score_search_result(
                query_terms,
                title=title,
                description=description,
                domain=parsed_link.netloc.lower(),
                preferred_domains=self.preferred_domains,
            )
            ranked_results.append((score, link))

        minimum_score = 1 if len(query_terms) <= 1 else 2
        ranked_results.sort(key=lambda entry: entry[0], reverse=True)

        urls: List[str] = []
        for score, link in ranked_results:
            if score < minimum_score:
                continue
            if link not in urls:
                urls.append(link)
            if len(urls) >= max_results:
                break

        if not urls and len(query_terms) <= 1:
            for _, link in ranked_results:
                if link not in urls:
                    urls.append(link)
                if len(urls) >= max_results:
                    break

        if not urls:
            raise RuntimeError(
                "No se encontraron resultados HTTPS utiles para la consulta."
            )
        return urls

    def fetch_many_safe(
        self,
        urls: Iterable[str],
        max_chars: int = 4000,
    ) -> tuple[List[WebDocument], List[WebFetchError]]:
        """Descarga varias URLs sin interrumpir Mesias si alguna fuente falla."""
        documents: List[WebDocument] = []
        errors: List[WebFetchError] = []
        for url in urls:
            try:
                documents.append(self.fetch(url, max_chars=max_chars))
            except RuntimeError as exc:
                errors.append(WebFetchError(url=url, error=str(exc)))
        return documents, errors

    def build_context(self, urls: Iterable[str], max_chars: int = 2000) -> str:
        """Construye un bloque textual de contexto web reutilizable por Mesias."""
        documents = self.fetch_many(urls, max_chars=max_chars)
        blocks = []
        for document in documents:
            blocks.append(
                f"Fuente: {document.title} ({document.url})\nContenido: {document.content}"
            )
        return "\n\n".join(blocks)

    def diagnose_connectivity(self, test_url: str = DEFAULT_CONNECTIVITY_TEST_URL) -> WebConnectivityStatus:
        """Comprueba DNS y salida HTTP para el modulo web de Mesias."""
        self._validate_url(test_url)
        parsed = urlparse(test_url)
        try:
            socket.getaddrinfo(parsed.hostname, parsed.port or 443)
        except socket.gaierror as exc:
            return WebConnectivityStatus(
                dns_ok=False,
                http_ok=False,
                checked_url=test_url,
                detail=f"Fallo DNS: {exc}",
            )

        try:
            self.fetch(test_url, max_chars=200)
        except RuntimeError as exc:
            return WebConnectivityStatus(
                dns_ok=True,
                http_ok=False,
                checked_url=test_url,
                detail=str(exc),
            )

        return WebConnectivityStatus(
            dns_ok=True,
            http_ok=True,
            checked_url=test_url,
            detail="Conectividad web operativa.",
        )

    @staticmethod
    def _validate_url(url: str) -> None:
        """Valida que la URL sea HTTPS antes de usarla en Mesias."""
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise RuntimeError(
                f"URL no soportada: {url}. Solo se permiten URLs HTTPS seguras.")
        if not parsed.netloc:
            raise RuntimeError(f"URL invalida: {url}")

    def _read_url_text(self, url: str) -> str:
        last_error: Optional[Exception] = None
        for _ in range(self.retries):
            request = Request(url, headers={"User-Agent": self.user_agent})
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    return response.read().decode("utf-8", errors="ignore")
            except HTTPError as exc:
                raise RuntimeError(
                    f"Error HTTP {exc.code} al abrir {url}") from exc
            except URLError as exc:
                last_error = exc

        if isinstance(last_error, URLError):
            raise RuntimeError(
                f"No se pudo conectar con {url}: {last_error.reason}") from last_error
        raise RuntimeError(f"No se pudo leer la URL: {url}")

    @staticmethod
    def _build_search_query(query: str) -> str:
        words = re.findall(r"\w+", query.lower())
        stopwords = {
            "a", "al", "busca", "buscar", "busques", "con", "consulta", "de", "del",
            "el", "en", "esta", "este", "favor", "informacion", "información", "internet",
            "investiga", "la", "las", "los", "necesito", "numero", "número", "online",
            "para", "por", "pueda", "puedes", "que", "se", "su", "sus", "sobre", "un", "una", "web", "y",
        }
        cleaned_words = [word for word in words if word not in stopwords]
        return " ".join(cleaned_words[:8]).strip()

    @staticmethod
    def _score_search_result(
        query_terms: set[str],
        *,
        title: str,
        description: str,
        domain: str,
        preferred_domains: Iterable[str] = DEFAULT_PREFERRED_DOMAINS,
    ) -> int:
        title_terms = set(re.findall(r"\w+", title.lower()))
        description_terms = set(re.findall(r"\w+", description.lower()))
        domain_terms = set(re.findall(r"\w+", domain.lower()))
        normalized_domain = domain.lower().lstrip(".")
        score = 0
        score += sum(3 for term in query_terms if term in title_terms)
        score += sum(1 for term in query_terms if term in description_terms)
        score += sum(2 for term in query_terms if term in domain_terms)
        score += WebClient._domain_preference_bonus(
            normalized_domain,
            preferred_domains=preferred_domains,
        )
        if len(query_terms) >= 2:
            strong_matches = sum(
                1 for term in query_terms if term in title_terms or term in domain_terms)
            if strong_matches < 2:
                score -= 3
        return score

    @staticmethod
    def _domain_preference_bonus(
        domain: str,
        *,
        preferred_domains: Iterable[str] = DEFAULT_PREFERRED_DOMAINS,
    ) -> int:
        normalized_domain = domain.lower().lstrip(".")
        for preferred_domain in preferred_domains:
            normalized_preferred = preferred_domain.lower().lstrip(".")
            if normalized_domain == normalized_preferred or normalized_domain.endswith(
                f".{normalized_preferred}"
            ):
                return 4
        if any(normalized_domain.endswith(suffix) for suffix in PREFERRED_DOMAIN_SUFFIXES):
            return 2
        return 0


__all__ = [
    "DEFAULT_CONNECTIVITY_TEST_URL",
    "DEFAULT_USER_AGENT",
    "DEFAULT_PREFERRED_DOMAINS",
    "WebClient",
    "WebConnectivityStatus",
    "WebDocument",
    "WebFetchError",
]
