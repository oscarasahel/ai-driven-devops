# Sesión 04 – Skill seguridad-iac

- **Fecha:** 2026-11-16
- **Fase:** Fase 4
- **Rama:** feature/fase-4-seguridad-iac
- **Temas del curso aplicados:** S1, S2, S3

## Objetivo
Imponer en código el gate de seguridad (TFLint, Checkov, Trivy) con excepciones documentadas.

## Qué se agregó
- `agente-iac/.claude/skills/seguridad-iac/SKILL.md`
- `agente-iac/scripts/seguridad.sh`
- `agente-iac/policies/excepciones.json`
- `.pre-commit-config.yaml`

## Decisiones
- **Excepciones con justificación y vencimiento** — una excepción vencida rompe el gate
- **Corregir SNS sin cifrar; excepcionar CMK** — las specs dejan KMS propio fuera de alcance

## Evidencia
- [commit] `760d03a` — commit de la fase 4
- [archivo] `agente-iac/docs/fase-4.md` — gate verde y dos pruebas negativas

## Cómo se validó
Se ejecutó el gate (TFLint, Checkov, Trivy): antes 1 hallazgo alto y 10 sin severidad, después 0 y 0, con 7 excepciones documentadas.

## Qué acertó y qué falló la IA
- **Acertó:** Encontró un SNS sin cifrar y lo corrigió; documentó las excepciones con justificación y vencimiento.
- **Falló:** Checkov no informa severidad sin API key, por lo que los hallazgos sin severidad hubo que clasificarlos a mano.

## Lección aprendida
Un gate sin excepciones documentadas se acaba ignorando; con justificación y vencimiento se puede sostener.

## Métricas
- recursos_terraform: 15
- hallazgos_antes: {'alta': 1, 'sin_severidad': 10}
- hallazgos_despues: {'alta': 0, 'sin_severidad': 0}
- excepciones_documentadas: 7

## Riesgos y pendientes
- Checkov no informa severidad sin API key

## Siguiente paso
Fase 5: Jenkins.
