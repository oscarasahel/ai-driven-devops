# Sesión 16 – SLI sin pruebas negativas, trazas OpenTelemetry y cliente de Jenkins

- **Fecha:** 2026-11-17
- **Fase:** Fase 17
- **Rama:** feature/fase-17-sli-otel-cliente-jenkins
- **Temas del curso aplicados:** S11

## Objetivo
Cerrar la primera versión: SLI que no penaliza las pruebas negativas, exportación de trazas en formato OpenTelemetry y cliente de Jenkins sin builds duplicados.

## Qué se agregó
- `agente-iac/policies/builds-prueba-negativa.json`
- `agente-iac/scripts/eventos_pipeline.py`
- `agente-iac/scripts/otel_exportar.py`
- `agente-iac/scripts/jenkins.sh`
- `agente-iac/docs/fase-17.md`

## Decisiones
- **Excluir del SLI solo los builds en failure listados como prueba negativa** — el control funcionando no es un defecto, pero los defectos reales deben seguir contando
- **Exportar trazas a archivo OTLP/JSON sin colector** — no añadir servicios al Compose a última hora; --enviar queda opcional y sin probar
- **jenkins.sh decide por código HTTP** — el curl de Windows devolvía distinto de 0 con 201 y el respaldo /build duplicaba builds

## Evidencia
- [commit] `e21726f` — SLI sin pruebas negativas
- [commit] `a0c7e01` — trazas OTLP/JSON
- [commit] `2e79b16` — arreglo de jenkins.sh disparar
- [archivo] `agente-iac/docs/fase-17.md` — causa del 400 y cifras del SLI

## Cómo se validó
120 pruebas; SLI del 100 % sobre una ventana de 20 builds y trazas OTLP/JSON generadas.

## Qué acertó y qué falló la IA
- **Acertó:** Excluyó del SLI solo las pruebas negativas listadas y evitó los builds duplicados decidiendo por código HTTP.
- **Falló:** No hay colector ni visor de trazas ni latencia por etapa, y --enviar no se probó contra un colector real.

## Lección aprendida
Una métrica sobre una ventana corta se puede leer mal: hay que decir de cuántos builds sale.

## Métricas
- recursos_terraform: 15
- pruebas_unitarias: 120
- sli_pipeline_pct: 100.0
- slo_pipeline_pct: 90.0

## Riesgos y pendientes
- Las trazas son un archivo: no hay colector ni visor ni latencia por etapa
- --enviar no está probado contra un colector real
- El SLI de 100 % es de una ventana de 20 builds; Jenkins rota los anteriores

## Siguiente paso
Colector OTLP real y latencia por etapa; ChatOps con canal real; evals del modelo en CI.
