# Sesión 02 – Skill analizar-requerimiento

- **Fecha:** 2026-11-16
- **Fase:** Fase 2
- **Rama:** feature/fase-2-analizar-requerimiento
- **Temas del curso aplicados:** S3, S4, S7

## Objetivo
Convertir requerimientos en specs verificables y validarlas en código.

## Qué se agregó
- `agente-iac/.claude/skills/analizar-requerimiento/SKILL.md`
- `agente-iac/scripts/validar_spec.py`
- `agente-iac/specs/001-bucket-artefactos/spec.md`
- `agente-iac/specs/002-eventos-pedidos/spec.md`

## Decisiones
- **Specs sin código, con Dado/Cuando/Entonces** — criterios verificables
- **Sondeo previo en el emulador** — no prometer lo que no funciona (SNS→SQS exige política de la cola)

## Evidencia
- [commit] `7ee8a33` — commit de la fase 2
- [archivo] `agente-iac/docs/fase-2.md` — validación y sondeo del emulador

## Cómo se validó
El validador scripts/validar_spec.py y sus pruebas comprueban la estructura de cada spec; 17 criterios de aceptación escritos.

## Qué acertó y qué falló la IA
- **Acertó:** Separó el análisis (spec sin código) de la construcción y sondeó el emulador antes de comprometer criterios.
- **Falló:** El validador revisa la estructura y no la calidad semántica: una spec bien formada puede ser ambigua.

## Lección aprendida
Validar la forma en código es barato, pero la calidad del requerimiento sigue necesitando revisión humana.

## Métricas
- recursos_terraform: 0
- criterios_aceptacion: 17

## Riesgos y pendientes
- El validador revisa estructura, no calidad semántica

## Siguiente paso
Fase 3: construir-iac.
