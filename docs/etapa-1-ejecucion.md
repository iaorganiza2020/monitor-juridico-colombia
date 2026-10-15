# Etapa 1 — resultados de inspección y pruebas

Fecha de verificación: 15 de octubre de 2026 (UTC/COT).

## Acceso a GitHub

El conector GitHub aparece disponible en el directorio, pero `installed=false`; en esta conversación tampoco se expusieron operaciones de repositorio. Por tanto, no hay autorización/conexión efectiva para consultar o crear repositorios. No se creó ningún repositorio.

## Fuentes oficiales revisadas

- **Sala de Casación Penal:** la página oficial de boletines presenta un índice cronológico con títulos, fechas de publicación y enlaces a boletines, incluidos los de 2026. Un boletín es una fuente de referencias y extractos, no prueba de que se recuperó el texto íntegro de cada sentencia.
- **Corte Constitucional:** la Relatoría ofrece búsqueda por texto, tema/subtema, número de providencia y norma demandada. El acceso es una interfaz web; no se identificó documentación oficial de API pública en la revisión realizada.
- **SUIN-Juriscol:** el Ministerio describe el sistema como catálogo de normas generales y abstractas, concordancias/afectaciones normativas y jurisprudencia. No se identificó una API pública documentada para extracción.
- **Diario Oficial:** la Imprenta Nacional describe consultas por número de Diario, tipo o número de norma, entidad y fecha. Su consulta usa una interfaz web; no se identificó documentación oficial de API pública.

No fue posible verificar `robots.txt`, condiciones de rastreo ni endpoints internos desde este runtime. No se implementó acceso a endpoints privados/no documentados ni automatización de formularios que pueda eludir controles. La exploración del sitio con el buscador web confirma disponibilidad de páginas, pero no concede autorización de rastreo.

## Pruebas

| Comprobación | Resultado |
| --- | --- |
| Pruebas unitarias de parser/metadatos | 4/4 aprobadas con `unittest` |
| Prueba HTTP desde el runtime para Corte Suprema, Corte Constitucional, SUIN y Diario Oficial | 4/4 expiraron con `URLError: timed out` (timeout de 3 segundos por fuente) |
| Registros emitidos por esa ejecución | 0; resultado parcial y errores guardados, sin fabricar registros |
| Validación de texto íntegro | Los boletines quedan clasificados como referencia; no se reporta texto íntegro disponible |
| Validación de vigencia normativa | No se emite estado de vigencia a partir de una mención en un catálogo |

La falla HTTP parece propia del entorno de ejecución, ya que las páginas oficiales se pudieron revisar mediante el buscador web. No demuestra indisponibilidad pública de los portales ni disponibilidad de los mismos desde GitHub Actions. La conectividad debe probarse en el entorno de despliegue antes de considerar operativo cualquier extractor.

## Criterio para cerrar la etapa

La estructura del proyecto y cuatro pruebas locales funcionan. La etapa 1 **todavía no queda validada de extremo a extremo**: falta una conexión GitHub instalada/autorizada, autorización explícita para crear el repositorio privado y una ejecución de los extractores con acceso HTTP real desde un entorno autorizado. La etapa no se considera lista para pasar a Supabase.
