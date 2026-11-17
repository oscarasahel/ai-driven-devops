# Sesión 15 – Staging con workspaces y promoción controlada

- **Fecha:** 2026-11-17
- **Fase:** Fase 16
- **Rama:** feature/fase-16-staging-promocion
- **Temas del curso aplicados:** S5

## Objetivo
Probar los cambios en un entorno staging aislado y permitir aplicar en local solo el código ya verificado en staging; fijar plugins e imágenes.

## Qué se agregó
- `agente-iac/specs/003-promocion-entornos/spec.md`
- `agente-iac/jenkins/Jenkinsfile`
- `agente-iac/scripts/promocion.py`
- `agente-iac/scripts/probar-promocion-jenkins.sh`
- `agente-iac/tests/test_promocion.py`
- `agente-iac/jenkins/plugins.txt`
- `agente-iac/docs/fase-16.md`

## Decisiones
- **Workspaces de Terraform sobre un único módulo** — menos duplicación y más fácil de administrar que directorios separados
- **Aprobación manual en staging y en local** — mantiene la regla de ningún apply sin aprobación
- **Compuerta por huella del contenido de infra/** — Jenkins no ve .git; así se promueve exactamente lo que se probó
- **No separar solicitante y aprobador** — en esta PoC es la misma persona

## Evidencia
- [commit] `c2d9ad6` — staging con workspaces y compuerta de promoción
- [archivo] `agente-iac/docs/evidencia/jenkins-promocion.log` — logs de los builds #12 a #18
- [archivo] `agente-iac/docs/fase-16.md` — 10 comprobaciones PASS en Jenkins

## Métricas
- recursos_terraform: 15
- pruebas_unitarias: 103
- sli_pipeline_pct: 75.0
- slo_pipeline_pct: 90.0

## Riesgos y pendientes
- Los workspaces aíslan el estado, no las credenciales ni la cuenta
- La huella solo cubre infra/, no scripts ni el Jenkinsfile
- jenkins.sh disparar muestra a veces un 400 inocuo y puede lanzar builds duplicados

## Siguiente paso
Marcar los builds de prueba negativa para excluirlos del SLI; S11 (OpenTelemetry).
