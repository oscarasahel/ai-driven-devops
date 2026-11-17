# agente-iac

Prueba de concepto 100 % local (Docker Desktop, sin cuenta AWS) de un agente que convierte un requerimiento en lenguaje natural en Terraform: **spec -> Terraform -> gate de seguridad -> plan -> aprobación humana -> apply en un emulador de AWS -> bitácora y dashboard**.

Reglas del proyecto: [CLAUDE.md](CLAUDE.md) y [docs/constitution.md](docs/constitution.md). Decisiones: [docs/adr/](docs/adr/). Detalle y evidencia de cada fase: `docs/fase-N.md`. Seguridad: [AI-BOM](docs/seguridad/ai-bom.md) y [modelo de amenazas](docs/seguridad/modelo-de-amenazas.md). Operación: [runbooks](docs/runbooks/), [observabilidad](docs/observabilidad.md), [diseño de ChatOps](docs/chatops-diseno.md).

> El repositorio es **público**: no incluye material confidencial del curso (ver "Archivos locales").

## Arranque rápido (PowerShell o Git Bash, desde `agente-iac/`)
```bash
cp .env.example .env                       # solo valores ficticios; .env no se versiona
mkdir -p .data/emulator
docker compose up -d --wait aws-emulator   # emulador AWS (https://127.0.0.1:9297)
docker compose run --rm terraform init
docker compose run --rm terraform plan
docker compose run --rm terraform apply    # pide confirmación
bash scripts/verificar-criterios.sh        # criterios de las specs contra el emulador
docker compose run --rm terraform destroy
```
Otros servicios: `docker compose up -d jenkins` (UI `127.0.0.1:8080`) y `docker compose up -d grafana bitacora-web` (UI `127.0.0.1:3000`). Jenkins comparte la red del emulador: **si el emulador se recrea, recrear también Jenkins** (`docker compose up -d --force-recreate jenkins`).

## Comprobaciones
| Qué | Comando |
|---|---|
| Pruebas unitarias (44) | `pip install -r requirements-dev.txt && python -m pytest -q` |
| Gate de seguridad (fmt, validate, TFLint, Checkov, Trivy) | `bash scripts/seguridad.sh` |
| Validar una spec | `python scripts/validar_spec.py specs/001-bucket-artefactos/spec.md` |
| Evals con resultado esperado (14 rápidos; 16 con el gate) | `bash evals/run_evals.sh [rapido]` |
| Validar la bitácora | `python scripts/bitacora.py validar` |
| Redirección real a la DLQ en el emulador | `bash scripts/probar-dlq.sh` |
| Pipeline de Jenkins (disparar, aprobar, rechazar) | `bash scripts/jenkins.sh disparar apply` ... ver el script |
| Eventos y SLI del pipeline | `python scripts/eventos_pipeline.py` |
| Paneles de Grafana con datos | `python scripts/verificar_dashboard.py` |
| Secretos en el historial | `docker run --rm -v "$PWD/..:/repo" zricethezav/gitleaks:v8.21.2 detect --source /repo --log-opts="--all" --redact` |

CI en GitHub Actions (`.github/workflows/ci.yml`, acciones fijadas por SHA): pytest, Gitleaks sobre todo el historial, gate de seguridad y evals rápidos.

## Flujo y skills (`.claude/skills/`)
1. `analizar-requerimiento` -> `specs/NNN-*/spec.md` (Dado/Cuando/Entonces, validada por `validar_spec.py`), con `plan.md` y `tasks.md`.
2. `construir-iac` -> módulos en `infra/modules/`, entorno en `infra/envs/local/`.
3. `seguridad-iac` -> gate con excepciones documentadas y vencibles en `policies/excepciones.json`.
4. `bitacora` -> `bitacora/` (reales verificables; simuladas aparte y marcadas).
Jenkins (`jenkins/Jenkinsfile`): validate -> lint -> security -> plan -> **aprobación manual** -> apply -> pruebas de humo.

## Estado real frente a los criterios de aceptación globales
| Criterio | Estado |
|---|---|
| `docker compose up` levanta emulador, Jenkins y Grafana sanos | Verificado por separado; los tres a la vez en una sola corrida: **no** |
| Un requerimiento recorre el flujo completo y deja recursos en el emulador | **Verificado en Jenkins** (build #2: gate, plan, aprobación, apply de 15 recursos, pruebas de humo) |
| El pipeline falla ante un recurso inseguro | Verificado en el gate (script, pre-commit y CI). No se probó un recurso inseguro **dentro** de Jenkins |
| No aplica sin aprobación manual | **Verificado:** con el build esperando, el emulador estaba vacío; un destroy rechazado (#3) terminó ABORTED sin cambios (`docs/fase-10.md`) |
| Bitácora y dashboard reflejan cada sesión con evidencia | Verificado: 9 paneles devuelven datos; aspecto visual no revisado |
| Sin secretos; versiones fijadas | Gitleaks sin hallazgos en todo el historial. Excepciones: RPM del emulador `LTS/latest` y plugins de Jenkins sin fijar |

## Límites conocidos
- Emulador: sin tabla de fidelidad publicada; Lambda `Invoke` y partes de EC2/VPC no funcionan.
- Los evals no ejecutan el LLM: el comportamiento del modelo ante requerimientos ambiguos o con inyección de prompt **no se prueba automáticamente**.
- Un solo usuario en Jenkins: no hay separación entre quien solicita y quien aprueba.
- Sin protección de rama ni checks requeridos en GitHub (paso manual del dueño del repo).
- SLI del pipeline 75 % con 4 builds (1 fallo por un defecto ya corregido): ver [observabilidad](docs/observabilidad.md).

## Archivos locales (no versionados)
`docs/seguimiento.md` (en la raíz del repo), `bitacora/bitacora.json`, `bitacora/resumen.json`, `bitacora/simuladas.local.json`, `bitacora/temas.local.json`, `bitacora/pipeline-eventos.json` y `.env`. Los cuatro primeros son material confidencial del curso o derivados de él. En un clon nuevo, `python scripts/bitacora.py generar` produce lo que falte.

## Ramas
Una rama por fase (`feature/fase-0-fundacion` ... `feature/fase-12-higiene-y-telemetria`), **apiladas**: cada una parte de la anterior. Para integrar: revisar en orden y fusionar solo la última (contiene todo) o fusionar una a una cambiando la base de cada PR. Nada se fusionó a `main`.
