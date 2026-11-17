# Sesión 18 – Jenkins desde Git y lanzamientos automáticos tras el merge

- **Fecha:** 2026-11-17
- **Fase:** Fase 20
- **Rama:** feature/fase-20-jenkins-desde-git
- **Temas del curso aplicados:** -

## Objetivo
Que Jenkins clone el repositorio de GitHub y lance el pipeline solo tras un merge, deteniéndose en la aprobación manual, y que un staging verificado encole local.

## Qué se agregó
- `agente-iac/specs/005-jenkins-desde-git/spec.md`
- `agente-iac/specs/005-jenkins-desde-git/plan.md`
- `agente-iac/specs/005-jenkins-desde-git/tasks.md`
- `agente-iac/jenkins/casc/jobs.groovy`
- `agente-iac/jenkins/Jenkinsfile`
- `agente-iac/jenkins/Dockerfile`
- `agente-iac/jenkins/plugins.txt`
- `agente-iac/docker-compose.yml`
- `agente-iac/tests/test_jenkins_desde_git.py`
- `agente-iac/docs/fase-20.md`

## Decisiones
- **Polling de Git cada 5 minutos en lugar de webhook** — Jenkins corre en 127.0.0.1 y GitHub no puede alcanzarlo; solo sale a GitHub por HTTPS
- **Encadenar local solo encolándolo, con la compuerta de promoción y la aprobación manual intactas** — la regla 4 exige aprobación humana para cualquier apply
- **Origen del código por REPO_URL y REPO_BRANCH con valores por defecto** — permite probar una rama antes del merge sin tocar el código

## Evidencia
- [commit] `03cdcca` — spec 005 con plan y tareas
- [commit] `3d3663f` — job desde Git, polling y encadenado
- [commit] `8b1eabe` — hallazgos del primer build desde Git
- [commit] `e15a697` — push que disparó el build #33 por polling
- [archivo] `agente-iac/docs/fase-20.md` — builds #30 a #33: línea base, estado perdido, encadenado a local y disparo automático

## Métricas
- recursos_terraform: 21
- pruebas_unitarias: 128

## Riesgos y pendientes
- El estado de Terraform sigue dentro del workspace de Jenkins: el primer clon lo vació y vaciarlo otra vez lo perdería
- El polling necesita un build exitoso desde Git como referencia; antes dijo No changes
- Cualquier commit en la rama lanza un build, incluidos los de documentación
- Un build esperando aprobación bloquea a los siguientes y caduca a los 30 minutos

## Siguiente paso
Comprobar CA-7 (sin commits nuevos no hay builds), fusionar el PR, quitar REPO_BRANCH del .env y mover el estado de Terraform fuera del workspace.
