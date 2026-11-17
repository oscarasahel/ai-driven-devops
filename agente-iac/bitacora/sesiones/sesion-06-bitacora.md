# Sesión 06 – Skill bitacora

- **Fecha:** 2026-11-16
- **Fase:** Fase 6
- **Rama:** feature/fase-6-bitacora
- **Temas del curso aplicados:** S14, S11

## Objetivo
Registrar sesiones con evidencia verificable y separar lo simulado de lo real.

## Qué se agregó
- `agente-iac/.claude/skills/bitacora/SKILL.md`
- `agente-iac/scripts/bitacora.py`
- `agente-iac/bitacora/sesiones.json`
- `agente-iac/bitacora/BITACORA.md`

## Decisiones
- **Sesiones simuladas en archivo local ignorado por git** — vienen de notas confidenciales y no deben presentarse como trabajo real
- **El validador exige commits existentes** — la evidencia se impone en código, no en el prompt

## Evidencia
- [commit] `716d1e0` — commit de la fase 6
- [archivo] `agente-iac/docs/fase-6.md` — verificación y límites

## Métricas
- recursos_terraform: 15
- sesiones_reales: 7
- sesiones_simuladas: 14

## Riesgos y pendientes
- Fechas de S1-S4 aproximadas

## Siguiente paso
Fase 7: Grafana y dashboard.
