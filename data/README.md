# Datos persistentes de Mesias

Esta carpeta acompaña un flujo de trabajo local y educativo. En un uso normal, parte de estos archivos sirven como material de aprendizaje y otra parte solo tiene sentido en la máquina de quien ejecuta el proyecto.

## Qué debe verse en GitHub

- `dataset_entrenamiento_docente.jsonl`: dataset ampliado para pruebas y entrenamiento LoRA.
- `ejemplo_entrenamiento.jsonl`: dataset pequeño y didáctico para aprender el flujo de entrenamiento antes de usar el dataset ampliado.
- `README.md`: explicación de qué archivos de `data` son públicos y cuáles son solo locales.

## Qué no debe subirse a GitHub

- `logs_mesias.json`: historial local de eventos de generación si el logging está activo.
- `memoria_chat.json`: historial conversacional persistente del uso real.
- `mesias_memory.json`: recuerdos simples persistentes, incluidos hechos por hablante.
- `checkpoints/`: salidas locales del entrenamiento LoRA.
- cualquier archivo `*.corrupt.*`: copias de seguridad generadas cuando un JSON local se aísla por corrupción.

La lógica es esta: los archivos que sirven para aprender, probar o documentar el proyecto sí deben vivir en GitHub; los que contienen actividad real del usuario o salidas regenerables del runtime y del entrenamiento se quedan solo en local.

Si quieres poner Mesias en marcha, sigue primero las indicaciones de [../README.md](../README.md) y la sección [../docs](../docs), especialmente [../docs/comandos.md](../docs/comandos.md) y [../docs/laboratorio.md](../docs/laboratorio.md).

En un clon limpio, Mesias recrea automáticamente los JSON locales vacíos cuando arrancan la memoria o el historial de chat por primera vez. Así el usuario no necesita bajar esos archivos desde GitHub ni crearlos a mano.

Si alguno de los JSON de memoria se corrompe, Mesias intenta aislarlo renombrándolo con sufijo `.corrupt` y recreando un estado vacío para no bloquear el arranque.

El dataset de ejemplo mezcla dos formatos soportados por Mesias:

- filas con `system_prompt`, `prompt` y `response`
- filas con `messages` en formato conversacional

Eso permite aprender la estructura mínima antes de pasar a datasets mayores.

Si durante pruebas o entrenamiento aparece algún ajuste pequeño de datos o entorno, no es necesariamente una anomalía del proyecto: Mesias también está pensado para que el estudiante vea y corrija esos detalles en un contexto controlado.