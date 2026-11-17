# Tareas – Spec 001

> Reconstruido a posteriori (2026-11-17), con el estado real y la evidencia. Ver `plan.md`.

| # | Tarea | Criterio | Estado | Evidencia |
|---|---|---|---|---|
| T1 | Módulo `secure-bucket` | CA-1 a CA-5 | Hecha | commit 4a97c80 |
| T2 | Módulo `pipeline-role` | CA-6 | Hecha | commit 4a97c80 |
| T3 | Entorno `local` con `default_tags` y `owner` obligatorio | CA-7 | Hecha | commit 4a97c80 |
| T4 | Comprobar criterios en el emulador | CA-1 a CA-7 | Hecha | `docs/fase-3.md`; build #2 de Jenkins |
| T5 | Gate de seguridad sin HIGH/CRITICAL sin excepción | CA-8 | Hecha | commit 760d03a; CI en GitHub |
| T6 | Excepciones documentadas (KMS, logging, replicación) | CA-8 | Hecha | `policies/excepciones.json` |
| T7 | Aprobación manual antes del apply | Spec: nivel de aprobación | Hecha | `docs/fase-10.md` |
