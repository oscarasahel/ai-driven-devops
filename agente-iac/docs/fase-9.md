# Fase 9 – Pruebas unitarias y CI en GitHub Actions (2026-11-17)

## Qué se entregó
- `tests/` con 34 pruebas pytest para `validar_spec.py`, `excepciones.py` y `bitacora.py` (`requirements-dev.txt`, `pytest.ini`). `excepciones.py` se refactorizó (`evaluar()`) para poder probarlo.
- `.github/workflows/ci.yml` con 4 jobs: pytest + validación de la bitácora, Gitleaks sobre todo el historial, gate de seguridad (fmt, validate, TFLint, Checkov, Trivy) con informes JUnit/SARIF como artefacto, y evals rápidos. Acciones fijadas por SHA, permisos mínimos (`contents: read`).

## Verificación real
- `pytest`: 34 pasan. Prueba de mutación manual: al romper `MAX_PREGUNTAS` y la comprobación de vencimiento, las pruebas correspondientes fallan; al restaurar vuelven a pasar.
- `actionlint` sin hallazgos.
- Gitleaks sobre las 14 commits de todas las ramas: sin fugas (el repo es público).
- **GitHub Actions** (run 44031273761 en `feature/fase-9-ci-y-pruebas`): los 4 jobs terminaron en éxito.

## Límites
- Los evals completos (con el gate lento) no corren en CI; el job de seguridad ya cubre el gate sobre `infra/`.
- No hay protección de rama ni checks requeridos en GitHub: configurarlo es un paso manual del dueño del repo.
