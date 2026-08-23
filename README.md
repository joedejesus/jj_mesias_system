# Mesias

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-4051B5)
![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063)
![Gradio](https://img.shields.io/badge/Gradio-UI-F97316?logo=gradio&logoColor=white)
![Transformers](https://img.shields.io/badge/Transformers-Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)
![PyTorch](https://img.shields.io/badge/PyTorch-Inference-EE4C2C?logo=pytorch&logoColor=white)
![LoRA](https://img.shields.io/badge/LoRA-Training-6A5ACD)
![PEFT](https://img.shields.io/badge/PEFT-Fine--Tuning-7B61FF)
![Datasets](https://img.shields.io/badge/Datasets-HF%20Datasets-FFCC4D)
![HTTPS](https://img.shields.io/badge/Web-HTTPS-0A66C2)
![Local First](https://img.shields.io/badge/Local-First-2E8B57)

Mesias es un asistente local en Python orientado a inferencia, memoria conversacional simple, contexto web seguro por HTTPS y entrenamiento LoRA prudente sobre un modelo local.

Es un proyecto de portfolio técnico centrado en IA aplicada, arquitectura Python modular e integración end-to-end de inferencia, API, interfaz, web segura, persistencia y pipeline de entrenamiento.

> 🧭 La documentación para poner este proyecto en marcha está en la sección [docs](docs). Si quieres usar Mesias sin estudiar todavía todo el repositorio, sigue este orden: [docs/comandos.md](docs/comandos.md), [docs/funcionamiento.md](docs/funcionamiento.md) y [docs/laboratorio.md](docs/laboratorio.md).

## 🖥️ Requisitos de máquina recomendados

Mesias no está pensado para cualquier equipo. Para una experiencia razonable, conviene usar una máquina limpia, estable y con recursos suficientes.

- recomendable: al menos 32 GB de RAM
- recomendable: CPU solvente y almacenamiento rápido
- recomendable: entorno local limpio, sin dependencias mezcladas con otros proyectos
- importante: el rendimiento real depende también del modelo local elegido y del estado general del sistema

Si el entorno es limitado, está cargado de procesos o no cumple un mínimo de recursos, Mesias puede arrancar mal, ir lento o fallar al cargar el modelo.

Para entrenamiento LoRA, conviene extremar el cuidado: revisa primero la sección [docs](docs) y lee de forma explícita [docs/laboratorio.md](docs/laboratorio.md) y [docs/comandos.md](docs/comandos.md) antes de lanzar cualquier proceso de entrenamiento.

## 🧩 Entorno validado

Para evitar expectativas erróneas, el flujo de uso de este repositorio está planteado alrededor de este escenario:

- ejecución local desde Windows
- entorno `venv` creado dentro de la raíz del proyecto
- modelo descargado manualmente dentro de `src/modelo`
- arranque por la vía canónica `python.exe -m src ...`

Si intentas usar otra disposición, otro sistema o un entorno mezclado con dependencias ajenas, pueden hacer falta ajustes adicionales.

## 🟢 Puesta en marcha rápida

Si vienes desde GitHub y quieres dejar Mesias funcionando sin revisar todavía todo el código, este es el recorrido corto.

### 1. Descargar el proyecto desde GitHub

```cmd
git clone <URL_DEL_REPOSITORIO>
cd jj_mesias_system
```

Si ya descargaste el repositorio como ZIP, descomprímelo y abre esa carpeta en VS Code.

### 2. Abrir primero estos archivos

- [README.md](README.md): visión general del proyecto
- [docs/comandos.md](docs/comandos.md): comandos exactos para arrancar consola, API o Gradio
- [docs/funcionamiento.md](docs/funcionamiento.md): contexto mínimo para entender cómo está organizado

Con esos tres archivos debería bastar para ponerlo en marcha sin tener que estudiar todo el repositorio de principio a fin.

### 3. Preparar el entorno

```cmd
scripts\setup.cmd
```

### 4. Descargar el modelo local

Motor validado:

- `Qwen/Qwen2.5-3B-Instruct`
- `https://huggingface.co/Qwen/Qwen2.5-3B-Instruct`

Copia sus archivos dentro de `src/modelo`.

### 5. Arrancar Mesias

```cmd
.\venv\Scripts\python.exe -m src console
```

O bien:

```cmd
.\venv\Scripts\python.exe -m src api
.\venv\Scripts\python.exe -m src gradio --host 127.0.0.1 --port 7860
```

## 🚀 Qué es Mesias

Mesias no intenta competir con modelos cerrados gigantes ni perseguir modas. Está planteado como una base de estudio y laboratorio para aprender IA con una arquitectura que se pueda leer, modificar, romper, reparar y volver a entender sin convertirse en una plataforma inflada.

La propuesta es concreta: ofrecer un proyecto local, razonablemente pequeño y técnicamente claro donde convivan inferencia, memoria, web segura, varias interfaces y entrenamiento sin perder legibilidad.

## 👨‍💻 Perfil técnico

- arquitectura modular en Python orientada a mantenibilidad y lectura del código
- inferencia local integrada con Transformers, PyTorch y artefactos de Hugging Face
- exposición del mismo núcleo funcional por CLI, FastAPI y Gradio
- separación explícita entre uso diario, persistencia, seguridad web y entrenamiento LoRA
- documentación operativa y estructura pensadas para facilitar revisión, aprendizaje y extensión

## 🎯 Para quién está hecho

Mesias está pensado para:

- estudiantes de IA, machine learning, deep learning o ciencia de datos
- personas que quieren una base local y controlable para experimentar con asistentes
- quien necesite entender cómo se conectan modelo, memoria, web, API, interfaz y validación en un mismo repositorio

No está pensado como sustituto directo de un modelo frontier ni como una solución optimizada al máximo sacrificando claridad.

## ✨ Qué intenta hacer bien

- cargar un modelo local de forma coherente
- reutilizar el mismo núcleo en consola, API y Gradio
- mantener una memoria conversacional simple y legible
- usar contexto web solo cuando aporta valor y con restricciones seguras
- responder con cautela cuando no puede verificar un dato externo
- separar el entrenamiento LoRA del runtime diario
- seguir siendo lo bastante pequeño como para entenderlo de verdad

## 🧱 Tecnologías del proyecto

- Python como base del sistema
- PyTorch, Transformers, Tokenizers, Safetensors, SentencePiece, Accelerate y Hugging Face Hub para inferencia local
- PEFT, Datasets, BitsAndBytes y tqdm para preparación y ajuste LoRA
- FastAPI, Pydantic y Uvicorn para exponer y validar la API HTTP
- Gradio para interfaz rápida de exploración
- Requests y BeautifulSoup para recuperación y parsing de contexto web seguro
- JSON, JSON Lines y dotenv para persistencia simple y configuración local
- Jupyter, IPython y NBConvert para experimentación y apoyo de laboratorio
- HTTPS como única vía admitida para contexto web externo

## 🧠 Filosofía de diseño

Aquí no se persigue un “GPT casero” sobredimensionado. Se persigue una herramienta sobria y útil para aprender.

Eso implica varias decisiones deliberadas:

- si algo puede ser simple y suficiente, se prefiere a una solución más sofisticada pero opaca
- si una característica añade ruido sin mejorar aprendizaje o fiabilidad, no merece entrar
- si una integración externa no es estable, Mesias debe degradarse con dignidad
- si una parte del sistema no puede explicarse con claridad, probablemente todavía no está bien diseñada

## 📚 Sección de documentación

La documentación operativa del proyecto vive en la sección [docs](docs). Ese es el lugar correcto para seguir las instrucciones de uso paso a paso y para poner Mesias en marcha sin revisar todo el código fuente.

- [docs/comandos.md](docs/comandos.md): comandos literales para consola, API, Gradio, web y entrenamiento
- [docs/funcionamiento.md](docs/funcionamiento.md): arquitectura, flujo interno y compatibilidad
- [docs/laboratorio.md](docs/laboratorio.md): guía práctica para aprendizaje, portabilidad y LoRA

Orden recomendado si quieres arrancar rápido:

- primero [docs/comandos.md](docs/comandos.md)
- después [docs/funcionamiento.md](docs/funcionamiento.md)
- por último [docs/laboratorio.md](docs/laboratorio.md)

Si alguien va a usar Mesias, levantar la API, probar Gradio o tocar entrenamiento, debe seguir esa sección de documentación.

## ⚙️ Estado recomendado

- entrada canónica: `python.exe -m src ...`
- entorno esperado: `venv` recreado dentro de la raíz del proyecto
- uso diario: consola, API o Gradio desde la misma fachada en `src/mesias.py`
- web: opcional y limitada a URLs `https://`
- entrenamiento: separado del runtime diario con `tools/train_lora_seguro.py`

## 🖥️ Preparación del entorno

La preparación paso a paso ya está resumida en la puesta en marcha rápida y detallada en [docs/comandos.md](docs/comandos.md). Como referencia, ten en cuenta estos puntos:

- `venv` no debe reutilizarse si mueves el proyecto de carpeta
- conviene trabajar siempre con el Python del entorno local del proyecto
- la vía de ejecución recomendada es `python.exe -m src ...`

## 🤖 Motor recomendado

El motor validado para este proyecto es:

- `Qwen/Qwen2.5-3B-Instruct`
- `https://huggingface.co/Qwen/Qwen2.5-3B-Instruct`

Mesias espera encontrar en `src/modelo` al menos estos artefactos:

- `config.json`
- `tokenizer_config.json` o `tokenizer.json`
- `model.safetensors.index.json` o `model.safetensors` o `pytorch_model.bin`

## ⚡ Modos de arranque

Una vez preparado el entorno y descargado el modelo, desde la raíz del proyecto puedes arrancar Mesias así:

```cmd
.\venv\Scripts\python.exe -m src console
.\venv\Scripts\python.exe -m src api --host 127.0.0.1 --port 8000
.\venv\Scripts\python.exe -m src gradio --host 127.0.0.1 --port 7860
```

Para FastAPI también puedes usar:

```cmd
.\venv\Scripts\python.exe -m src api
```

Al arrancar, Mesias imprime la URL exacta que debes abrir en navegador. Si usas `0.0.0.0` como host, abre la URL local anunciada por Mesias, normalmente `http://127.0.0.1:8000/`, no `http://0.0.0.0:8000/`.

## ✅ Verificación mínima

Tras instalar dependencias, ejecuta:

```cmd
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Esta batería valida el arranque CLI, la serialización de memoria, la capa web segura y los imports de API y Gradio sin cargar el modelo completo en cada prueba.

## 🗂️ Estructura corta

- `src/mesias.py`: fachada principal
- `src/core`: carga del modelo, tokenizer y rutas
- `src/interfaces`: consola, API y Gradio
- `src/memory`: memoria persistente e historial por hablante
- `src/internet/web.py`: búsqueda y captura HTTPS
- `src/training`: preparación de datos y entrenamiento LoRA
- `data`: datasets, memoria, historial y logs
- `docs`: guías de uso, funcionamiento y laboratorio
- `tests`: comprobaciones automáticas de bajo coste

## 🔌 Contrato práctico

- la API pública recomendada para código consumidor es `Mesias`, `MesiasResponse`, `diagnose_runtime` y `load_mesias` desde `src` o desde el paquete raíz
- los wrappers de `src/interfaces/__init__.py` se mantienen por compatibilidad y comodidad, no como punto principal de extensión

## 🧩 Compatibilidad de motores Hugging Face

Mesias está validado sobre Qwen2.5-3B-Instruct, pero puede cargar otros motores locales de Hugging Face si respetan este contrato técnico básico:

- deben cargar con `AutoModelForCausalLM`
- deben incluir `config.json`
- deben exponer un tokenizer local reconocible por Mesias, al menos con `tokenizer_config.json` o `tokenizer.json`
- deben incluir pesos locales en `model.safetensors.index.json`, `model.safetensors` o `pytorch_model.bin`
- deben funcionar en modo local con `transformers`, sin depender de descarga remota en tiempo de ejecución
- si el motor se usará como chat, conviene que su tokenizer tenga un chat template compatible o equivalente

Si alguien quiere usar un motor distinto o crear uno nuevo, lo más seguro es exportarlo a una carpeta local con esos artefactos y probar primero `python.exe -m src console --doctor` y después una generación corta.

## 🌐 Política web

- Mesias solo consume URLs `https://`
- si detecta una pregunta factual o dependiente de información externa, intenta buscar apoyo web aunque el usuario no escriba literalmente `busca en internet`
- el descubrimiento automático prioriza resultados con coincidencia textual fuerte
- en empate o cercanía, favorece dominios más fiables como `wikipedia.org`, `wikidata.org`, `britannica.com`, `who.int`, `nih.gov`, `nasa.gov`, `noaa.gov`, `un.org` y `europa.eu`
- también da una preferencia menor a dominios terminados en `.gov`, `.edu` y `.org`
- si no encuentra suficiente relevancia o no puede verificar un dato, falla de forma explícita en vez de inventar una fuente peor

## ⚠️ Límites actuales

- si falla el DNS del entorno, Mesias sigue respondiendo en local pero la web puede quedar degradada
- la búsqueda web prioriza resultados textualmente relevantes, pero no sustituye un sistema de ranking documental avanzado
- la memoria es simple, persistente y legible; no pretende ser una base de conocimiento compleja

## 🛠️ Estabilidad y propósito educativo

Mesias puede requerir ajustes menores durante la ejecución o el entrenamiento, especialmente si se usa fuera del entorno validado o si se cambia el modelo, la configuración o el estado general de la máquina.

Eso no contradice su estabilidad base: siguiendo el procedimiento recomendado, el proyecto está planteado para comportarse de forma consistente y predecible dentro de su escenario de uso.

Esa fricción controlada también es intencional. Mesias no busca ocultar toda la complejidad detrás de una experiencia cerrada, sino servir como recurso educativo para que quien estudia pueda inspeccionar el código, entender el comportamiento del sistema y resolver ajustes o incidencias pequeñas cuando aparezcan.

Además, el proyecto cuenta con pruebas automáticas sobre los recorridos principales. Eso no significa que todo sea infalible en cualquier entorno, pero sí que existe una base validada para CLI, memoria, web segura e interfaces, y que el comportamiento esperado está cubierto por tests del repositorio.

## 🧪 Enfoque del proyecto

Mesias prioriza legibilidad, control local y separación clara de responsabilidades. Su valor está en reunir inferencia, memoria, web, varias interfaces y entrenamiento dentro de una base que siga siendo entendible y mantenible.