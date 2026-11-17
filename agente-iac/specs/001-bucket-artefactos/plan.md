# Plan técnico – Spec 001 (bucket de artefactos)

> **Reconstruido a posteriori (2026-11-17):** el código se escribió antes que este documento, que describe lo que se hizo y por qué. En specs futuras `plan.md` y `tasks.md` se escriben antes de construir.

## Enfoque
Dos módulos pequeños y un entorno que los compone, con el endpoint, la CA y las credenciales del emulador por variables de entorno (no en el código).

| Módulo | Responsabilidad | Criterios que cubre |
|---|---|---|
| `infra/modules/secure-bucket` | Bucket + bloqueo de acceso público + versionado + cifrado AES256 + ciclo de vida (30/7 días) + política solo-HTTPS | CA-1 a CA-5 |
| `infra/modules/pipeline-role` | Rol IAM + política con `ListBucket` y `Get/PutObject` solo sobre el bucket | CA-6 |
| `infra/envs/local` | Compone ambos; `default_tags` (project, env, owner) | CA-7 |
| `scripts/seguridad.sh` | Gate de seguridad | CA-8 |

## Decisiones
- Cifrado SSE-S3 (AES256); KMS gestionado por el cliente fuera de alcance (excepciones documentadas en `policies/excepciones.json`).
- `owner` es variable obligatoria sin valor por defecto; el valor local vive en `terraform.tfvars`.
- `depends_on` explícito: el ciclo de vida exige versionado; la política exige el bloqueo público.

## Riesgos
Comportamiento del emulador distinto del de AWS: mitigado con `scripts/verificar-criterios.sh` (29 criterios entre ambas specs) y la ejecución en Jenkins.
