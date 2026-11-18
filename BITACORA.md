# Bitácora de sesiones (reales)

## Empieza aquí

agente-iac es una prueba de concepto local: un requerimiento en texto pasa a una spec verificable, luego a Terraform, por un gate de seguridad y por una aprobación humana, y se aplica en un emulador de AWS. Esta bitácora registra cada sesión de trabajo con su evidencia.

| Qué buscas | Dónde está |
|---|---|
| Visión general y diagramas | [README del proyecto](agente-iac/README.md) |
| Resumen para revisores | [Cierre del proyecto](agente-iac/docs/cierre-proyecto.md) |
| Guía para presentarlo | [Guía de presentación](agente-iac/docs/guia-presentacion.md) |
| Requisitos y criterios de aceptación | [Specs](agente-iac/specs/) |
| Detalle de cada fase | [Documentos de fase](agente-iac/docs/) (`fase-N.md`) |
| Builds reales de Jenkins | [Evidencia](agente-iac/docs/evidencia/) |
| Seguridad | [AI-BOM](agente-iac/docs/seguridad/ai-bom.md) y [modelo de amenazas](agente-iac/docs/seguridad/modelo-de-amenazas.md) |
| Operación | [Runbooks](agente-iac/docs/runbooks/) |

Cada sesión de la tabla enlaza a su ficha: objetivo, decisiones, evidencia, cómo se validó, qué acertó y qué falló la IA, y la lección aprendida.

## Sesiones

Solo sesiones con evidencia verificable (commit y archivos existentes). Las sesiones simuladas del curso viven en un archivo local y se distinguen en Grafana.

| # | Fecha | Fase | Tema | Rama | Commit |
|---|---|---|---|---|---|
| 0 | 2026-11-16 | Fase 0 | [Fundación](agente-iac/bitacora/sesiones/sesion-00-fundacion.md) | feature/fase-0-fundacion | d8a5efa |
| 1 | 2026-11-16 | Fase 1 | [Infra base](agente-iac/bitacora/sesiones/sesion-01-infra-base.md) | feature/fase-1-infra-base | e7941dc |
| 2 | 2026-11-16 | Fase 2 | [Skill analizar-requerimiento](agente-iac/bitacora/sesiones/sesion-02-analizar-requerimiento.md) | feature/fase-2-analizar-requerimiento | 7ee8a33 |
| 3 | 2026-11-16 | Fase 3 | [Skill construir-iac](agente-iac/bitacora/sesiones/sesion-03-construir-iac.md) | feature/fase-3-construir-iac | 4a97c80 |
| 4 | 2026-11-16 | Fase 4 | [Skill seguridad-iac](agente-iac/bitacora/sesiones/sesion-04-seguridad-iac.md) | feature/fase-4-seguridad-iac | 760d03a |
| 5 | 2026-11-16 | Fase 5 | [Jenkins con aprobación manual](agente-iac/bitacora/sesiones/sesion-05-jenkins.md) | feature/fase-5-jenkins | 0b69f84 |
| 6 | 2026-11-16 | Fase 6 | [Skill bitacora](agente-iac/bitacora/sesiones/sesion-06-bitacora.md) | feature/fase-6-bitacora | 716d1e0 |
| 7 | 2026-11-16 | Fase 7 | [Grafana y dashboard por sesión](agente-iac/bitacora/sesiones/sesion-07-grafana.md) | feature/fase-7-grafana | 56425d6 |
| 8 | 2026-11-16 | Fase 8 | [Endurecimiento y evals](agente-iac/bitacora/sesiones/sesion-08-endurecimiento.md) | feature/fase-8-endurecimiento | 4067d49 |
| 9 | 2026-11-17 | Fase 9 | [Pruebas unitarias y CI en GitHub Actions](agente-iac/bitacora/sesiones/sesion-09-ci-y-pruebas.md) | feature/fase-9-ci-y-pruebas | c93a23c |
| 10 | 2026-11-17 | Fase 10 | [Jenkins verificado de extremo a extremo](agente-iac/bitacora/sesiones/sesion-10-jenkins-verificado.md) | feature/fase-10-jenkins-verificado | 570716e |
| 11 | 2026-11-17 | Fase 11 | [Runbooks, ChatOps, AI-BOM y modelo de amenazas](agente-iac/bitacora/sesiones/sesion-11-runbooks-amenazas.md) | feature/fase-11-runbooks-chatops-amenazas | af43bc9 |
| 12 | 2026-11-17 | Fase 12 | [Higiene del repo público y telemetría del pipeline](agente-iac/bitacora/sesiones/sesion-12-higiene-y-telemetria.md) | feature/fase-12-higiene-y-telemetria | 8ee5c56 |
| 13 | 2026-11-17 | Fase 13 | [ChatOps de solo lectura, sugerencias de corrección en CI y evals con modelo](agente-iac/bitacora/sesiones/sesion-13-chatops-sugerencias-evals-modelo.md) | feature/fase-13-chatops-sugerencias-evals-modelo | ef8aa45 |
| 14 | 2026-11-17 | Fase 15 | [El gate rechaza un recurso inseguro dentro de Jenkins](agente-iac/bitacora/sesiones/sesion-14-jenkins-rechaza-inseguro.md) | feature/fase-15-jenkins-rechaza-inseguro | a4eb82f |
| 15 | 2026-11-17 | Fase 16 | [Staging con workspaces y promoción controlada](agente-iac/bitacora/sesiones/sesion-15-staging-promocion.md) | feature/fase-16-staging-promocion | c2d9ad6 |
| 16 | 2026-11-17 | Fase 17 | [SLI sin pruebas negativas, trazas OpenTelemetry y cliente de Jenkins](agente-iac/bitacora/sesiones/sesion-16-sli-otel-cliente-jenkins.md) | feature/fase-17-sli-otel-cliente-jenkins | e21726f, a0c7e01, 2e79b16 |
| 17 | 2026-11-17 | Fase 19 | [Spec 004: bucket de secretos reutilizando secure-bucket](agente-iac/bitacora/sesiones/sesion-17-bucket-secretos.md) | feature/spec-004-bucket-secretos | 2a3e317, 968a620, 0dba369 |
| 18 | 2026-11-17 | Fase 20 | [Jenkins desde Git y lanzamientos automáticos tras el merge](agente-iac/bitacora/sesiones/sesion-18-jenkins-desde-git.md) | feature/fase-20-jenkins-desde-git | 03cdcca, 3d3663f, 8b1eabe, e15a697, 68b2e1e |
