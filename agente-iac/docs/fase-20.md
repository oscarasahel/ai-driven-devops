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

## Hallazgos de la primera ejecución real (build #30)
- **El polling necesita una línea base.** Con builds anteriores sin revisión de Git, el polling respondía "No changes" y no lanzaba nada. Hizo falta **un primer lanzamiento manual, una sola vez** (el #30); después, un commit nuevo en la rama lo dispara solo.
- **El primer clon vació el workspace y se perdió el estado de Terraform de staging.** El #30 clonó el commit `d7df1c5` desde Git, pasó el gate y el plan y esperó la aprobación, pero el apply falló (`BucketAlreadyExists`, `QueueAlreadyExists`, `ResourceInUseException`, `EntityAlreadyExists`) porque los recursos del #28 seguían en el emulador sin estado que los registrara. Se limpiaron a mano con el AWS CLI, solo los `agente-iac-stg-*`.
- **Riesgo que queda:** el estado de Terraform sigue dentro del workspace de Jenkins; vaciarlo (o un nuevo clon completo) lo vuelve a perder. Mover el estado fuera del workspace queda como mejora.

## Ejecución exitosa desde Git (builds #31 y #32)
- **#31 (staging, `apply`):** clonó `8b1eabe` desde GitHub, gate OK, aprobación manual, apply de 21 recursos, pruebas de humo "TODO OK" (incluida la sección de la spec 004) y promoción habilitada.
- **#32 (local, `apply`):** lo encoló solo el #31 ("Started by upstream project agente-iac build number 31"), pasó la compuerta de promoción ("verificado en staging"), esperó la aprobación manual y terminó en SUCCESS con 21 recursos y "TODO OK".
- Los lanzamientos manuales fueron el #30 (línea base, falló por el estado perdido) y el #31.
- **El polling necesita un build exitoso desde Git como referencia**, no solo uno que haya clonado: tras el #30 (fallido) seguía diciendo "No changes" en 0 ms; tras el #31 (SUCCESS) detectó el push siguiente.

## Disparo automático (build #33)
Un push a la rama (`e15a697`) creó el #33 sin intervención: "Started by an SCM change", `staging` + `apply` por defecto, gate OK y plan **"No changes. Your infrastructure matches the configuration."** (el estado de Terraform se conservó). Se detuvo en la aprobación manual.

## Límites
- Polling, no webhook: hay hasta 5 minutos de retraso.
- Cualquier commit en `main` (incluidos los de documentación) lanza un build; filtrar por rutas queda como mejora.
- Un build esperando aprobación bloquea a los siguientes (`disableConcurrentBuilds`); a los 30 minutos termina abortado.
- Un solo usuario en Jenkins: sigue sin haber separación entre quien solicita y quien aprueba.
- Si el repositorio pasara a privado, haría falta un token de solo lectura inyectado por entorno.
