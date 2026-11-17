# Spec 001 – Bucket de artefactos de build

- **Estado:** borrador
- **Fecha:** 2026-11-16
- **Requerimiento origen:** requerimiento.md

## Objetivo
Proveer un bucket S3 privado, cifrado y versionado para los artefactos de build del pipeline, y un rol IAM de mínimo privilegio que solo pueda leer y escribir en él.

## Alcance
- Un bucket de artefactos con cifrado, versionado, bloqueo de acceso público y obligación de HTTPS.
- Reglas de ciclo de vida: expiración de objetos a 30 días y de versiones no vigentes a 7 días.
- Un rol IAM y una política que permitan listar el bucket y leer/escribir objetos únicamente en él.
- Etiquetas `project`, `env` y `owner` en todos los recursos que las admitan.

## Fuera de alcance
- Replicación entre regiones, registro de accesos y notificaciones de eventos.
- Quién asume el rol (el principal de confianza se define como supuesto).
- Claves KMS gestionadas por el cliente.

## Recursos
| Recurso | Servicio | Propósito |
|---|---|---|
| Bucket de artefactos | S3 | Almacén privado de artefactos |
| Configuración de versionado, cifrado, bloqueo público, ciclo de vida y política de bucket | S3 | Controles de seguridad y retención |
| Rol de pipeline | IAM | Identidad con acceso mínimo al bucket |
| Política de acceso al bucket | IAM | Permisos de lectura/escritura acotados |

## Criterios de aceptación
**CA-1 – Bucket privado**
- Dado el bucket desplegado
- Cuando se consulta su configuración de bloqueo de acceso público
- Entonces los cuatro indicadores (BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets) están en `true`

**CA-2 – Cifrado en reposo**
- Dado el bucket desplegado
- Cuando se consulta su configuración de cifrado
- Entonces el algoritmo por defecto es `AES256` o `aws:kms`

**CA-3 – Versionado**
- Dado el bucket desplegado
- Cuando se consulta su versionado
- Entonces el estado es `Enabled`

**CA-4 – Solo HTTPS**
- Dado el bucket desplegado
- Cuando se consulta su política de bucket
- Entonces existe una sentencia `Deny` para `s3:*` con condición `aws:SecureTransport = false`

**CA-5 – Retención**
- Dado el bucket desplegado
- Cuando se consulta su configuración de ciclo de vida
- Entonces los objetos expiran a los 30 días y las versiones no vigentes a los 7 días

**CA-6 – Mínimo privilegio del rol**
- Dado el rol de pipeline y su política
- Cuando se revisan las acciones y recursos permitidos
- Entonces solo incluyen `s3:ListBucket`, `s3:GetObject` y `s3:PutObject` sobre el ARN del bucket y `bucket/*`, sin comodines de servicio (`s3:*`) ni `Resource: *`

**CA-7 – Etiquetas**
- Dado el bucket y el rol desplegados
- Cuando se consultan sus etiquetas
- Entonces tienen `project`, `env` y `owner`

**CA-8 – Gate de seguridad**
- Dado el código generado
- Cuando se ejecutan Checkov, TFLint y Trivy
- Entonces no hay hallazgos HIGH ni CRITICAL sin excepción documentada

## Restricciones
- Región `us-east-1`. Nombres de recursos en inglés y con prefijo `agente-iac-`.
- Sin credenciales ni datos reales; solo el emulador local.
- Valores `env`=`local` y `project`=`agente-iac`; `owner` se toma de una variable.

## Compatibilidad con el emulador
| Operación | Verificada | Nota |
|---|---|---|
| Crear bucket, versionado, cifrado, bloqueo público, ciclo de vida, etiquetas, política de bucket | Sí (AWS CLI, 2026-11-16) | Falta confirmar la lectura de vuelta desde Terraform (fase 3) |
| IAM crear rol, crear política, adjuntar | Sí (AWS CLI, 2026-11-16) | Los códigos de error de IAM pueden diferir de AWS |

## Supuestos
- Cifrado `AES256` (SSE-S3) por defecto, por ser la opción más simple y soportada; KMS queda fuera de alcance.
- La confianza del rol se define con un servicio genérico (`ec2.amazonaws.com`) como marcador; en producción se sustituye por la identidad real del pipeline.
- `owner` no se especificó: es una variable obligatoria sin valor por defecto.
- El bucket no lleva `force_destroy`; en el emulador se vacía a mano antes de destruir.

## Preguntas abiertas
- ¿Qué identidad real asumirá el rol del pipeline? (no bloquea; se usa marcador)

## Riesgos
- Los controles de S3 pueden comportarse distinto en el emulador que en AWS; se mitiga con las pruebas de la fase 3.
- Una política `Deny` mal escrita puede bloquear al propio rol; se cubre con CA-4 y CA-6.

## Nivel de aprobación
- Spec: humano (propietario del requerimiento).
- `apply`: aprobación manual en Jenkins (desde fase 5); sin acciones destructivas automáticas.
