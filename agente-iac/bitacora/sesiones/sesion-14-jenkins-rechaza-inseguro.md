# Sesión 14 – El gate rechaza un recurso inseguro dentro de Jenkins

- **Fecha:** 2026-11-17
- **Fase:** Fase 15
- **Rama:** feature/fase-15-jenkins-rechaza-inseguro
- **Temas del curso aplicados:** S13, S15

## Objetivo
Demostrar que el pipeline de Jenkins rechaza un recurso inseguro antes de planificar o pedir aprobación, y corregir lo que la prueba destapara.

## Qué se agregó
- `agente-iac/scripts/probar-gate-jenkins.sh`
- `.gitattributes`
- `agente-iac/tests/test_higiene.py`
- `agente-iac/docs/runbooks/jenkins-pipeline-falla.md`
- `agente-iac/docs/fase-15.md`

## Decisiones
- **Comprobar el contenido del log y no solo que el build falle** — el build #5 falló por scripts con CRLF y no por el gate; un criterio ingenuo lo habría dado por bueno
- **Forzar LF con .gitattributes** — Jenkins monta el árbol de trabajo de Windows y los scripts con CRLF no se ejecutan en Linux
- **No excluir el build de la prueba negativa del SLI** — el SLI no distingue la etapa del fallo; se documenta en observabilidad

## Evidencia
- [commit] `a4eb82f` — prueba negativa en Jenkins y finales de línea LF
- [archivo] `agente-iac/docs/evidencia/jenkins-gate-inseguro.log` — log del build #6 rechazado por el gate
- [archivo] `agente-iac/docs/fase-15.md` — 6 comprobaciones PASS y hallazgo del build #5

## Métricas
- recursos_terraform: 15
- pruebas_unitarias: 93
- sli_pipeline_pct: 50.0
- slo_pipeline_pct: 90.0

## Riesgos y pendientes
- La prueba usa el árbol de trabajo local, no el código de un PR
- El SLI baja a 50 % por tres builds malos (dos defectos corregidos y una prueba negativa deliberada)
- Un solo recurso inseguro probado, no cada control por separado

## Siguiente paso
Separar solicitante y aprobador en Jenkins y planificar el staging (S5).
