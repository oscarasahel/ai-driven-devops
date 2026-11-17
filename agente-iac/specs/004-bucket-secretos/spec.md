# Spec 004 – Bucket de secretos de aplicación

- **Estado:** aprobada
- **Aprobación:** delegada por el usuario al agente, 2026-11-17; no revisada línea a línea por un humano
- **Fecha:** 2026-11-17
- **Requerimiento origen:** requerimiento.md

## Objetivo
Proveer un bucket S3 privado, cifrado y versionado para guardar los secretos de una aplicación, con expiración automática de los objetos a los 30 días, reutilizando el módulo existente `secure-bucket`.

## Alcance
- Una instancia del módulo `secure-bucket` con nombre propio para secretos.
- Cifrado en reposo, versionado, bloqueo de acceso público y obligación de HTTPS (controles que ya aporta el módulo).
- Expiración de objetos a los 30 días.
- Etiquetas `project`, `env` y `owner` heredadas de la configuración común.

## Fuera de alcance
- Rol o política IAM de acceso al bucket (no se pidió; quién lee y escribe los secretos queda por definir).
- Claves KMS gestionadas por el cliente, replicación, registro de accesos y notificaciones.
- Cualquier valor de secreto real: el bucket se despliega vacío.
- Cambios al código del módulo `secure-bucket`.

## Recursos
| Recurso | Servicio | Propósito |
|---|---|---|
| Bucket de secretos | S3 | Almacén privado de secretos de la aplicación |
| Versionado, cifrado, bloqueo público, ciclo de vida y política de bucket (aportados por el módulo) | S3 | Controles de seguridad y retención |

## Criterios de aceptación
**CA-1 – Bucket privado**
- Dado el bucket de secretos desplegado
- Cuando se consulta su configuración de bloqueo de acceso público
- Entonces los cuatro indicadores (BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets) están en `true`

**CA-2 – Cifrado en reposo**
- Dado el bucket de secretos desplegado
- Cuando se consulta su configuración de cifrado
- Entonces el algoritmo por defecto es `AES256` o `aws:kms`

**CA-3 – Versionado**
- Dado el bucket de secretos desplegado
- Cuando se consulta su versionado
- Entonces el estado es `Enabled`

**CA-4 – Expiración a 30 días**
- Dado el bucket de secretos desplegado
- Cuando se consulta su configuración de ciclo de vida
- Entonces existe una regla habilitada que expira los objetos a los 30 días y las versiones no vigentes a los 7 días

**CA-5 – Solo HTTPS**
- Dado el bucket de secretos desplegado
- Cuando se consulta su política de bucket
- Entonces existe una sentencia `Deny` para `s3:*` con condición `aws:SecureTransport = false`

**CA-6 – Reutilización del módulo**
- Dado el código generado
- Cuando se revisa cómo se crea el bucket
- Entonces el bucket proviene del módulo `secure-bucket` y no se define ningún recurso de bucket S3 fuera del módulo

**CA-7 – Etiquetas**
- Dado el bucket de secretos desplegado
- Cuando se consultan sus etiquetas
- Entonces tiene `project`, `env` y `owner`

**CA-8 – Gate de seguridad**
- Dado el código generado
- Cuando se ejecutan Checkov, TFLint y Trivy
- Entonces no hay hallazgos HIGH ni CRITICAL sin excepción documentada

## Restricciones
- Región `us-east-1`. Nombres de recursos en inglés y con prefijo `agente-iac-`.
- Sin credenciales ni datos reales; solo el emulador local.
- Valores `env`=`local` y `project`=`agente-iac`; `owner` se toma de una variable.
- No se modifica el módulo `secure-bucket`; solo se parametriza desde fuera.

## Compatibilidad con el emulador
| Operación | Verificada | Nota |
|---|---|---|
| S3: crear bucket, versionado, cifrado, bloqueo público, ciclo de vida, etiquetas, política de bucket | Sí (AWS CLI, 2026-11-16; Terraform, spec 001) | El módulo ya se aplica en el emulador |
| KMS con clave propia | No aplica | `TagResource` de KMS no está soportado; por eso se usa SSE-S3 |

## Supuestos
- Cifrado `AES256` (SSE-S3) por defecto del módulo; el usuario confirmó que no se usará clave KMS propia. Reutiliza la excepción ya documentada para `secure-bucket` en `policies/excepciones.json` (revisión 2027-02-16).
- Versiones no vigentes: se conservan 7 días (valor por defecto del módulo), confirmado por el usuario.
- Nombre del bucket: `<prefijo>-secrets` (`agente-iac-secrets` en local, `agente-iac-stg-secrets` en staging), siguiendo el patrón de la spec 001 y el prefijo de entorno de la spec 003.
- No se crea rol IAM porque todavía no existe; sin él solo un administrador puede leer o escribir en el bucket. Se añadirá en una spec posterior.
- `owner` no se especificó: es una variable obligatoria sin valor por defecto.
- El bucket no lleva `force_destroy`; en el emulador se vacía a mano antes de destruir.

## Preguntas abiertas
- Ninguna. Resueltas por el usuario el 2026-11-17: aún no hay rol IAM (fuera de alcance), las versiones no vigentes se conservan solo 7 días y no se usará clave KMS propia.

## Riesgos
- Guardar secretos en S3 es un patrón débil frente a AWS Secrets Manager o SSM Parameter Store (rotación, auditoría, control por secreto); Secrets Manager no está verificado en el emulador. Mitigación: la spec solo despliega el bucket vacío y no admite valores reales.
- Con versionado, la expiración a 30 días solo crea un marcador de borrado; el borrado definitivo depende de la regla de versiones no vigentes (7 días). Mitigación: CA-4 y el supuesto de versiones no vigentes lo hacen explícito.
- Los controles de S3 pueden comportarse distinto en el emulador que en AWS; se mitiga con las pruebas de la fase de construcción.

## Nivel de aprobación
- Spec: humano (propietario del requerimiento); aprobación delegada al agente el 2026-11-17.
- `apply`: aprobación manual en Jenkins; sin acciones destructivas automáticas.
