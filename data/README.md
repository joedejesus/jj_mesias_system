# Datos persistentes de Mesias

## Que debe verse en GitHub

- `dataset_entrenamiento_docente.jsonl`: dataset ampliado para pruebas y entrenamiento LoRA.
- `ejemplo_entrenamiento.jsonl`: dataset pequeño y didáctico para aprender el flujo de entrenamiento antes de usar el dataset ampliado.
- `README.md`: explicación de qué archivos de `data` son públicos y cuáles son solo locales.

## Que no debe subirse a GitHub

- `logs_mesias.json`: historial local de eventos de generación si el logging está activo.
- `memoria_chat.json`: historial conversacional persistente del uso real.
- `mesias_memory.json`: recuerdos simples persistentes, incluidos hechos por hablante.
- `checkpoints/`: salidas locales del entrenamiento LoRA.
- cualquier archivo `*.corrupt.*`: copias de seguridad generadas cuando un JSON local se aísla por corrupción.

La lógica es esta: los archivos que sirven para aprender, probar o documentar el proyecto sí deben vivir en GitHub; los que contienen actividad real del usuario o salidas regenerables del runtime y del entrenamiento se quedan solo en local.

En un clon limpio, Mesias recrea automaticamente los JSON locales vacios cuando arrancan la memoria o el historial de chat por primera vez. Asi el usuario no necesita bajar esos archivos desde GitHub ni crearlos a mano.

Si alguno de los JSON de memoria se corrompe, Mesias intenta aislarlo renombrándolo con sufijo `.corrupt` y recreando un estado vacío para no bloquear el arranque.

El dataset de ejemplo mezcla dos formatos soportados por Mesias:

- filas con `system_prompt`, `prompt` y `response`
- filas con `messages` en formato conversacional

Eso permite aprender la estructura mínima antes de pasar a datasets mayores.