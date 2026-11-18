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

## Cómo se validó
Los criterios se comprobaron contra el emulador (29 verificados) con terraform fmt y validate en verde.

## Qué acertó y qué falló la IA
- **Acertó:** Generó los módulos pequeños desde las specs aprobadas y comprobó los criterios en el emulador.
- **Falló:** La redirección real a la cola de mensajes fallidos (DLQ) solo se comprobó por atributos; se verificó con un mensaje real más adelante (sesión 11).

## Lección aprendida
Comprobar atributos no es comprobar comportamiento: lo que no se ejercita queda como riesgo hasta probarlo.

## Métricas
- recursos_terraform: 15
- criterios_verificados: 29

## Riesgos y pendientes
- Redirección real a la DLQ sin probar (solo por atributos)

## Siguiente paso
Fase 4: gate de seguridad.
