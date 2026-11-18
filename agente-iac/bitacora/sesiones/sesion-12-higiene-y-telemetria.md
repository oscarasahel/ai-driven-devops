# Sesión 12 – Higiene del repo público y telemetría del pipeline

- **Fecha:** 2026-11-17
- **Fase:** Fase 12
- **Rama:** feature/fase-12-higiene-y-telemetria
- **Temas del curso aplicados:** S11, S12, S15

## Objetivo
Mantener el material confidencial fuera del repo público y medir el pipeline con eventos estructurados y un SLI.

## Qué se agregó
- `agente-iac/scripts/eventos_pipeline.py`
- `agente-iac/scripts/verificar_dashboard.py`
- `agente-iac/docs/observabilidad.md`
- `agente-iac/scripts/bitacora.py`
- `agente-iac/grafana/dashboards/avance-por-sesion.json`

## Decisiones
- **Guardar en el repo solo ids de temas; nombres en un archivo local** — el repo es público y los nombres derivan de material confidencial
- **Un rechazo humano cuenta como build bueno en el SLI** — es el control funcionando, no una falla
- **No reescribir el historial público sin autorización** — force-push es destructivo; lo decide el dueño del repo

## Evidencia
- [commit] `8ee5c56` — higiene, eventos y dashboard
- [archivo] `agente-iac/docs/fase-12.md` — 44 pruebas, 9 de 9 paneles, Gitleaks sin hallazgos

## Cómo se validó
44 pruebas unitarias, eventos estructurados del pipeline y SLI calculado (75 % frente a un SLO de 90 %); 9 paneles con datos.

## Qué acertó y qué falló la IA
- **Acertó:** Separó los nombres de los temas del curso a un archivo local y midió el pipeline con eventos y un SLI.
- **Falló:** Los títulos de los temas siguen en el historial de ramas anteriores del repo público; el SLI es muy sensible con 4 builds.

## Lección aprendida
Un repo público exige decidir qué no se publica antes de escribirlo, no después.

## Métricas
- recursos_terraform: 15
- pruebas_unitarias: 44
- paneles: 9
- paneles_con_datos: 9
- sli_pipeline_pct: 75.0
- slo_pipeline_pct: 90.0

## Riesgos y pendientes
- Los títulos de los temas siguen en el historial de ramas anteriores (público)
- SLI muy sensible con 4 builds
- Aspecto visual del dashboard sin revisar

## Siguiente paso
Revisión humana por la mañana y decisión sobre el historial y la fusión de ramas.
