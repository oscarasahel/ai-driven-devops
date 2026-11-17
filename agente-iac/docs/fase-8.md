# Fase 8 – Endurecimiento (2026-11-16)

## Qué se entregó
- `evals/run_evals.sh`: 16 casos con código de salida esperado (14 rápidos + 2 del gate), sin LLM ni emulador.
- README con el estado real de cada criterio global y los límites.

## Casos
- Specs: 2 válidas; negativas: ambigüedad sin priorizar (7 preguntas), HCL embebido, sin Estado, criterios sin Entonces.
- Proceso: "Aprobación manual" antecede a "Apply" en el Jenkinsfile; sin `-auto-approve`; sin credenciales AKIA en archivos versionados; `.env` no versionado.
- Bitácora: sesión real con commit inexistente rechazada; bitácora actual válida.
- Excepciones: vigentes hoy / vencidas con fecha simulada.
- Gate: pasa sobre `infra/`; falla ante un bucket S3 público sin cifrar.

## Resultado real
16/16 coinciden con lo esperado. Un caso falló en la primera corrida por un defecto del propio eval (`xargs` devuelve 123 si algún grep no halla coincidencias); se cambió a `git grep` y pasó.

## Lo que NO cubren
- Ambigüedad e inyección de prompt a nivel del modelo (requeriría ejecutar el agente con un conjunto de requerimientos y revisar sus respuestas).
- El pipeline de Jenkins de extremo a extremo (ver fase 5).
