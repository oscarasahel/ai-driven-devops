# Fase 2 – Skill analizar-requerimiento (2026-11-16)

## Qué se entregó
- Skill `.claude/skills/analizar-requerimiento/SKILL.md`.
- Plantilla `specs/_plantilla/spec.md` y validador `scripts/validar_spec.py` (sin dependencias).
- Dos requerimientos de ejemplo con spec en estado `borrador`:
  - `specs/001-bucket-artefactos`: S3 privado, cifrado, versionado, HTTPS, ciclo de vida + rol IAM de mínimo privilegio.
  - `specs/002-eventos-pedidos`: SNS a SQS con DLQ + DynamoDB con TTL y recuperación a un punto en el tiempo.

## Verificación
```powershell
docker run --rm -v "${PWD}:/w" -w /w python:3.12-slim python -I scripts/validar_spec.py specs/001-bucket-artefactos/spec.md specs/002-eventos-pedidos/spec.md
```
- Ambas specs pasan (exit 0). Una spec mala (sin secciones, con HCL, estado inválido) falla con exit 1.
- Antes de redactar, se sondearon en el emulador las operaciones que usan las specs (ver `docs/emulador-tabla.md`).

## Pendientes
- Las specs siguen en `borrador`: un humano debe pasarlas a `aprobada` antes de la fase 3.
- El validador comprueba estructura, no la calidad semántica de los criterios.
