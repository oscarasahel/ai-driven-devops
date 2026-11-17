# AWS Emulator – verificación (fase 0)

Fecha: 2026-11-16. Fuente: https://github.com/aws/aws-emulator y guías en docs.aws.amazon.com/emulator. Lectura vía subagente; **no se ejecutó nada todavía** (se valida en fase 1).

## Hechos verificados
| Tema | Dato | Fuente |
|---|---|---|
| Última release | v1.0.485 (commit a2568e8) | /releases |
| Imagen Docker | No hay imagen publicada: se construye con un Dockerfile | getting-started-docker |
| Base | `public.ecr.aws/amazonlinux/amazonlinux:2023-minimal` + RPM de `downloads.aws.com/.../LTS/latest/` | getting-started-docker |
| Versión fijable | **No documentada**: el RPM es `LTS/latest`; la versión depende del momento del build | idem |
| Acceso | HTTPS `127.0.0.1:9297`; publicar como `127.0.0.1:9297:9297` | idem |
| Telemetría | Activada por defecto. Apagar con `--telemetry off` (tras el nombre de imagen), `EMULATOR_TELEMETRY=off` o `config.toml` | README |
| Salud | `GET https://127.0.0.1:9297/__admin/health` -> `ok` (con `--cacert ca.pem`) | point-sdk-to-emulator |
| Certificado | `ca.pem` en `~/.aws/emulator/9297/`; cambia en cada arranque; firma SigV4 obligatoria | idem |
| Memoria | Límite 2 GiB (`--memory=2g`); si se excede, sale con 137 | getting-started-docker |
| Terraform | **No hay documentación del provider/endpoints**; solo consta que CLI/SDKs leen `AWS_ENDPOINT_URL` | no encontrado |
| Fidelidad por servicio | **No encontré tabla**; el README dice que se publica con cada release, pero la página no la muestra | /releases |

## Servicios relevantes (estado según notas e issues; no es puntuación de fidelidad)
| Servicio | Señales | Riesgo para la PoC |
|---|---|---|
| S3 | Fixes recientes (ListObjectsV2, GetObject); sin issue abierto propio | Bajo. Servicio candidato para prueba de humo |
| IAM | Fixes en códigos de error y MFA | Medio: códigos de error pueden diferir de AWS |
| EC2/VPC | Fixes por 501 NotImplemented en operaciones y proyecciones Describe incompletas; CreateSubnet citado como stub | **Alto**: VPC/subnets pueden fallar |
| DynamoDB | Fixes en Query/Scan con índices y proyecciones | Medio |
| Lambda | Issue HIGH: `Invoke` responde NotImplemented (sin runtime; DryRun sí) | **Alto**: se puede crear la función, no ejecutarla |
| SQS / SNS | Solo fixes de validación e integraciones | Bajo-medio |
| KMS | `TagResource` responde NotImplemented | Medio: tags en claves fallan |

## Pendientes de verificar en fase 1
1. Si el provider de Terraform funciona con HTTPS + CA propia (variables `AWS_CA_BUNDLE`, `AWS_ENDPOINT_URL`) y qué endpoints por servicio exige.
2. Lista oficial de servicios (`what-is-service.html`) y assets de la release.
3. Si el `Dockerfile` puede fijarse a una versión concreta; de no poder, registrar la versión efectiva (`aws-emulator --version`) en la bitácora.
4. Las ~4.900 entradas de `issues/things-that-do-not-work` no se leyeron; se consultarán por servicio antes de cada requerimiento.
