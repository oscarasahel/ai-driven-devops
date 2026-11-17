# Tareas – Spec 002

> Reconstruido a posteriori (2026-11-17), con el estado real y la evidencia. Ver `plan.md`.

| # | Tarea | Criterio | Estado | Evidencia |
|---|---|---|---|---|
| T1 | Módulo `order-events` (tema, colas, política, suscripción) | CA-1 a CA-4, CA-7 | Hecha | commit 4a97c80 |
| T2 | Módulo `order-state-table` | CA-5, CA-6 | Hecha | commit 4a97c80 |
| T3 | Etiquetas en todos los recursos | CA-8 | Hecha | `default_tags`; `verificar-criterios.sh` |
| T4 | Cifrar el tema SNS | Hallazgo de seguridad | Hecha | commit 760d03a |
| T5 | Gate de seguridad con excepciones | CA-9 | Hecha | CI en GitHub |
| T6 | Comprobar entrega tema a cola y atributos | CA-1 a CA-8 | Hecha | build #2 de Jenkins |
| T7 | Probar la redirección real a la DLQ tras superar `maxReceiveCount` | CA-2 (comportamiento) | Hecha | `scripts/probar-dlq.sh` (2026-11-17): el mensaje llegó a la DLQ |
