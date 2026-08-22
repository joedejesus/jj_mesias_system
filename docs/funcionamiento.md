# Funcionamiento del sistema Mesias

Mesias usa un modelo local en [src/modelo](../src/modelo). El codigo solo lo localiza, valida y carga.

## Flujo principal

1. [src/core/model_loader.py](../src/core/model_loader.py) resuelve la ruta del modelo y comprueba que existan tokenizer, configuracion y pesos.
2. [src/mesias.py](../src/mesias.py) prepara mensajes, llama al modelo y registra logs.
3. [src/interfaces](../src/interfaces) reutiliza esa misma clase para consola, API y Gradio.
4. [src/internet/web.py](../src/internet/web.py) añade contexto web con fuentes HTTPS seguras si lo pides y si la conectividad funciona.
5. [src/memory](../src/memory) guarda memoria simple e historial conversacional en [data](../data).
6. [src/training](../src/training) prepara datasets y entrena adaptadores LoRA sin tocar el modelo base.

## Lo importante para entender el proyecto

- El centro real es [src/mesias.py](../src/mesias.py).
- La entrada de usuario recomendada es `python -m src`, aunque existan atajos de compatibilidad.
- La carga del modelo vive en [src/core](../src/core).
- Las interfaces no tienen logica propia de inferencia; solo llaman a Mesias.
- La memoria persistente puede recordar datos simples del hablante y guardarlos en JSON compacto.
- Si la memoria o el historial quedan corruptos, Mesias intenta aislar el JSON roto y reconstruir un estado vacio.
- Mesias detecta algunas preguntas factuales o dependientes de informacion externa para intentar apoyo web sin exigir que el usuario lo pida con una formula exacta.
- El entrenamiento esta separado del uso diario.
- La web y la memoria son opcionales.

## Mapa corto de carpetas

- [../src](../src): codigo principal.
- [../data](../data): datasets, memoria, logs y checkpoints.
- [../notebooks](../notebooks): pruebas manuales y apoyo para aprender.
- [../tools](../tools): utilidades auxiliares.
- [comandos.md](comandos.md), [funcionamiento.md](funcionamiento.md) y [laboratorio.md](laboratorio.md): las 3 guias cortas del proyecto.

## Diagnostico

- Consola: `--doctor`
- API: `GET /diagnostics`
- Humo automatizado: `python -m unittest discover -s tests -p "test_*.py"`

## Arranque de FastAPI

- La forma minima recomendada es `python.exe -m src api` desde la raiz del proyecto con `venv` activo.
- Si necesitas fijar host o puerto, usa `python.exe -m src api --host 127.0.0.1 --port 8000`.
- Si el puerto pedido esta ocupado, la API busca uno cercano libre y Mesias imprime la URL correcta para abrir en navegador.
- Si arrancas con `0.0.0.0`, Mesias sigue mostrando una URL local util para navegador, normalmente `127.0.0.1`, para evitar la confusion de abrir `0.0.0.0`.
- La raiz `/` existe para comprobacion rapida en navegador y `/docs` expone Swagger UI.

## Web segura

- Mesias solo consume fuentes `https://`.
- En consola, API y Gradio existe una heuristica ligera para detectar preguntas como fecha, poblacion, clima, capitales u otros datos externos que conviene contrastar con web.
- Cuando esa heuristica salta, Mesias intenta descubrir fuentes HTTPS antes de responder.
- El ranking web favorece dominios preferidos y mas fiables, por ejemplo `wikipedia.org`, `wikidata.org`, `britannica.com`, `who.int`, `nih.gov`, `nasa.gov`, `noaa.gov`, `un.org` y `europa.eu`.
- Como regla secundaria, tambien prioriza `.gov`, `.edu` y `.org` frente a dominios menos institucionales cuando la relevancia textual es parecida.
- Si la red falla, Mesias no se cae: responde sin contexto web o informa del problema, intentando evitar afirmaciones tajantes cuando no puede verificar.

## Compatibilidad de motores

Aunque el proyecto viene preparado para Qwen2.5-3B-Instruct, el cargador de [src/core/model_loader.py](../src/core/model_loader.py) admite otros motores locales de Hugging Face si cumplen estas condiciones:

- `config.json` presente.
- `tokenizer_config.json` o `tokenizer.json` presente.
- Pesos locales en `model.safetensors.index.json`, `model.safetensors` o `pytorch_model.bin`.
- Compatibilidad con `AutoModelForCausalLM` de `transformers`.
- Uso local sin depender de descargas remotas durante la inferencia.

Si alguien crea un motor nuevo, debe exportarlo a una carpeta con esa estructura y validarlo primero con `python -m src console --doctor`.

## Portabilidad

- El proyecto usa rutas relativas y se puede mover de carpeta.
- El entorno [../venv](../venv) debe recrearse si mueves el proyecto.
- Usa siempre ese entorno para no mezclar dependencias.

## Si quieres leer el codigo sin perderte

1. Empieza por [src/mesias.py](../src/mesias.py).
2. Sigue con [src/core/model_loader.py](../src/core/model_loader.py).
3. Luego mira [src/interfaces/roles.py](../src/interfaces/roles.py).
4. Deja [src/training](../src/training) para el final.
