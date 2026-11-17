# Fase 10 – Pipeline de Jenkins verificado de extremo a extremo (2026-11-17)

Cierra el pendiente de la fase 5. Logs completos en `docs/evidencia/jenkins-build-{2,3,4}.log` (revisados con Gitleaks: sin secretos).

## Resultado real
| Build | Acción | Resultado | Qué demuestra |
|---|---|---|---|
| #1 | apply | FAILURE | Defecto mío: el Jenkinsfile buscaba `/repo/agente-iac` y el compose monta `agente-iac/` como `/repo` |
| #2 | apply | **SUCCESS** | Gate en modo nativo (6 etapas PASS) -> plan (15 a crear) -> **espera aprobación** -> "Approved by admin" -> apply (15 creados) -> pruebas de humo "TODO OK" |
| #3 | destroy | **ABORTED** | "Rejected by admin": el destroy rechazado **no tocó nada** (el bucket siguió en el emulador) |
| #4 | destroy | **SUCCESS** | Destroy aprobado; el emulador quedó vacío |

Mientras el build #2 esperaba la aprobación, el emulador estaba **vacío** (`s3 ls`, `dynamodb list-tables`): sin aprobación no se aplica nada.

## Defectos encontrados y corregidos
1. Ruta de `rsync` en el Jenkinsfile (build #1). Además se excluyen `.env`, `.data` y `.git` de la copia al workspace.
2. `scripts/jenkins.sh`, la causa del 404 de la fase 5: dependía de `wfapi` (plugin `pipeline-stage-view`, no instalado); el `sed` del crumb asumía un orden de campos que Jenkins no garantiza; y la regex del id de aprobación solo admitía hexadecimal minúsculo (había ids como `Abed48...`). Ahora el id se lee del formulario de `/input/`.

## Límites
- Se probó con un solo usuario (`admin`); no hay separación entre quien solicita y quien aprueba.
- El job se recrea desde JCasC al reiniciar Jenkins; el historial de builds vive en el volumen `jenkins_home`.
