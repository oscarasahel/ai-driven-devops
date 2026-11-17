# Fase 17 – Trazas OpenTelemetry (S11, versión mínima) (2026-11-17)

## Qué es
`scripts/otel_exportar.py` convierte `bitacora/pipeline-eventos.json` (un evento por build de Jenkins) a trazas **OTLP/JSON** (`bitacora/trazas-otlp.json`, local e ignorado por git). Cada build es una traza de un solo span.

| Campo OTLP | Origen |
|---|---|
| `traceId` (32 hex) | `trace_id` si ya es hex; si no (p. ej. `agente-iac-pipeline-9`), SHA-256 truncado |
| `spanId` (16 hex) | SHA-256 de `trace_id` + operación (determinista) |
| `start/endTimeUnixNano` | `started_at` (UTC) y `duration_ms` |
| `status` | ERROR solo si `outcome = failure`; `success`, `rejected` y `running` = OK |
| atributos | `service.name`, `ci.build_url`, `pipeline.outcome` |

## Cómo usarlo
```bash
python scripts/eventos_pipeline.py     # refresca los eventos desde Jenkins
python scripts/otel_exportar.py        # escribe bitacora/trazas-otlp.json
python scripts/otel_exportar.py --enviar http://localhost:4318/v1/traces   # opcional, si tienes un colector
```
Valida longitudes de `traceId`/`spanId` y que el fin no preceda al inicio antes de escribir. Los textos de los eventos se copian como atributos y nunca se interpretan (son datos).

## Verificación
- `tests/test_otel_exportar.py`: 9 pruebas; mutaciones comprobadas (estado de error y longitud del `spanId` rompen pruebas).
- Ejecución real: 21 trazas generadas desde los eventos actuales.

## Límites
- **No hay colector ni Jaeger/Tempo en el compose**: el archivo no se visualiza en ninguna herramienta del proyecto; `--enviar` solo sirve si el usuario levanta un colector OTLP/HTTP por su cuenta (no probado).
- **Sin latencia por etapa**: los eventos son por build, así que cada traza tiene un único span; no hay spans por etapa (validar, plan, aprobación, apply).
- Los `rejected` y los `ABORTED` por limpieza cuentan como OK, igual que en el SLI; no distingue pruebas negativas deliberadas.
- Es la forma de los datos, no instrumentación real del pipeline: esa exigiría un plugin de OpenTelemetry en Jenkins y un colector.

## SLI ajustado
`policies/builds-prueba-negativa.json` lista los builds de prueba negativa deliberada (#6, #12, #15, #17) con su motivo. `eventos_pipeline.py` los marca (`prueba_negativa`) y `sli_pct` los excluye; `sli_bruto_pct` y `excluidos` quedan como campos nuevos. Solo se excluye un build en `failure` que esté en la lista: los defectos reales (#1, #5) siguen contando. Resultado: **bruto 75 %, ajustado 93,8 %** (SLO 90 %). `tests/test_sli_pruebas_negativas.py` (6 pruebas, con mutación).

## Arreglo de `jenkins.sh disparar`
- **Causa:** el curl de Windows sale con código distinto de 0 aunque Jenkins responda 201 y encole el build; el script lo tomaba por fallo y lanzaba el respaldo `/build`, que da el 400 y a veces duplica el build (#8 a #10, #21).
- **Arreglo:** una sola petición; decide por el código HTTP y solo cae a `/build` ante 400/404 (job sin parámetros todavía). Espera hasta 90 s a que aparezca el build.
- **Evidencia:** dos lanzamientos reales crearon exactamente 1 build cada uno (#25 y #26). Prueba de higiene que impide volver al respaldo ciego.
