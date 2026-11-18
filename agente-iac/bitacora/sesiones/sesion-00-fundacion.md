# Sesión 00 – Fundación

- **Fecha:** 2026-11-16
- **Fase:** Fase 0
- **Rama:** feature/fase-0-fundacion
- **Temas del curso aplicados:** S1, S3, S7

## Objetivo
Dejar la estructura, las reglas y la verificación del emulador antes de construir.

## Qué se agregó
- `agente-iac/CLAUDE.md`
- `agente-iac/docs/constitution.md`
- `agente-iac/docs/adr/001-fundacion.md`
- `agente-iac/docs/emulador-tabla.md`
- `.gitignore`

## Decisiones
- **Docker Desktop en lugar de WSL2** — es el entorno real del usuario
- **Una rama por fase** — trazabilidad y revisión por PR

## Evidencia
- [commit] `d8a5efa` — commit de la fase 0
- [archivo] `agente-iac/docs/emulador-tabla.md` — tabla de servicios y límites del emulador

## Cómo se validó
Se comprobó que el emulador responde y que la estructura y las reglas existen; no había nada que aplicar todavía.

## Qué acertó y qué falló la IA
- **Acertó:** Dejó las reglas y la estructura antes de construir, y anotó lo que no pudo verificar (tabla de fidelidad del emulador, versión no fijable).
- **Falló:** No encontró una tabla de fidelidad por servicio del emulador ni pudo fijar su versión; quedaron como riesgos.

## Lección aprendida
Fijar las reglas antes de escribir código evita decidir bajo presión; lo que no se puede fijar se declara como riesgo desde el primer día.

## Métricas
- recursos_terraform: 0
- archivos_nuevos: 19

## Riesgos y pendientes
- No se encontró tabla de fidelidad por servicio del emulador
- El RPM del emulador no se puede fijar a versión

## Siguiente paso
Fase 1: compose y prueba de humo.
