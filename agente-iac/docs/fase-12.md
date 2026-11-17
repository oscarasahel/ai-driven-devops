# Fase 12 – Higiene del repo público y telemetría del pipeline (2026-11-17)

## Qué se entregó
- **Higiene (el repo es público):** los 14 nombres de temas del curso salen de `bitacora/sesiones.json` (queda solo el id) y viven en `bitacora/temas.local.json`, ignorado por git; `bitacora.py` los combina al generar. Prueba que impide volver a versionarlos.
- **Telemetría:** `scripts/eventos_pipeline.py` convierte el historial de Jenkins en eventos estructurados con `trace_id` y calcula el SLI; `docs/observabilidad.md` define SLI/SLO.
- **Dashboard:** dos paneles nuevos (SLI del pipeline y eventos) y `scripts/verificar_dashboard.py` para comprobar que los 9 paneles devuelven datos.
- README con el estado real tras las fases 9-12.

## Verificación real
- 44 pruebas pasan; 14 evals rápidos coinciden con lo esperado; bitácora válida.
- Gitleaks sobre todo el historial de todas las ramas: sin hallazgos.
- `eventos_pipeline.py` leyó 4 builds reales (#1 failure, #2 success, #3 rejected, #4 success): SLI 75 %, SLO 90 %.
- `verificar_dashboard.py`: 9 de 9 paneles con datos.

## Hallazgo operativo
Al relanzar el emulador, Jenkins quedó "healthy" pero sin responder: comparte la red del contenedor del emulador y esa red desaparece al recrearlo. Se resuelve con `docker compose up -d --force-recreate jenkins`; añadido al runbook del pipeline y al README.

## Límites y puntos para el dueño del repo
- **Historial público:** los títulos de los 14 temas del curso ya estuvieron en commits anteriores de `sesiones.json` (ramas fase-6 a fase-11). Quitarlos del historial exigiría reescribirlo y hacer force-push, que **no** se hizo: decisión del dueño. No contienen contenido de diapositivas, solo títulos de sesión.
- No se recoge la versión (commit) de cada build; no hay latencia por etapa ni trazas distribuidas.
- El aspecto visual del dashboard sigue sin revisarse.
