# Fase 7 – Grafana y dashboard por sesión (2026-11-16)

## Qué se entregó
- `docker-compose.yml`: `bitacora-web` (nginx 1.27.3, solo sirve `bitacora.json` y `resumen.json` por la red interna) y `grafana` (grafana-oss 11.4.0, plugin Infinity 3.7.1, `127.0.0.1:3000`, límite 512 MB, sin acceso anónimo, analítica apagada).
- Provisioning como código: datasource `Bitacora` (Infinity) y proveedor de dashboards.
- Dashboard `Avance por sesión` (`grafana/dashboards/avance-por-sesion.json`, generado por `scripts/generar_dashboard.py`) con 7 paneles: línea de tiempo, temas aplicados vs pendientes (dona + detalle), recursos Terraform por sesión, hallazgos antes/después, estado del último pipeline y tabla de la bitácora con marca REAL/SIMULADO.
- `scripts/bitacora.py generar` ahora produce `bitacora/resumen.json` con los agregados (ignorado por git).

## Verificación real
- `docker compose up -d --wait grafana bitacora-web`: ambos sanos.
- API de Grafana: dashboard presente en la carpeta `agente-iac` y datasource aprovisionado.
- `/api/ds/query` sobre los 7 paneles: todos devuelven datos y sin error (21 filas de sesiones: 7 reales + 14 simuladas; 14 temas; 2 severidades; pipeline "no verificado").

## Límites
- **No se revisó el aspecto visual** (sin navegador disponible): solo que las consultas devuelven los datos esperados. Abrir `http://127.0.0.1:3000` (usuario/clave de `.env`) para revisarlo.
- El panel "Estado del último pipeline" lee `pipeline.estado` de `sesiones.json`; no está conectado a métricas vivas de Jenkins (Prometheus no se incluyó; era opcional).
- Los JSON de la bitácora son locales/confidenciales (ignorados por git); en un clon nuevo hay que correr `python scripts/bitacora.py generar`.
