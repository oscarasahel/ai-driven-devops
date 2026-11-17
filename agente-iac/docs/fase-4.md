# Fase 4 – Skill seguridad-iac y gate local (2026-11-16)

## Qué se entregó
- Skill `.claude/skills/seguridad-iac/SKILL.md`.
- `scripts/seguridad.sh`: fmt, validate, TFLint, Checkov y Trivy en contenedores con versión fijada; informes JUnit/SARIF en `reports/` (ignorado por git).
- `policies/excepciones.json` + `scripts/excepciones.py`: excepciones con justificación y fecha de revisión; una vencida o incompleta rompe el gate.
- `.tflint.hcl` (preset recommended) y `.pre-commit-config.yaml` (raíz del repo).

## Hallazgos iniciales (sobre el código de la fase 3) y decisión
| Herramienta | Hallazgo | Decisión |
|---|---|---|
| TFLint | `required_version` ausente en 4 módulos | **Corregido** |
| Checkov CKV_AWS_26 | Tema SNS sin cifrar | **Corregido** (`kms_master_key_id = "alias/aws/sns"`, verificado en el emulador) |
| Trivy AVD-AWS-0132 (HIGH), AVD-AWS-0136 (HIGH, aparece tras cifrar SNS con clave AWS) | Exigen clave KMS propia (S3, SNS) | **Excepción** (spec deja CMK fuera de alcance) |
| Checkov CKV_AWS_145, CKV_AWS_18, CKV2_AWS_62, CKV_AWS_144, CKV_AWS_119 | KMS por defecto, logging, notificaciones y replicación S3; CMK DynamoDB | **Excepción** (fuera de alcance de specs 001/002) |
Todas con revisión el 2027-02-16.

## Verificación real
- Gate sobre `infra/`: PASS en las 6 etapas, exit 0 (Checkov 73 passed, 0 failed).
- Negativa 1: un bucket con ACL `public-read`, sin cifrar, y un security group con SSH abierto a 0.0.0.0/0 hacen **fallar** el gate (exit 1; Trivy 7 HIGH, Checkov 7 checks).
- Negativa 2: con fecha simulada 2028-01-01 las excepciones están vencidas y `excepciones.py` sale con 1.
- `pre-commit run gate-seguridad-iac --all-files`: Passed.
- Re-aplicado en el emulador tras el cambio de SNS: 15 creados, criterios de las specs 001/002 en OK, plan sin cambios; luego `destroy`.

## Límites / pendiente
- Los criterios de seguridad CA-8 (001) y CA-9 (002) ya se cumplen mediante este gate.
- Checkov no da severidad sin API key: bloquea cualquier check fallido, más estricto que HIGH/CRITICAL.
- No se instaló el hook en `.git/hooks` (`pre-commit install`); queda a decisión del usuario.
