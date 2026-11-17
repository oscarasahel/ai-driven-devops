# Plan técnico – Spec 002 (eventos de pedidos)

> **Reconstruido a posteriori (2026-11-17):** el código precedió a este documento. Ver el aviso de `specs/001-bucket-artefactos/plan.md`.

## Enfoque
| Módulo | Responsabilidad | Criterios que cubre |
|---|---|---|
| `infra/modules/order-events` | Tema SNS (cifrado con la clave administrada), cola principal y DLQ (SSE-SQS, `maxReceiveCount` 3, retención 14 d en la DLQ), política de la cola, suscripción | CA-1 a CA-4, CA-7 |
| `infra/modules/order-state-table` | Tabla DynamoDB `order_id`, pago por uso, TTL en `expires_at`, recuperación a un punto en el tiempo | CA-5, CA-6 |
| `infra/envs/local` | Compone los módulos y aplica etiquetas | CA-8 |

## Decisiones
- La política de la cola es **obligatoria**: sin ella SNS no entrega (verificado en el emulador). La suscripción depende de ella (`depends_on`).
- Atributo de expiración `expires_at` (supuesto de la spec).
- La redirección real a la DLQ se probó en el emulador con colas temporales (`scripts/probar-dlq.sh`), además de verificarse por atributos (CA-2).

## Riesgos
Lambda Invoke no funciona en el emulador: por eso no hay consumidor en el alcance.
