# Sesión 01 – Infra base

- **Fecha:** 2026-11-16
- **Fase:** Fase 1
- **Rama:** feature/fase-1-infra-base
- **Temas del curso aplicados:** S5, S6

## Objetivo
Levantar el emulador con Docker Compose y crear un bucket S3 con Terraform.

## Qué se agregó
- `agente-iac/docker-compose.yml`
- `agente-iac/emulator/Dockerfile`
- `agente-iac/infra/envs/local/main.tf`
- `agente-iac/docs/fase-1.md`

## Decisiones
- **Terraform y AWS CLI en la red del emulador** — el certificado solo vale para localhost/127.0.0.1
- **apply sin confirmación solo en el emulador** — autorización explícita del usuario para autonomía

## Evidencia
- [commit] `e7941dc` — commit de la fase 1
- [archivo] `agente-iac/docs/fase-1.md` — resultado real: apply, ls y plan sin cambios

## Métricas
- recursos_terraform: 1
- emulador: 1.0.485
- provider_aws: 5.100.0

## Riesgos y pendientes
- La versión del emulador no es fijable

## Siguiente paso
Fase 2: skill analizar-requerimiento.
