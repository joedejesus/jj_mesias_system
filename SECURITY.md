# Seguridad

## Alcance

Mesias es un proyecto local de inteligencia artificial orientado a estudio, revisión técnica y experimentación no comercial. Aun así, cualquier sistema de este tipo puede implicar riesgos si se configura mal, se integra sin control o se utiliza fuera de su contexto previsto.

Este documento explica cómo reportar problemas de seguridad o usos inseguros detectados en el repositorio.

## Qué debe reportarse

Conviene reportar, entre otros, problemas como:

- ejecución inesperada o insegura de acciones no previstas
- exposición de datos, rutas, memoria o información sensible
- validaciones insuficientes en interfaces, API o flujos de entrada
- usos web inseguros o bypass de restricciones previstas
- comportamientos que puedan aumentar el riesgo para terceros o facilitar un uso irresponsable del sistema

## Qué no debe publicarse en abierto de entrada

Si el hallazgo puede facilitar abuso, exponer datos o empeorar el riesgo antes de corregirse, no publiques primero todos los detalles en un issue abierto.

En esos casos, prioriza una divulgación responsable y limitada al titular del repositorio o al canal privado que GitHub pueda ofrecer para reportes de seguridad.

## Cómo reportarlo

Si GitHub ofrece informes privados de seguridad para este repositorio, usa ese canal.

Si no está disponible, contacta con el titular del repositorio por una vía privada asociada a su perfil público antes de abrir un issue con detalles técnicos completos.

Para incidencias no sensibles, dudas de endurecimiento o propuestas generales de mejora, sí puede abrirse un issue normal o una Discussion con contexto suficiente y sin publicar material que aumente el riesgo.

## Qué incluir en el reporte

Un reporte útil debería incluir, en la medida de lo posible:

- descripción clara del problema
- componente afectado
- pasos de reproducción
- impacto potencial
- condiciones necesarias para que ocurra
- propuesta de mitigación o contención, si existe

## Expectativas y límites

Este repositorio no ofrece compromisos formales de SLA, soporte continuo ni plazos garantizados de respuesta. Aun así, los reportes razonables y bien documentados se revisarán con prioridad proporcional al riesgo y al alcance del problema.

## Relación con la licencia y el descargo de responsabilidad

La existencia de esta política de seguridad no implica garantía de ausencia de fallos ni aptitud para entornos sensibles. Consulta [LICENSE](LICENSE) para las limitaciones legales, restricciones de uso y descargo de responsabilidad aplicables al proyecto. Para las reglas generales de participación, revisa también [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) y [CONTRIBUTING.md](CONTRIBUTING.md).