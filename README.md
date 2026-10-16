# Monitor jurídico Colombia

Extractores conservadores y de solo lectura para preparar un monitor jurídico. Se integra con el Site privado y su Skill **El juez cabrón | Colombia**. El repositorio público solo contiene código de consulta y programación; no almacena credenciales ni documentos privados.

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
- El Site tiene D1 y MCP. El flujo de GitHub Actions requiere los secretos y una ejecución manual comprobada; el YAML por sí solo no acredita una programación operativa.
- Nunca se almacena material confidencial de expedientes del usuario.

## Historial y cambios

Los extractores versionan el formato JSON; los datos históricos se guardarán de forma append-only en una etapa posterior. Ninguna actualización del monitor cambiará automáticamente la Skill ni declarará cambio de precedente sin análisis jurídico humano.

## Programador del Site privado (pendiente de validación operativa)

`.github/workflows/site-monitor.yml` define `workflow_dispatch` y `0 12 * * *` UTC (07:00 de Bogotá). Invoca `scripts/trigger_site_monitor.py`, que llama la ruta `/api/internal/monitor/run` del Site privado por HTTPS. El despacho de Sites exige `SITE_ACCESS_TOKEN` y la ruta exige una firma HMAC-SHA256 con `MONITOR_JOB_SECRET`, fecha de cinco minutos y un identificador de ejecución único. D1 registra los intentos autenticados y bloquea duplicados. El monitor existente conserva su bloqueo de simultaneidad. Ninguno de estos secretos debe entrar al repositorio ni a los logs.

Configurar **en GitHub → Settings → Secrets and variables → Actions** los secretos `SITE_ACCESS_TOKEN` (acceso de servicio proporcionado por Sites) y `MONITOR_JOB_SECRET` (secreto aleatorio de al menos 32 bytes). Configurar el mismo `MONITOR_JOB_SECRET` como secreto de producción del Site y volver a desplegar la versión guardada para aplicar la revisión del entorno. Mantener el Site privado. No publicar los valores.

Después, ejecutar manualmente el flujo desde Actions. Comprobar en D1 `monitor_dispatches`, `monitor_runs`, `source_checks` y `monitor_schedule`, y en MCP `estado_monitor`. El primer despacho manual solo deja `pending_first_scheduled_run`; `active` se registra únicamente tras un evento `schedule` auténtico y una ejecución almacenada. Los eventos de GitHub pueden retrasarse, especialmente al inicio de la hora. Un despliegue o un workflow presente en el repositorio no sustituyen la prueba de ejecución.
