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

## Métricas
- recursos_terraform: 0
- archivos_nuevos: 19

## Riesgos y pendientes
- No se encontró tabla de fidelidad por servicio del emulador
- El RPM del emulador no se puede fijar a versión

## Siguiente paso
Fase 1: compose y prueba de humo.
