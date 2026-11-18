# Sesión 08 – Endurecimiento y evals

- **Fecha:** 2026-11-16
- **Fase:** Fase 8
- **Rama:** feature/fase-8-endurecimiento
- **Temas del curso aplicados:** S7, S13

## Objetivo
Fijar con evals y pruebas negativas lo que el sistema impone en código, y documentar el estado real.

## Qué se agregó
- `agente-iac/evals/run_evals.sh`
- `agente-iac/README.md`
- `agente-iac/docs/fase-8.md`

## Decisiones
- **Evals deterministas sin LLM** — repetibles y sin costo; el comportamiento del modelo queda declarado como no cubierto
- **README con estado real por criterio** — no presentar como hecho lo que no se ejecutó

## Evidencia
- [commit] `4067d49` — commit de la fase 8
- [archivo] `agente-iac/docs/fase-8.md` — 16/16 casos con el resultado esperado

## Cómo se validó
16 evals deterministas en verde y pruebas negativas; README con el estado real por criterio.

## Qué acertó y qué falló la IA
- **Acertó:** Fijó con evals deterministas lo que el sistema impone en código y documentó el estado real.
- **Falló:** Quedaron sin cubrir el pipeline de Jenkins de extremo a extremo y la ambigüedad o inyección de prompt a nivel del modelo.

## Lección aprendida
Los evals sin modelo cubren lo que el código garantiza, no lo que el modelo decide.

## Métricas
- recursos_terraform: 15
- evals_total: 16
- evals_ok: 16

## Riesgos y pendientes
- Pipeline de Jenkins sin verificar de extremo a extremo
- Ambigüedad e inyección de prompt a nivel del modelo sin evals automáticos

## Siguiente paso
Revisar y fusionar las ramas; ejecutar el pipeline de Jenkins a mano.
