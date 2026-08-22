# Laboratorio de Mesias

Esta guia resume aprendizaje, entrenamiento y portabilidad.

## Regla principal

- Si acabas de clonar el repo desde GitHub, `venv` no vendra incluido y `src/modelo` puede estar vacia salvo archivos de ayuda.
- Primero recrea `venv` y despues descarga tu motor local dentro de [src/modelo](../src/modelo).
- No toques [src/modelo](../src/modelo) si tu motor actual ya funciona.
- Usa siempre el Python de [../venv](../venv).
- Si mueves el proyecto, recrea `venv`.
- Arranca siempre por la via canónica `python -m src ...`.

## Pipeline minimo para aprender

1. Arranca Mesias en consola.
2. Prueba Gradio si quieres una interfaz mas comoda.
3. Lee [src/mesias.py](../src/mesias.py).
4. Mira [src/interfaces/roles.py](../src/interfaces/roles.py) y [src/memory](../src/memory).
5. Deja el entrenamiento para el final.

## Web durante las pruebas

- Si preguntas por fecha, habitantes, capitales, clima u otros datos externos, Mesias intenta buscar apoyo web por ti incluso sin una formula exacta.
- Si quieres control total, puedes seguir pasando URLs manualmente en consola o API.
- Si la red del entorno falla, las pruebas locales del modelo siguen funcionando.

## Memoria del hablante

- Gradio y la consola interactiva pueden recordar datos simples del usuario, por ejemplo nombre o preferencias expresadas de forma directa.
- Esa memoria se guarda en [../data](../data) con un formato JSON compacto y compatible hacia atras.
- Si alguno de esos JSON se rompe, Mesias intenta moverlo a un archivo `.corrupt.*` y rehacer el estado minimo.

## Entrenamiento minimo

- Dataset simple: [../data/ejemplo_entrenamiento.jsonl](../data/ejemplo_entrenamiento.jsonl)
- Dataset mas amplio: [../data/dataset_entrenamiento_docente.jsonl](../data/dataset_entrenamiento_docente.jsonl)
- Runtime y memoria: [../data](../data)
- Estado de cada archivo persistente: [../data/README.md](../data/README.md)
- Preparacion: [../src/training/preparacion_datos.py](../src/training/preparacion_datos.py)
- Entrenamiento: [../src/training/entrenamiento.py](../src/training/entrenamiento.py)
- Lanzador: `./venv/Scripts/python.exe ./tools/train_lora_seguro.py --prepare-only`

Para aprender desde cero, empieza por [../data/ejemplo_entrenamiento.jsonl](../data/ejemplo_entrenamiento.jsonl): es pequeño, legible y mezcla ejemplos simples de `prompt/response` con ejemplos conversacionales en `messages`.

Comando literal para probar solo ese dataset:

`./venv/Scripts/python.exe ./tools/train_lora_seguro.py --dataset ./data/ejemplo_entrenamiento.jsonl --prepare-only`

Antes de tocar entrenamiento, valida el proyecto con `./venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py"`.

Valores prudentes:

- `epochs=1.0`
- `train_batch_size=1`
- `gradient_accumulation_steps=8`
- `dataloader_num_workers=0`
- `cpu_threads=4`

## Compatibilidad basica

Si tu motor actual en [src/modelo](../src/modelo) ya responde bien, no necesitas cambiar nada. Si algun dia pruebas otro, revisa solo esto:

- Debe cargar con `AutoModelForCausalLM`.
- Debe tener tokenizer local.
- Debe tener `config.json`.
- Debe exponer pesos compatibles para `transformers`, al menos `model.safetensors.index.json`, `model.safetensors` o `pytorch_model.bin`.
- Si es un motor conversacional, su tokenizer deberia tener chat template o un formato equivalente usable por Mesias.

Antes de adoptar un motor nuevo o propio de Hugging Face:

- Exporta todos los artefactos a una carpeta local.
- Prueba `python -m src console --doctor`.
- Prueba una generación corta en consola.
- Si vas a entrenar LoRA encima, valida después `./venv/Scripts/python.exe ./tools/train_lora_seguro.py --prepare-only`.

## Portabilidad

- Puedes mover la carpeta del proyecto.
- No debes reutilizar el `venv` viejo despues del traslado.
- Ejecuta `scripts\setup.cmd` o `./scripts/setup.ps1` en la nueva ruta.

## Que tocar y que no tocar

- Toca sin miedo: [../src/interfaces/roles.py](../src/interfaces/roles.py), [../src/memory](../src/memory), [../src/security/seguridad.py](../src/security/seguridad.py)
- Toca con mas cuidado: [../src/training](../src/training)
- No toques salvo que sepas por que: [../src/modelo](../src/modelo)

## Carpetas auxiliares

- [../notebooks](../notebooks): cuadernos para experimentar sin tocar el runtime.
- [../tools](../tools): scripts auxiliares que no forman parte del uso diario.