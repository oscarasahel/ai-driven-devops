# Sesión 03 – Skill construir-iac

- **Fecha:** 2026-11-16
- **Fase:** Fase 3
- **Rama:** feature/fase-3-construir-iac
- **Temas del curso aplicados:** S1, S9, S10

## Objetivo
Generar módulos Terraform desde las specs aprobadas y comprobar los criterios en el emulador.

## Qué se agregó
- `agente-iac/.claude/skills/construir-iac/SKILL.md`
- `agente-iac/infra/modules/secure-bucket/main.tf`
- `agente-iac/infra/modules/order-events/main.tf`
- `agente-iac/scripts/verificar-criterios.sh`

## Decisiones
- **Specs aprobadas por delegación** — el usuario pidió autonomía; queda anotado en cada spec

## Evidencia
- [commit] `4a97c80` — commit de la fase 3
- [archivo] `agente-iac/docs/fase-3.md` — 15 recursos aplicados, verificación TODO OK, destroy

## Métricas
- recursos_terraform: 15
- criterios_verificados: 29

## Riesgos y pendientes
- Redirección real a la DLQ sin probar (solo por atributos)

## Siguiente paso
Fase 4: gate de seguridad.
