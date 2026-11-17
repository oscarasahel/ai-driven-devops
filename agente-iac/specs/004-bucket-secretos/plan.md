# Plan técnico – Spec 004 (bucket de secretos)

## Enfoque
Reutilizar el módulo existente `secure-bucket` sin modificarlo: una segunda instancia en el entorno `local` con otro nombre. El módulo ya aporta bloqueo de acceso público, versionado, cifrado AES256, ciclo de vida (30/7 días) y política solo-HTTPS.

| Pieza | Responsabilidad | Criterios que cubre |
|---|---|---|
| `infra/modules/secure-bucket` (sin cambios) | Controles de seguridad y retención del bucket | CA-1 a CA-5 |
| `infra/envs/local/main.tf` (instancia `secrets_bucket`) | Nombre `<prefijo>-secrets` y output del ARN | CA-6 |
| `default_tags` del provider | Etiquetas project, env y owner | CA-7 |
| `scripts/seguridad.sh` | Gate de seguridad | CA-8 |
| `scripts/verificar-criterios.sh` (sección Spec 004) | Comprobación contra el emulador | CA-1 a CA-5 y CA-7 |

## Decisiones
- Sin módulo nuevo ni rol IAM (aún no existe quién lo asuma).
- SSE-S3 (AES256); sin clave KMS propia. Cubierto por las excepciones ya documentadas de `secure-bucket` en `policies/excepciones.json`.
- Versiones no vigentes a 7 días (valor por defecto del módulo, confirmado por el usuario).
- Nombre `<prefijo>-secrets` para respetar el prefijo de entorno de staging (spec 003).

## Riesgos
- S3 no es el servicio ideal para secretos (Secrets Manager o SSM): el bucket se despliega vacío y no admite valores reales.
- Con versionado, la expiración a 30 días crea un marcador de borrado; el borrado definitivo depende de la regla de versiones no vigentes.
