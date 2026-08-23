# Carpeta del modelo local

Esta carpeta se publica vacía en GitHub salvo este archivo y `__init__.py`.

Mesias no descarga automáticamente el modelo porque el proyecto está planteado para un uso local, controlado y explícito del entorno.

Para usar Mesias, descarga el motor validado en:

- `https://huggingface.co/Qwen/Qwen2.5-3B-Instruct`

Después copia aquí los artefactos del modelo, por ejemplo:

- `config.json`
- `generation_config.json`
- `tokenizer_config.json` o `tokenizer.json`
- `model.safetensors.index.json` o `model.safetensors` o `pytorch_model.bin`
- los ficheros de pesos asociados si el modelo viene fragmentado

La ruta esperada por defecto es `src/modelo`.

Si trabajas fuera del entorno validado del proyecto o cambias el motor recomendado, puede hacer falta algún ajuste menor. Antes de seguir, revisa [../../README.md](../../README.md), [../../docs/comandos.md](../../docs/comandos.md) y [../../docs/funcionamiento.md](../../docs/funcionamiento.md).
