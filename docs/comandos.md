# Comandos disponibles en Mesias

Usa esta guia desde VS Code cuando tu terminal este en la raiz del proyecto y con `venv` activo.

La via canonica de arranque es `python.exe -m src ...`.

## Comandos literales

- Consola interactiva:

```cmd
python.exe -m src console
```

- Consola con una pregunta directa:

```cmd
python.exe -m src console "Explica que es una red neuronal"
```

- Consola con diagnostico:

```cmd
python.exe -m src console --doctor
```

- API:

```cmd
python.exe -m src api --host 127.0.0.1 --port 8000
```

- Arranque minimo equivalente:

```cmd
python.exe -m src api
```

- Si el puerto pedido ya esta ocupado, Mesias intenta subir en uno cercano libre y lo anuncia en consola.
- Al arrancar, Mesias imprime la URL exacta que debes abrir en navegador, por ejemplo `http://127.0.0.1:8000/` o `http://127.0.0.1:8001/`.
- Deja esa terminal abierta mientras uses la API.
- Si arrancas con `--host 0.0.0.0`, no abras `http://0.0.0.0:8000/` en el navegador: usa la URL local que imprime Mesias, normalmente `http://127.0.0.1:8000/`.

- Gradio:

```cmd
python.exe -m src gradio --host 127.0.0.1 --port 7860
```

- Consola con una fuente HTTPS manual:

```cmd
python.exe -m src console --url https://es.wikipedia.org/wiki/Mosc%C3%BA "Resume esta fuente en 5 lineas"
```

## Instalacion

- Preparacion automatica desde CMD:

```cmd
scripts\setup.cmd
```

- Instalacion manual:

```cmd
python.exe -m pip install -r requirements.txt
```

- Verificacion automatica tras la instalacion:

```cmd
python.exe -m unittest discover -s tests -p "test_*.py"
```

- Usa siempre el Python del entorno `venv` ya activado.
- Si mueves el proyecto, borra `venv` y recrealo.

## API util

- Flujo recomendado de arranque en navegador:

```cmd
python.exe -m src api
```

- Espera una linea como esta en consola:

```text
Abre http://127.0.0.1:8000/ o http://127.0.0.1:8000/docs en tu navegador.
```

- Abre esa URL exacta. La raiz `/` devuelve un resumen JSON de la API y `/docs` abre Swagger UI.

- URL base: abre `/` para ver un resumen rapido de endpoints.
- Documentacion interactiva: abre `/docs` en el navegador.
- Health: `GET /health`
- Roles: `GET /roles`
- Diagnostico: `GET /diagnostics`
- Generacion directa: `POST /generate`
- Chat con historial: `POST /chat`

### Ejemplo real de POST /generate

```cmd
curl -X POST http://127.0.0.1:8000/generate ^
	-H "Content-Type: application/json" ^
	-d "{\"prompt\":\"Explica que es una red neuronal en una frase\",\"role\":\"general\",\"history\":[],\"urls\":[]}"
```

### Ejemplo real de POST /chat

```cmd
curl -X POST http://127.0.0.1:8000/chat ^
	-H "Content-Type: application/json" ^
	-d "{\"prompt\":\"y ponme un ejemplo\",\"role\":\"general\",\"history\":[{\"role\":\"user\",\"content\":\"Explica que es una red neuronal en una frase\"}],\"urls\":[]}"
```

### Respuesta esperada

```json
{
	"text": "...",
	"role": "general",
	"prompt_tokens": 123,
	"completion_tokens": 45,
	"total_tokens": 168,
	"messages": [
		{"role": "system", "content": "..."},
		{"role": "user", "content": "..."}
	]
}
```

## Solucion de problemas de FastAPI

- Si el navegador dice que no puede conectarse, comprueba primero que la terminal donde lanzaste `python.exe -m src api` siga abierta.
- Si el puerto `8000` estaba ocupado, abre el puerto alternativo que Mesias imprime en consola.
- Si ves `Uvicorn running on http://0.0.0.0:8000`, no copies esa URL al navegador; abre `http://127.0.0.1:8000/` o la URL exacta anunciada por Mesias.
- Si `/` responde pero ves un `404` para `/favicon.ico`, eso ya no es un error: Mesias responde `204 No Content` para evitar ruido del navegador.

## Web segura

- Mesias solo descarga fuentes `https://`.
- En consola y API, puedes pasar contexto web manual con `--url` o `urls`, pero Mesias tambien intenta buscar automaticamente cuando detecta una pregunta factual o dependiente de informacion externa.
- En Gradio, esa misma deteccion automatica se aplica aunque no escribas literalmente `busca en internet`.
- Si no logra verificar bien el dato, intenta responder con mas cautela en vez de afirmar algo inventado.
- Si falla DNS o la salida web del entorno, Mesias sigue funcionando en local pero sin apoyo web.

## Entrenamiento LoRA

- Dataset minimo: [data/ejemplo_entrenamiento.jsonl](../data/ejemplo_entrenamiento.jsonl)
- Dataset ampliado: [data/dataset_entrenamiento_docente.jsonl](../data/dataset_entrenamiento_docente.jsonl)
- Estado de archivos persistentes: [data/README.md](../data/README.md)
- Preparacion de datos: [src/training/preparacion_datos.py](../src/training/preparacion_datos.py)
- Entrenamiento: [src/training/entrenamiento.py](../src/training/entrenamiento.py)
- Preparacion del entrenamiento:

```cmd
python.exe .\tools\train_lora_seguro.py --prepare-only
```

- Preparacion usando el dataset de ejemplo para aprender el flujo:

```cmd
python.exe .\tools\train_lora_seguro.py --dataset .\data\ejemplo_entrenamiento.jsonl --prepare-only
```

- Entrenamiento con dataset docente:

```cmd
python.exe .\tools\train_lora_seguro.py --dataset .\data\dataset_entrenamiento_docente.jsonl
```
