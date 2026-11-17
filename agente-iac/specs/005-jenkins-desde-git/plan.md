# Plan técnico – Spec 005 (Jenkins desde Git)

## Enfoque
Cambiar solo la capa de Jenkins: el job clona el repositorio en lugar de leer una carpeta montada, y un polling lo dispara tras un merge. Los módulos de Terraform no cambian.

| Pieza | Cambio | Criterios que cubre |
|---|---|---|
| `jenkins/casc/jobs.groovy` | Definición `cpsScm` (Git, rama `REPO_BRANCH`, por defecto `main`), `scriptPath` en el repo y `scm('H/5 * * * *')` | CA-1, CA-3, CA-7 |
| `jenkins/Dockerfile` y `plugins.txt` | Binario `git`; plugins `git`, `git-client`, `gson-api` y `mina-sshd-api-*` con versión fijada; ya no se copia el Jenkinsfile a la imagen | CA-1 |
| `jenkins/Jenkinsfile` | `Preparar` ya no copia desde `/repo`; etapa nueva `Encadenar local` (solo tras `apply` de staging, `wait: false`) | CA-2, CA-4, CA-5, CA-6 |
| `docker-compose.yml` | Variables `REPO_URL` y `REPO_BRANCH` con valores por defecto; se quita el montaje `./:/repo` | CA-1, CA-9 |
| `tests/test_jenkins_desde_git.py` | Impone en código los valores por defecto, la aprobación, el encadenado y la ausencia de credenciales | CA-1, CA-4 a CA-6, CA-9 |

## Decisiones
- Polling en lugar de webhook: Jenkins corre en `127.0.0.1`; GitHub no puede alcanzarlo. Jenkins solo sale a GitHub por HTTPS.
- `REPO_BRANCH` permite probar una rama antes del merge sin tocar el código; el valor por defecto es `main`.
- Estado de Terraform y marcadores de promoción se conservan: el primero está ignorado por git y el segundo vive fuera del workspace (`/var/jenkins_home/promociones`).
- `Encadenar local` solo encola: la compuerta de promoción y la aprobación manual siguen mandando.

## Riesgos
- Reconstruir la imagen y recrear el contenedor: el volumen `jenkins_home` conserva el historial y el estado.
- Si `main` aún no tiene el Jenkinsfile nuevo, un polling contra `main` lanzaría un build con el pipeline antiguo. Se recrea Jenkins apuntando a la rama de la fase (`REPO_BRANCH`) hasta el merge.
