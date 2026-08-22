from __future__ import annotations

import unittest

from src.internet.web import WebClient
from src.mesias import Mesias


class WebTestCase(unittest.TestCase):
    def test_mesias_detects_factual_queries_for_web(self) -> None:
        mesias = Mesias.__new__(Mesias)
        self.assertTrue(mesias.should_search_web("Sabes que dia es hoy"))
        self.assertTrue(mesias.should_search_web(
            "Necesito el numero de habitantes de Asturias"))
        self.assertFalse(mesias.should_search_web(
            "Cuentame un cuento infantil"))

    def test_search_query_removes_noise_words(self) -> None:
        query = "busca en internet la capital de rusia y sus habitantes"
        self.assertEqual(WebClient._build_search_query(
            query), "capital rusia habitantes")

    def test_search_prefers_high_relevance_terms(self) -> None:
        query_terms = {"capital", "rusia", "habitantes"}
        score = WebClient._score_search_result(
            query_terms,
            title="Capital de Rusia y sus habitantes",
            description="",
            domain="es.wikipedia.org",
        )
        weak_score = WebClient._score_search_result(
            query_terms,
            title="Capital Markets",
            description="Finanzas y trading",
            domain="capital.com",
        )
        self.assertGreater(score, weak_score)

    def test_search_prefers_authoritative_domain_when_relevance_is_equal(self) -> None:
        query_terms = {"vacunas", "salud"}
        preferred_score = WebClient._score_search_result(
            query_terms,
            title="Vacunas y salud",
            description="Guia oficial",
            domain="who.int",
        )
        generic_score = WebClient._score_search_result(
            query_terms,
            title="Vacunas y salud",
            description="Guia comercial",
            domain="example-shop.com",
        )
        self.assertGreater(preferred_score, generic_score)


if __name__ == "__main__":
    unittest.main()
