# Mesias

Mesias es un asistente local en Python orientado a inferencia, memoria conversacional simple, contexto web HTTPS y entrenamiento LoRA prudente sobre un modelo local que cada usuario descarga por separado.

## Por qué existe este proyecto

Mesias no nace para competir con modelos cerrados enormes ni para perseguir la última moda del sector. Nace como una herramienta de estudio y laboratorio para aprender IA con una base que sea estable, entendible, modificable y suficientemente escalable.

La idea es simple: si estás estudiando deep learning, machine learning, matemáticas o ciencia de datos, necesitas un sistema que haga bien unas pocas cosas importantes y que además puedas abrir, leer, romper, reparar y extender sin perderte en una arquitectura inflada.

Este proyecto prioriza:

- claridad antes que complejidad innecesaria
- estabilidad antes que velocidad de experimentar sin control
- componentes locales y legibles antes que dependencias mágicas
- aprendizaje práctico antes que marketing técnico

## Para quién está hecho

Mesias está pensado para:

- estudiantes de IA que quieren un proyecto real sobre el que aprender
- personas que necesitan una base local y controlable para probar ideas de NLP o asistentes
- quien quiera entender cómo se conectan inferencia, memoria, web, entrenamiento y validación en un mismo repositorio sin montar una plataforma enorme

No está pensado para quien busque un sustituto directo de un modelo frontier ni para quien necesite el máximo rendimiento posible a costa de legibilidad.

## Qué intenta hacer bien

- cargar un modelo local de forma coherente
- exponer el mismo núcleo en consola, API y Gradio
- permitir memoria conversacional simple sin convertir el proyecto en una base de datos compleja
- usar contexto web solo cuando aporta valor y sin abrir la puerta a fuentes inseguras
- responder con sobriedad cuando no puede verificar un dato, en vez de rellenar con seguridad falsa
- permitir entrenamiento LoRA prudente sin mezclarlo con el runtime diario
- mantenerse lo bastante pequeño como para que una persona pueda comprenderlo de verdad

## Filosofía de diseño

Aquí no se persigue un “GPT 5.6 casero”. Se persigue una herramienta sobria que sirva para avanzar en conocimiento.

Eso implica aceptar varias decisiones deliberadas:

- si algo puede ser simple y suficiente, se prefiere a una solución más sofisticada pero opaca
- si una característica añade ruido sin mejorar el aprendizaje o la fiabilidad, no merece entrar
- si una integración externa no es estable, Mesias debe degradarse con dignidad en vez de fingir que todo va bien
- si una parte del sistema no puede explicarse con claridad, probablemente todavía no está bien diseñada

## Estado recomendado

- Entrada canónica: `python.exe -m src ...`
- Entorno esperado: `venv` recreado dentro de la raíz del proyecto.
- Uso diario: consola, API o Gradio desde la misma fachada en `src/mesias.py`.
- Web: opcional y limitada a URLs `https://`.
- Entrenamiento: separado del runtime diario con `tools/train_lora_seguro.py`.

## Repositorio para GitHub

Este repositorio esta preparado para subirse sin incluir archivos pesados ni dependencias locales ya construidas.

- La carpeta `venv` no se versiona y en GitHub se considera vacia: cada usuario debe recrear su entorno local.
- Si mantienes una referencia publica en X con el snapshot exacto del entorno, enlazala desde aqui antes de publicar.
- La carpeta `src/modelo` tambien se publica vacia salvo archivos de ayuda: cada usuario debe descargar su propio motor local.

### Entorno local

La forma recomendada de recrearlo es una de estas dos:

```cmd
scripts\setup.cmd
```

o manualmente:

```cmd
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Motor recomendado

El motor validado para este proyecto es:

- `Qwen/Qwen2.5-3B-Instruct`
- `https://huggingface.co/Qwen/Qwen2.5-3B-Instruct`

Despues de descargarlo, copia sus artefactos dentro de `src/modelo`.

Mesias espera encontrar ahi, como minimo:

- `config.json`
- `tokenizer_config.json` o `tokenizer.json`
- `model.safetensors.index.json` o `model.safetensors` o `pytorch_model.bin`

## Arranque rápido

Desde la raíz del proyecto:

```cmd
.\venv\Scripts\python.exe -m src console
.\venv\Scripts\python.exe -m src api --host 127.0.0.1 --port 8000
.\venv\Scripts\python.exe -m src gradio --host 127.0.0.1 --port 7860
```

Para FastAPI, tambien puedes usar simplemente:

```cmd
.\venv\Scripts\python.exe -m src api
```

Al arrancar, Mesias imprime la URL exacta que debes abrir en navegador. Si usas `0.0.0.0` como host, abre la URL local anunciada por Mesias, normalmente `http://127.0.0.1:8000/`, no `http://0.0.0.0:8000/`.

## Verificación mínima

Tras instalar dependencias, ejecuta:

```cmd
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Esta batería valida el arranque CLI, la serialización de memoria, la capa web segura y los imports de API y Gradio sin requerir cargar el modelo completo en cada prueba.

## Estructura corta

- `src/mesias.py`: fachada principal.
- `src/core`: carga del modelo, tokenizer y rutas.
- `src/interfaces`: consola, API y Gradio.
- `src/memory`: memoria persistente e historial por hablante.
- `src/internet/web.py`: búsqueda y captura HTTPS.
- `src/training`: preparación de datos y entrenamiento LoRA.
- `data`: datasets, memoria, historial y logs.
- `docs`: guías breves de uso y funcionamiento.
- `tests`: comprobaciones automáticas de bajo coste.

## Contrato práctico

- La API pública recomendada para código consumidor es `Mesias`, `MesiasResponse`, `diagnose_runtime` y `load_mesias` desde `src` o desde el paquete raíz.
- Los wrappers de `src/interfaces/__init__.py` se conservan por compatibilidad y comodidad, no como punto principal de extensión.

## Compatibilidad de motores Hugging Face

Mesias está validado sobre Qwen2.5-3B-Instruct, pero puede cargar otros motores locales de Hugging Face si respetan el mismo contrato técnico básico:

- Deben cargar con `AutoModelForCausalLM`.
- Deben incluir `config.json`.
- Deben exponer un tokenizer local reconocible por Mesias, al menos con `tokenizer_config.json` o `tokenizer.json`.
- Deben incluir pesos locales en alguno de estos formatos: `model.safetensors.index.json`, `model.safetensors` o `pytorch_model.bin`.
- Deben ser utilizables en modo local con `transformers`, sin depender de descarga remota en tiempo de ejecución.
- Si el motor se va a usar como chat, conviene que su tokenizer tenga un chat template compatible o un formato de conversación equivalente.

Si otra persona quiere usar un motor distinto o crear uno nuevo, la forma más segura es exportarlo a una carpeta local con esos artefactos y probar primero `python.exe -m src console --doctor` y después una generación corta.

## Política web

- Mesias solo consume URLs `https://`.
- Si detecta una pregunta factual o dependiente de información externa, intenta buscar apoyo web aunque el usuario no escriba literalmente `busca en internet`.
- El descubrimiento automático prioriza resultados con coincidencia textual fuerte.
- En empate o cercanía, favorece dominios más fiables como `wikipedia.org`, `wikidata.org`, `britannica.com`, `who.int`, `nih.gov`, `nasa.gov`, `noaa.gov`, `un.org` y `europa.eu`.
- También da una preferencia menor a dominios terminados en `.gov`, `.edu` y `.org`.
- Si no encuentra suficiente relevancia o no puede verificar un dato, falla de forma explícita en vez de inventar una fuente peor.

## Límites actuales

- Si falla el DNS del entorno, Mesias sigue respondiendo en local pero la web puede quedar degradada.
- La búsqueda web prioriza resultados textualmente relevantes, pero no sustituye un sistema de ranking documental avanzado.
- La memoria es simple, persistente y legible; no pretende ser una base de conocimiento compleja.

## Valor para estudiantes y mantenibilidad

Para una persona en formación, el valor principal de Mesias no es solo que responda, sino que deja ver el camino completo:

- cómo se carga un modelo local
- cómo se construyen mensajes y prompts
- cómo se añaden interfaces distintas sin duplicar toda la lógica
- cómo se gestionan memoria, web y entrenamiento sin acoplarlo todo en un solo archivo gigante
- cómo se valida un proyecto con pruebas pequeñas y diagnósticos concretos

Si se mantiene esta disciplina, el proyecto puede aguantar bien el paso del tiempo como base de aprendizaje, prototipado y evolución gradual. No porque sea inmenso, sino precisamente porque su ambición está contenida.

El mayor riesgo a largo plazo no es técnico sino de dirección: si empieza a acumular funciones sin criterio, perderá su mejor cualidad, que es ser entendible. Si en cambio sigue creciendo por capas pequeñas, con validación y documentación, tiene buena base para durar.

## Documentación breve

- `docs/comandos.md`
- `docs/funcionamiento.md`
- `docs/laboratorio.md`