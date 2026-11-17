# Spec 003 – Staging y promoción controlada de entornos

- **Estado:** aprobada
- **Aprobación:** el usuario aprobó el enfoque (workspaces, aprobación manual en ambos entornos), 2026-11-17
- **Fecha:** 2026-11-17
- **Requerimiento origen:** requerimiento.md

## Objetivo
Añadir un entorno `staging` aislado del entorno principal (`local`) y una compuerta que solo permita aplicar en `local` el código ya aplicado y verificado en `staging`.

## Alcance
- Un workspace de Terraform `staging`, con estado propio, sobre el mismo módulo raíz.
- Variables de staging: `env=staging` y prefijo `agente-iac-stg`, para que los nombres no choquen con `local`.
- Parámetro `ENTORNO` (`staging` o `local`) en el pipeline de Jenkins; `staging` por defecto.
- Compuerta de promoción por huella del código (`infra/`): sin apply verificado en staging, el apply en `local` se bloquea antes de planificar.
- Las pruebas de humo se ejecutan contra el prefijo del entorno elegido.
- Destruir staging revoca la habilitación de promoción.

## Fuera de alcance
- Un segundo emulador o cuenta separada (no hay aislamiento de credenciales).
- Despliegues blue/green o canary.
- Separar solicitante y aprobador (en esta PoC es la misma persona).

## Recursos
| Recurso | Servicio | Propósito |
|---|---|---|
| Copia del entorno con prefijo `agente-iac-stg` | S3, IAM, SNS, SQS, DynamoDB | Ensayo previo del cambio |
| Marcador de promoción (archivo por huella) | Jenkins | Registrar qué código pasó por staging |

## Criterios de aceptación
**CA-1 – Staging aislado**
- Dado el código actual
- Cuando se aplica en staging
- Entonces se crean los recursos con prefijo `agente-iac-stg` y los de `local` no cambian

**CA-2 – Promoción bloqueada sin staging**
- Dado un código sin apply verificado en staging
- Cuando se intenta aplicar en `local`
- Entonces el pipeline falla en la compuerta, antes del plan y de la aprobación

**CA-3 – Promoción permitida con staging verificado**
- Dado un apply en staging con pruebas de humo en verde
- Cuando se aplica el mismo código en `local`
- Entonces la compuerta lo permite y sigue pidiendo aprobación manual

**CA-4 – Un cambio invalida la promoción**
- Dado un código ya verificado en staging
- Cuando cambia cualquier archivo de Terraform de `infra/`
- Entonces la promoción vuelve a bloquearse hasta repetir staging

**CA-5 – Destruir staging no toca local**
- Dado ambos entornos desplegados
- Cuando se destruye staging
- Entonces los recursos de `local` siguen intactos y la promoción queda revocada

**CA-6 – Aprobación manual en ambos**
- Dado cualquier apply o destroy en cualquier entorno
- Cuando el plan está listo
- Entonces el pipeline espera una aprobación manual antes de aplicar

## Restricciones
- Región `us-east-1`; solo emulador local; sin credenciales reales.
- La huella solo cubre `infra/`; no incluye scripts ni el Jenkinsfile.

## Compatibilidad con el emulador
| Operación | Verificada | Nota |
|---|---|---|
| Workspaces de Terraform con backend local | Pendiente | No depende del emulador; se verifica en Jenkins (fase 16) |
| Crear una segunda copia de los recursos con otro prefijo | Pendiente | Mismos servicios ya verificados; los nombres globales deben diferir |

## Supuestos
- Los workspaces bastan como aislamiento de estado; no aíslan credenciales ni cuenta.
- El marcador vive en el volumen de Jenkins, fuera del workspace del job.
- Staging es el valor por defecto del parámetro para que un lanzamiento sin elegir no toque `local`.

## Preguntas abiertas
- ¿Se necesita un aprobador distinto en `local`? (no bloquea; queda para una fase posterior)

## Riesgos
- Mismo emulador y credenciales: un error de prefijo podría tocar recursos de `local`.
- La huella no cubre scripts ni Jenkinsfile; un cambio ahí no invalida la promoción.
- Recrear el emulador borra ambos entornos y deja marcadores obsoletos.

## Nivel de aprobación
- Spec: humano (propietario del requerimiento).
- `apply` y `destroy` en cualquier entorno: aprobación manual en Jenkins.
