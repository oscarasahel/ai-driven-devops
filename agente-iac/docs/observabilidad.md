# Observabilidad del pipeline

## Pregunta operativa
¿Qué proporción de las ejecuciones del pipeline `agente-iac` termina como se espera, y qué pasó en las que no?

## Evento estructurado (uno por build)
Generado por `scripts/eventos_pipeline.py` a partir de la API de Jenkins:

| Campo | Significado |
|---|---|
| `trace_id` | `agente-iac-pipeline-<n>`: une el evento con el build, su log (`docs/evidencia/`) y la bitácora |
| `service` | `agente-iac-pipeline` |
| `operation` | `apply` o `destroy` |
| `outcome` | `success`, `rejected` (rechazo humano), `failure`, `running` |
| `duration_ms` | Duración total del build (incluye la espera de la aprobación humana) |
| `started_at` | Inicio en UTC |
| `build_url` | Enlace al build |

## SLI y SLO
- **SLI:** `(success + rejected) / (success + rejected + failure)`. Un rechazo humano cuenta como bueno porque es el control funcionando; solo `failure` es malo. Los builds en curso no cuentan.
- **Exclusión:** las pruebas negativas deliberadas no cuentan (se informa también el SLI bruto).
- **SLO:** 90 % de builds buenos. (Objetivo interno de la PoC, no un compromiso.)
- **Presupuesto de error:** con 10 builds, 1 `failure` agota el presupuesto.

## Estado real (2026-11-17)
Ventana de los últimos 20 builds que conserva Jenkins (`numToKeepStr: 20`; #1 y #5 ya salieron de ella): **SLI bruto 85 %**; **SLI ajustado 100 %**, que cumple el SLO de 90 %. Medido antes con 21 eventos (incluidos #1 y #5): bruto 75 %, ajustado 93,8 %. El ajustado excluye los builds de prueba negativa deliberada (#6 recurso inseguro; #12, #15 y #17 promoción bloqueada), listados con su motivo en `policies/builds-prueba-negativa.json`: ahí el `failure` es el control funcionando. Solo se excluye un build que terminó en `failure` y está en esa lista; los defectos reales (#1 ruta en el Jenkinsfile, #5 CRLF) siguen contando. Con tan pocos builds el valor es muy sensible: es un instrumento, no una conclusión.

## Dónde se ve
Dashboard "Avance por sesión" en Grafana: paneles *SLI del pipeline* y *Eventos del pipeline*. Datos: `bitacora/pipeline-eventos.json` (local, ignorado por git). Para actualizarlos: `python scripts/eventos_pipeline.py`.

## Alertas (diseño, no implementado)
Alertar cuando el SLI de los últimos 10 builds baje del SLO, con el propietario del pipeline y la consulta siguiente: filtrar `outcome = failure` y abrir el log del `trace_id`.

## Qué no cubre
- No hay métricas de latencia por etapa ni trazas distribuidas (OpenTelemetry): un solo evento por build.
- No se registra la versión (commit) con la que corrió cada build; habría que pasarla como parámetro.
- El emulador y Jenkins no exportan métricas a Prometheus.
