# ai-driven-devops

Prueba de concepto **100 % local** (Docker Desktop, sin cuenta AWS) de un agente que convierte un requerimiento en lenguaje natural en infraestructura como código:

`requerimiento → spec → Terraform → gate de seguridad → plan → aprobación humana → apply → bitácora y Grafana`

Todo vive en [`agente-iac/`](agente-iac/). Los datos y la bitácora del curso son locales y no se versionan: este repositorio es público.

## Por dónde empezar
| Si quieres... | Ve a |
|---|---|
| Recorrer el proyecto y la demo | [Guía de presentación](agente-iac/docs/guia-presentacion.md) |
| Levantarlo y ver los comandos | [README de agente-iac](agente-iac/README.md) |
| Entender las reglas y decisiones | [Constitution](agente-iac/docs/constitution.md) y [ADR](agente-iac/docs/adr/) |
| Ver qué se hizo en cada fase | `agente-iac/docs/fase-N.md` |
| Ver la evidencia real de Jenkins | [agente-iac/docs/evidencia/](agente-iac/docs/evidencia/) |

## Arranque mínimo (desde `agente-iac/`)
```bash
cp .env.example .env                      # valores ficticios; no se versiona
docker compose up -d --wait               # emulador AWS, Jenkins, Grafana
```
Jenkins en `http://127.0.0.1:8080` y Grafana en `http://127.0.0.1:3000` (usuarios y contraseñas en tu `.env`).
