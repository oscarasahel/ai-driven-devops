# Sesión 07 – Grafana y dashboard por sesión

- **Fecha:** 2026-11-16
- **Fase:** Fase 7
- **Rama:** feature/fase-7-grafana
- **Temas del curso aplicados:** S11, S7

## Objetivo
Visualizar el avance por sesión con un dashboard aprovisionado como código.

## Qué se agregó
- `agente-iac/grafana/dashboards/avance-por-sesion.json`
- `agente-iac/grafana/provisioning/datasources/bitacora.yaml`
- `agente-iac/docker-compose.yml`
- `agente-iac/scripts/generar_dashboard.py`

## Decisiones
- **Agregados calculados en bitacora.py (resumen.json)** — Grafana solo muestra, la lógica queda en código testeable
- **Infinity 3.7.1 con Grafana 11.4.0** — versiones fijadas y compatibles

## Evidencia
- [commit] `56425d6` — commit de la fase 7
- [archivo] `agente-iac/docs/fase-7.md` — consultas de los 7 paneles verificadas por API

## Cómo se validó
Dashboard aprovisionado como código; 7 paneles con datos comprobados contra la API de Grafana.

## Qué acertó y qué falló la IA
- **Acertó:** Calculó los agregados en bitacora.py y dejó el dashboard versionado.
- **Falló:** No se pudo revisar el aspecto visual (sin navegador) y el estado del pipeline no estaba conectado a métricas vivas.

## Lección aprendida
Que los paneles devuelvan datos no demuestra que se vean bien; la revisión visual es un paso aparte.

## Métricas
- recursos_terraform: 15
- paneles: 7
- paneles_con_datos: 7

## Riesgos y pendientes
- Aspecto visual no revisado (sin navegador)
- Estado del pipeline no conectado a métricas vivas

## Siguiente paso
Fase 8: evals, pruebas negativas y README.
