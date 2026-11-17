# Tareas – Spec 004

Ver `plan.md`. Estado a 2026-11-17.

| # | Tarea | Criterio | Estado | Evidencia |
|---|---|---|---|---|
| T1 | Analizar el requerimiento y redactar la spec | Todos | Hecha | `spec.md`; `validar_spec.py` en OK |
| T2 | Aprobar la spec | Nivel de aprobación | Hecha | Aprobación delegada por el usuario (registrada en la spec) |
| T3 | Instanciar `secure-bucket` como `secrets_bucket` | CA-1 a CA-6 | Hecha | `infra/envs/local/main.tf` |
| T4 | `fmt`, `validate` y `plan` | CA-8 | Hecha | Plan de 21 recursos (5 del bucket de secretos) |
| T5 | Gate de seguridad sin HIGH/CRITICAL | CA-8 | Hecha | `scripts/seguridad.sh`: PASS en los 6 pasos, sin excepciones nuevas |
| T6 | Añadir los criterios al verificador | CA-1 a CA-5, CA-7 | Hecha | `scripts/verificar-criterios.sh`, sección Spec 004 |
| T7 | `apply`, verificar, plan sin cambios y `destroy` en el emulador | CA-1 a CA-5, CA-7 | Hecha | 21 creados; "TODO OK" (10 comprobaciones de la 004); `plan -detailed-exitcode` = 0; 21 destruidos |
| T8 | Ejecutar en Jenkins con aprobación manual | Nivel de aprobación | Pendiente | Solo se probó con Terraform directo en el emulador |
