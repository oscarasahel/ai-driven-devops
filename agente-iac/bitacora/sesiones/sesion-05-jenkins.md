# Sesión 05 – Jenkins con aprobación manual

- **Fecha:** 2026-11-16
- **Fase:** Fase 5
- **Rama:** feature/fase-5-jenkins
- **Temas del curso aplicados:** S6, S14

## Objetivo
Orquestar el flujo en Jenkins con aprobación manual antes del apply.

## Qué se agregó
- `agente-iac/jenkins/Dockerfile`
- `agente-iac/jenkins/Jenkinsfile`
- `agente-iac/jenkins/casc/jenkins.yaml`
- `agente-iac/scripts/jenkins.sh`

## Decisiones
- **Jenkins en la red del emulador** — mismo motivo del certificado
- **Binarios copiados de imágenes oficiales** — las descargas de Trivy daban 404

## Evidencia
- [commit] `0b69f84` — commit de la fase 5
- [archivo] `agente-iac/docs/fase-5.md` — declara explícitamente que no se verificó E2E

## Cómo se validó
Se levantó Jenkins y se definió el pipeline, pero la ejecución completa no se hizo en esta sesión: quedó registrada como no verificada.

## Qué acertó y qué falló la IA
- **Acertó:** Orquestó el flujo con aprobación manual y registró con honestidad que no lo había ejecutado entero.
- **Falló:** Dejó el pipeline sin evidencia de la aprobación manual y jenkins.sh devolvió un 404 que no se diagnosticó.

## Lección aprendida
Un pipeline escrito no es un pipeline verificado; declararlo evitó dar por bueno algo sin probar.

## Métricas
- recursos_terraform: 15
- pipeline_verificado: False

## Riesgos y pendientes
- El pipeline completo NO se ejecutó: sin evidencia de la aprobación manual
- scripts/jenkins.sh devolvió 404 sin diagnosticar

## Siguiente paso
Fase 6: bitácora.
