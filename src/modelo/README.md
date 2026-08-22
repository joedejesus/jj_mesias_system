# Carpeta del modelo local

Esta carpeta se publica vacia en GitHub salvo este archivo y `__init__.py`.

Para usar Mesias, descarga el motor validado en:

- `https://huggingface.co/Qwen/Qwen2.5-3B-Instruct`

Despues copia aqui los artefactos del modelo, por ejemplo:

- `config.json`
- `generation_config.json`
- `tokenizer_config.json` o `tokenizer.json`
- `model.safetensors.index.json` o `model.safetensors` o `pytorch_model.bin`
- los ficheros de pesos asociados si el modelo viene fragmentado

La ruta esperada por defecto es `src/modelo`.
