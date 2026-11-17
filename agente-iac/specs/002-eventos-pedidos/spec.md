# Spec 002 – Procesamiento asíncrono de eventos de pedidos

- **Estado:** aprobada
- **Aprobación:** delegada por el usuario al agente (autonomía), 2026-11-16; no revisada línea a línea por un humano
- **Fecha:** 2026-11-16
- **Requerimiento origen:** requerimiento.md

## Objetivo
Recibir eventos de pedidos en un tema SNS, encolarlos en SQS con una cola de mensajes fallidos y guardar el estado de cada pedido en una tabla DynamoDB con expiración y recuperación a un punto en el tiempo.

## Alcance
- Un tema SNS de eventos de pedidos.
- Una cola SQS principal suscrita al tema y una cola de mensajes fallidos (DLQ).
- Política de redirección: tras 3 recepciones fallidas el mensaje pasa a la DLQ; la DLQ retiene 14 días.
- Una tabla DynamoDB con clave `order_id`, pago por uso, expiración a 90 días y recuperación a un punto en el tiempo.
- Cifrado de las colas y etiquetas `project`, `env`, `owner`.

## Fuera de alcance
- Consumidor de la cola (Lambda u otro): Lambda Invoke no funciona en el emulador.
- Alarmas, métricas y suscripciones externas (correo, HTTP).
- Cifrado con claves KMS gestionadas por el cliente.

## Recursos
| Recurso | Servicio | Propósito |
|---|---|---|
| Tema de eventos | SNS | Punto de entrada de eventos |
| Cola principal | SQS | Procesamiento asíncrono |
| Cola de mensajes fallidos | SQS | Retención de mensajes no procesados |
| Política de la cola principal | SQS | Permite al tema publicar en la cola |
| Suscripción cola-tema | SNS | Entrega de eventos a la cola |
| Tabla de estado de pedidos | DynamoDB | Estado por `order_id` |

## Criterios de aceptación
**CA-1 – Entrega tema a cola**
- Dado el tema, la cola y su suscripción desplegados
- Cuando se publica un mensaje en el tema
- Entonces el mensaje se puede recibir de la cola principal

**CA-2 – Reintentos y DLQ**
- Dado la cola principal desplegada
- Cuando se consultan sus atributos de redirección
- Entonces `maxReceiveCount` es 3 y apunta al ARN de la DLQ

**CA-3 – Retención de la DLQ**
- Dado la DLQ desplegada
- Cuando se consulta su retención de mensajes
- Entonces `MessageRetentionPeriod` es 1209600 segundos (14 días)

**CA-4 – Cifrado de colas**
- Dado las dos colas desplegadas
- Cuando se consultan sus atributos
- Entonces ambas tienen cifrado habilitado (SSE-SQS o KMS)

**CA-5 – Tabla de estado**
- Dado la tabla desplegada
- Cuando se describe
- Entonces la clave hash es `order_id` de tipo cadena y el modo de facturación es `PAY_PER_REQUEST`

**CA-6 – Expiración y recuperación**
- Dado la tabla desplegada
- Cuando se consulta TTL y copias continuas
- Entonces TTL está habilitado sobre un atributo definido y la recuperación a un punto en el tiempo está habilitada

**CA-7 – Mínimo privilegio de la política de la cola**
- Dado la política de la cola principal
- Cuando se revisan sus sentencias
- Entonces solo permite `sqs:SendMessage` al servicio SNS con condición `aws:SourceArn` igual al ARN del tema

**CA-8 – Etiquetas**
- Dado todos los recursos desplegados que admiten etiquetas
- Cuando se consultan sus etiquetas
- Entonces tienen `project`, `env` y `owner`

**CA-9 – Gate de seguridad**
- Dado el código generado
- Cuando se ejecutan Checkov, TFLint y Trivy
- Entonces no hay hallazgos HIGH ni CRITICAL sin excepción documentada

## Restricciones
- Región `us-east-1`; prefijo `agente-iac-` en los nombres; solo emulador local.
- DynamoDB sin capacidad aprovisionada; sin credenciales reales.

## Compatibilidad con el emulador
| Operación | Verificada | Nota |
|---|---|---|
| DynamoDB crear tabla, TTL, recuperación a un punto en el tiempo | Sí (AWS CLI, 2026-11-16) | Fixes recientes en Query/Scan, no se usan aquí |
| SQS crear cola con retención, cifrado SSE-SQS y política de redirección (`maxReceiveCount` 3) | Sí (AWS CLI, 2026-11-16) | Los atributos se leen de vuelta correctamente |
| SNS crear tema, suscribir cola y publicar | Sí (AWS CLI, 2026-11-16) | La entrega **solo ocurre con la política de la cola que permita al tema**; sin ella el mensaje no llega (igual que en AWS) |
| Redirección real a la DLQ tras superar `maxReceiveCount` | Sí (2026-11-17, `scripts/probar-dlq.sh`) | El mensaje no borrado termina en la DLQ; CA-2 también se comprueba por atributos |

## Supuestos
- Cifrado SSE-SQS (administrado) en las colas, por ser la opción más segura sin claves a gestionar.
- Atributo de expiración llamado `expires_at` (número, epoch en segundos); el requerimiento no lo nombra.
- Retención de la cola principal por defecto (4 días); solo la DLQ pide 14 días.
- La política de la cola solo admite publicar desde el tema indicado.

## Preguntas abiertas
- ¿Se necesita un consumidor real en producción? (no bloquea; queda fuera de alcance por el emulador)

## Riesgos
- Sin la política de la cola (CA-7) no hay entrega SNS a SQS; el código debe crearla antes de la suscripción útil.
- La redirección a DLQ puede no reproducirse en el emulador; se verifica por atributos (CA-2), no por comportamiento.

## Nivel de aprobación
- Spec: humano (propietario del requerimiento).
- `apply`: aprobación manual en Jenkins (desde fase 5).
