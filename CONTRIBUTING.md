# Contribuciones

## Enfoque del repositorio

Mesias se publica principalmente como proyecto técnico de estudio, portfolio y laboratorio. Eso significa que las aportaciones externas pueden ser útiles como señalamiento, revisión o propuesta, pero no se gestionan como en un proyecto abierto de gobernanza comunitaria amplia.

Para preservar la unicidad, la coherencia técnica y el control integral del proyecto, no se admiten pull requests externos como vía ordinaria de contribución. Los canales habilitados para informar de errores, mejoras o dudas son los issues y las Discussions del repositorio.

La existencia de este documento no convierte el repositorio en software libre ni modifica la licencia aplicable. Antes de proponer cambios, revisa [README.md](README.md), la carpeta [docs](docs), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) y [LICENSE](LICENSE).

## Antes de proponer cambios

Conviene verificar lo siguiente:

- que el cambio encaja con el objetivo del proyecto: claridad técnica, utilidad educativa y arquitectura mantenible
- que no introduce dependencias innecesarias, complejidad gratuita o comportamiento difícil de justificar
- que respeta el flujo de uso documentado y el entorno validado del repositorio
- que no contradice las restricciones de uso, redistribución o explotación indicadas en la licencia

## Formas recomendadas de contribuir

Las vías más útiles suelen ser estas:

- abrir un issue claro y reproducible para reportar un problema
- abrir una Discussion para plantear una mejora técnica, una duda de diseño o una propuesta de evolución
- señalar errores en documentación, pasos ambiguos o supuestos no explicados

No se aceptan pull requests externos como canal normal de cambios. Si una propuesta resulta útil, el titular del repositorio decidirá si la implementa directamente, la adapta o la incorpora por su cuenta.

## Cómo preparar una propuesta útil

Si vas a abrir un issue o una Discussion, intenta incluir:

- objetivo del cambio
- problema actual observado
- entorno utilizado y pasos de reproducción, si aplica
- impacto esperado
- riesgos, límites o decisiones de diseño relevantes

Si tu propuesta implica cambios de código, conviene además indicar:

- mantener el estilo existente del proyecto
- evitar mezclar refactors amplios con arreglos puntuales
- no tocar áreas no relacionadas sin necesidad clara
- actualizar documentación si el flujo de uso cambia
- ejecutar, cuando sea viable, las comprobaciones mínimas documentadas en [README.md](README.md)

## Criterios de aceptación

El titular del repositorio revisará cada propuesta según su ajuste con el propósito del proyecto. Un cambio puede ser rechazado aunque funcione técnicamente si:

- amplía demasiado el alcance
- complica el mantenimiento
- rompe la coherencia de la arquitectura o de la documentación
- introduce riesgos de seguridad, legales o de operación
- desplaza el proyecto fuera de su enfoque educativo y local

## Derechos sobre las contribuciones propuestas

Al enviar una propuesta, declaras que tienes derecho a compartir ese contenido y que tu aportación no infringe derechos de terceros.

Si el titular decide incorporar una idea, sugerencia o propuesta nacida de un issue o una Discussion, podrá adaptarla, modificarla o integrarla dentro del proyecto bajo el marco legal y de licencia vigente en este repositorio.

## Seguridad y divulgación responsable

Si detectas un problema que pueda afectar a la seguridad, a un uso inseguro del sistema o a terceros, no lo publiques primero como issue abierto ni como Discussion pública. Revisa [SECURITY.md](SECURITY.md).