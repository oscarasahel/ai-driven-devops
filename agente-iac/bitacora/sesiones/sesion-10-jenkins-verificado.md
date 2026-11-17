# Sesión 10 – Jenkins verificado de extremo a extremo

- **Fecha:** 2026-11-17
- **Fase:** Fase 10
- **Rama:** feature/fase-10-jenkins-verificado
- **Temas del curso aplicados:** S5, S6, S14

## Objetivo
Demostrar con ejecuciones reales que el pipeline no aplica sin aprobación manual y que un rechazo no cambia nada.

## Qué se agregó
- `agente-iac/jenkins/Jenkinsfile`
- `agente-iac/scripts/jenkins.sh`
- `agente-iac/docs/fase-10.md`
- `agente-iac/docs/evidencia/jenkins-build-2.log`
- `agente-iac/docs/evidencia/jenkins-build-3.log`
- `agente-iac/docs/evidencia/jenkins-build-4.log`

## Decisiones
- **Probar el rechazo además de la aprobación** — un control de aprobación solo es creíble si se demuestra que rechazar no cambia nada
- **Guardar los logs de los builds como evidencia, revisados con Gitleaks** — la bitácora exige evidencia verificable y el repo es público

## Evidencia
- [commit] `570716e` — correcciones y evidencia de Jenkins
- [archivo] `agente-iac/docs/evidencia/jenkins-build-2.log` — apply: gate, plan, aprobación de admin, 15 recursos, pruebas de humo OK
- [archivo] `agente-iac/docs/evidencia/jenkins-build-3.log` — destroy rechazado: ABORTED, sin cambios
- [archivo] `agente-iac/docs/evidencia/jenkins-build-4.log` — destroy aprobado

## Métricas
- recursos_terraform: 15
- builds_ok: 2
- builds_rechazados: 1
- builds_con_defecto: 1
- pipeline_verificado: True

## Riesgos y pendientes
- Un solo usuario (admin): no hay separación entre solicitante y aprobador
- El build #1 falló por un defecto mío (ruta de rsync), corregido

## Siguiente paso
Fase 11: runbooks, diseño de ChatOps, AI-BOM y modelado de amenazas.
