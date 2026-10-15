# Monitor jurídico Colombia — etapa 1

Extractores conservadores y de solo lectura para preparar un monitor jurídico. Se integra después con la Skill privada **El juez cabrón | Colombia** (v1.1.0); este proyecto no la reemplaza ni modifica sus instrucciones.

## Alcance actual

- Corte Suprema, Sala de Casación Penal: indexa referencias de boletines oficiales; estas no se confunden con el texto íntegro de las providencias reseñadas.
- Corte Constitucional: reconoce enlaces oficiales individuales a providencias cuando están presentes en el HTML consultado. La Relatoría ofrece un buscador público con filtros por fechas, número, texto y temas.
- Normativa penal: reconoce referencias a normas solo si provienen de enlaces oficiales SUIN o Diario Oficial. Una referencia no es una conclusión de vigencia ni de materia penal; ambas requieren revisión del texto y afectaciones.
- Emite JSON con fuente, URL original, campos de fecha/identificación disponibles y estado/nota de verificación. No crea filas ficticias para fuentes sin acceso.

## Fuentes y viabilidad observada

| Fuente | Mecanismo oficial observado | Estado técnico para automatización |
| --- | --- | --- |
| Corte Suprema, boletines penales | Índice HTML cronológico con enlaces de boletines PDF y fechas de publicación | Parser HTML inicial. Un boletín es referencia secundaria; cada providencia requiere su fuente original. No se identificó API pública documentada. |
| Corte Constitucional, Relatoría | Buscador público; permite buscar en texto completo, temas, número y normas demandadas | Adapter inicial para enlaces directos del índice; el buscador puede renderizar o consultar dinámicamente. No se identificó una API pública documentada. |
| SUIN-Juriscol | Catálogo de normas generales/abstractas y afectaciones normativas/jurisprudenciales | Portal oficial consultable; no se identificó API pública documentada en la información consultada. El extractor solo acepta enlaces explícitos de norma. |
| Diario Oficial, Imprenta Nacional | Búsqueda por número de Diario, tipo/número de norma, entidad o fecha; el portal de consulta tiene interfaz web | Consulta automatizada no validada; requiere verificar formularios, términos, robots y estabilidad antes de ponerla en producción. |

La disponibilidad pública de una página no demuestra por sí sola permiso para rastreo automatizado. No se pudo verificar aquí el contenido de `robots.txt`, las condiciones técnicas de uso ni un contrato/API de extracción. El cliente tiene tasa baja (una solicitud por fuente por ejecución), timeout y User-Agent identificable; antes de activarlo en GitHub Actions deben validarse esos controles desde el entorno de ejecución.

## Ejecución

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m monitor_juridico.cli --output reports/run.json
```

El comando termina con código 2 si falla alguna fuente y conserva la falla en el JSON; no presenta un resultado parcial como consulta completa.

## Pruebas

```bash
PYTHONPATH=src python -m unittest discover -s tests -p '*unittest.py' -v
```

Las pruebas unitarias comprueban el tratamiento de metadatos/estados; no simulan una descarga real ni prueban la conectividad externa. La comprobación web realizada para esta versión confirmó que la página oficial de boletines de Sala Penal listaba el boletín de septiembre de 2026 publicado el 8 de octubre de 2026; la ficha se usa únicamente como ejemplo de metadato de boletín, nunca como providencia verificada.

## Limitaciones y siguientes pasos (aún no implementados)

- El runtime de trabajo no pudo establecer conexiones HTTP directas a los portales; las consultas web oficiales sí devolvieron páginas y resultados. La prueba `--probe` en un runner autorizado es necesaria antes de declarar operativos los extractores en red.
- Falta confirmar la forma técnica/condiciones de consulta de buscadores dinámicos y documentos originales; si no hay endpoint estable y permitido, usar descarga manual o fuentes oficiales con API/feeds habilitados.
- Aún no hay base persistente, Supabase, servidor MCP, programación diaria, credenciales ni automatización GitHub.
- Nunca se almacena material confidencial de expedientes del usuario.

## Historial y cambios

Los extractores versionan el formato JSON; los datos históricos se guardarán de forma append-only en una etapa posterior. Ninguna actualización del monitor cambiará automáticamente la Skill ni declarará cambio de precedente sin análisis jurídico humano.
