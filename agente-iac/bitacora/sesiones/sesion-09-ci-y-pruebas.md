# Sesión 09 – Pruebas unitarias y CI en GitHub Actions

- **Fecha:** 2026-11-17
- **Fase:** Fase 9
- **Rama:** feature/fase-9-ci-y-pruebas
- **Temas del curso aplicados:** S4, S5, S15

## Objetivo
Cerrar las brechas de pruebas unitarias, CI con Gitleaks y GitHub Actions.

## Qué se agregó
- `agente-iac/tests/test_validar_spec.py`
- `agente-iac/tests/test_excepciones.py`
- `agente-iac/tests/test_bitacora.py`
- `agente-iac/scripts/excepciones.py`
- `.github/workflows/ci.yml`

## Decisiones
- **Acciones de GitHub fijadas por SHA** — cadena de suministro: un tag puede moverse, un SHA no
- **Gitleaks sobre todo el historial** — el repo es público
- **Comprobar las pruebas con mutaciones manuales** — una prueba que nunca falla no prueba nada

## Evidencia
- [commit] `c93a23c` — pruebas y workflow de CI
- [archivo] `agente-iac/docs/fase-9.md` — run de Actions 44031273761 con los 4 jobs en éxito

## Métricas
- recursos_terraform: 15
- pruebas_unitarias: 34
- jobs_ci: 4
- jobs_ci_ok: 4

## Riesgos y pendientes
- Sin protección de rama ni checks requeridos (paso manual en GitHub)
- Los evals lentos no corren en CI

## Siguiente paso
Fase 10: pipeline de Jenkins verificado de extremo a extremo.
