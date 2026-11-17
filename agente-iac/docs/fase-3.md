# Fase 3 – Skill construir-iac (2026-11-16)

## Aprobación de specs
Las specs 001 y 002 pasaron a `aprobada` por **aprobación delegada del usuario al agente** (instrucción "apruébalos con autonomía"). No hubo revisión línea a línea de un humano; queda anotado en cada spec.

## Qué se entregó
- Skill `.claude/skills/construir-iac/SKILL.md`.
- Módulos en `infra/modules/`: `secure-bucket`, `pipeline-role`, `order-events`, `order-state-table`.
- Entorno `infra/envs/local` (reemplaza la prueba de humo de la fase 1) con `terraform.tfvars` (`owner = "platform-team"`).
- `scripts/verificar-criterios.sh`: comprueba los criterios CA de ambas specs contra el emulador.
- `docker-compose.yml`: el servicio `terraform` monta `./infra` completo para resolver los módulos.

## Verificación real (emulador v1.0.485, provider aws 5.100.0)
| Paso | Resultado |
|---|---|
| `fmt -recursive -check` | sin diferencias |
| `init` / `validate` | OK |
| `plan` | 15 a crear |
| `apply` del plan | 15 creados |
| `plan -detailed-exitcode` posterior | sin cambios |
| `scripts/verificar-criterios.sh` | **TODO OK** (CA de seguridad 001-CA-8 y 002-CA-9 corresponden a la fase 4, aún no se ejecutan) |
| `destroy` | ver commit / bitácora |

## Hallazgos del emulador
- Terraform lee de vuelta correctamente S3 (versionado, cifrado, bloqueo público, ciclo de vida, política, etiquetas), IAM, SNS, SQS (redrive, SSE, política) y DynamoDB (TTL, PITR). Sin `plan` fantasma.
- Los tiempos varían: la creación de colas SQS y el ciclo de vida de S3 tardaron ~25 s y ~55 s.
- `default_tags` del provider se aplican a todos los recursos verificados.
- Se corrigió un defecto del script de verificación (no del código): `list-queue-tags --output text` omite claves, ahora se consultan con `keys(Tags)`.

## Pendiente (fase 4)
- Gate de seguridad (Checkov/TFLint/Trivy). Probable hallazgo: SNS sin cifrado con KMS y DynamoDB/SQS sin clave gestionada por el cliente; decidir corregir o documentar excepción.
- Sigue sin probarse la redirección real a la DLQ (solo por atributos).
