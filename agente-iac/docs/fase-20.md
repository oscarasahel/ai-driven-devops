# Fase 20 – Jenkins desde Git y lanzamientos automáticos (2026-11-17)

## Qué es
Spec 005. Hasta ahora Jenkins leía la carpeta local del equipo (`./:/repo:ro`) y el pipeline se lanzaba a mano con `scripts/jenkins.sh disparar`. Ahora el job clona el repositorio de GitHub (rama `main` por defecto) y un polling de 5 minutos lanza el build tras un merge. La aprobación manual no cambia.

## Flujo
`merge en main` -> polling detecta el commit -> build `staging` + `apply` -> gate de seguridad y plan -> **aprobación manual** -> apply -> pruebas de humo -> registro de promoción -> se encola `local` + `apply` -> compuerta de promoción -> **aprobación manual**.

## Qué cambió
| Archivo | Cambio |
|---|---|
| `jenkins/casc/jobs.groovy` | Definición desde Git y `scm('H/5 * * * *')`; origen por `REPO_URL` y `REPO_BRANCH` |
| `jenkins/Dockerfile`, `jenkins/plugins.txt` | `git` en la imagen; plugins `git` 5.11.0, `git-client` 6.7.1 y dependencias fijadas |
| `jenkins/Jenkinsfile` | `Preparar` sin `rsync`; etapa `Encadenar local` |
| `docker-compose.yml` | Variables de origen; sin montaje del código |
| `tests/test_jenkins_desde_git.py` | 8 pruebas (128 en total) |

## Verificado
- Configuración del job en una instancia de Jenkins desechable con la imagen nueva: `GitSCM` con `*/main`, `scriptPath agente-iac/jenkins/Jenkinsfile` y `SCMTrigger H/5 * * * *`.
- `git ls-remote` anónimo desde el contenedor de Jenkins alcanza GitHub (confirma también que el repositorio es público).
- Gate de seguridad: 6 PASS. Gitleaks sobre el historial: sin hallazgos.

## Pendiente (T8 a T10 de `specs/005-jenkins-desde-git/tasks.md`)
- Un build real disparado por el polling, hasta la aprobación, sin ejecutar `jenkins.sh disparar`.
- El encadenado a `local` y que el estado de Terraform se conserve.
- Comprobar que, sin commits nuevos, no se crean builds.
Hasta que `main` tenga el Jenkinsfile nuevo, se prueba recreando Jenkins con `REPO_BRANCH=feature/fase-20-jenkins-desde-git` en `.env`.

## Límites
- Polling, no webhook: hay hasta 5 minutos de retraso.
- Cualquier commit en `main` (incluidos los de documentación) lanza un build; filtrar por rutas queda como mejora.
- Un build esperando aprobación bloquea a los siguientes (`disableConcurrentBuilds`); a los 30 minutos termina abortado.
- Un solo usuario en Jenkins: sigue sin haber separación entre quien solicita y quien aprueba.
- Si el repositorio pasara a privado, haría falta un token de solo lectura inyectado por entorno.
