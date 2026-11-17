# Tareas – Spec 003

| # | Tarea | Criterio | Estado | Evidencia |
|---|---|---|---|---|
| T1 | `staging.tfvars` y workspace `staging` en el pipeline | CA-1 | Hecha | build #13 |
| T2 | Parámetro `ENTORNO` y etapa «Entorno» en el Jenkinsfile | CA-1, CA-6 | Hecha | `jenkins/Jenkinsfile` |
| T3 | `scripts/promocion.py` (huella, marcar, exigir, revocar) | CA-2 a CA-5 | Hecha | `tests/test_promocion.py` (8 pruebas) |
| T4 | Compuerta de promoción antes del plan | CA-2, CA-3, CA-4 | Hecha | builds #12, #14, #15 |
| T5 | Registro y revocación de la promoción | CA-3, CA-5 | Hecha | builds #13, #16, #17 |
| T6 | Pruebas de humo parametrizadas por prefijo | CA-1 | Hecha | `NAME_PREFIX`; build #13 |
| T7 | Prueba de extremo a extremo en Jenkins | CA-1 a CA-6 | Hecha | `docs/evidencia/jenkins-promocion.log` |
