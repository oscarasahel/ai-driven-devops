# Sesión 11 – Runbooks, ChatOps, AI-BOM y modelo de amenazas

- **Fecha:** 2026-11-17
- **Fase:** Fase 11
- **Rama:** feature/fase-11-runbooks-chatops-amenazas
- **Temas del curso aplicados:** S13, S14, S15, S3

## Objetivo
Cerrar las brechas de documentación operativa y de seguridad frente a las sesiones de runbooks, ChatOps y DevSecOps.

## Qué se agregó
- `agente-iac/docs/runbooks/jenkins-falla-construccion-imagen.md`
- `agente-iac/docs/runbooks/jenkins-pipeline-falla.md`
- `agente-iac/docs/runbooks/revision-previa-al-apply.md`
- `agente-iac/docs/chatops-diseno.md`
- `agente-iac/docs/seguridad/ai-bom.md`
- `agente-iac/docs/seguridad/modelo-de-amenazas.md`
- `agente-iac/scripts/probar-dlq.sh`

## Decisiones
- **Runbooks a partir de incidentes reales** — un runbook basado en fallos ocurridos se puede contrastar con la evidencia
- **plan.md y tasks.md marcados como reconstruidos a posteriori** — no presentar como previo lo que se escribió después
- **Documentación con contenido propio y sin material del curso** — el repositorio es público

## Evidencia
- [commit] `af43bc9` — documentación y prueba de la DLQ
- [archivo] `agente-iac/docs/fase-11.md` — qué se verificó y qué no

## Métricas
- recursos_terraform: 15
- runbooks: 3
- riesgos_owasp_revisados: 20
- dlq_comportamiento_verificado: True

## Riesgos y pendientes
- ChatOps es solo diseño
- Runbook de revisión previa no probado con un plan destructivo inesperado
- Numeración OWASP a verificar contra la versión vigente

## Siguiente paso
Fase 12: higiene del repositorio público, telemetría del pipeline y actualización del dashboard.
