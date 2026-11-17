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
| Pruebas unitarias (90) | `pip install -r requirements-dev.txt && python -m pytest -q` |
| Gate de seguridad (fmt, validate, TFLint, Checkov, Trivy) | `bash scripts/seguridad.sh` |
| Validar una spec | `python scripts/validar_spec.py specs/001-bucket-artefactos/spec.md` |
| Evals con resultado esperado (14 rápidos; 16 con el gate) | `bash evals/run_evals.sh [rapido]` |
| Validar la bitácora | `python scripts/bitacora.py validar` |
| Redirección real a la DLQ en el emulador | `bash scripts/probar-dlq.sh` |
| Evals que ejecutan el modelo (local, usa la CLI `claude`; no corre en CI) | `python scripts/evals_modelo.py [--caso inyeccion --repeticiones 3]` |
| ChatOps de solo lectura (en Git Bash: `MSYS_NO_PATHCONV=1`) | `python scripts/chatops.py "/iac-explain 3"` · `"/iac-status"` |
| Sugerencias de corrección desde los informes del gate | `python scripts/sugerir_correccion.py` |
| Exportar los eventos del pipeline como trazas OpenTelemetry (OTLP/JSON, S11 mínimo) | `python scripts/otel_exportar.py` (ver `docs/fase-17.md`) |
| Staging y promoción a local en Jenkins (spec 003: apply en staging, compuerta, cambio que invalida, destroy) | `bash scripts/probar-promocion-jenkins.sh` |
| Prueba negativa del gate dentro de Jenkins (inserta un recurso inseguro, lanza el pipeline, restaura) | `bash scripts/probar-gate-jenkins.sh` |
| Pipeline de Jenkins (disparar, aprobar, rechazar) | `bash scripts/jenkins.sh disparar [apply|destroy] [staging|local]` ... ver el script |
| Eventos y SLI del pipeline | `python scripts/eventos_pipeline.py` |
| Paneles de Grafana con datos | `python scripts/verificar_dashboard.py` |
| Secretos en el historial | `docker run --rm -v "$PWD/..:/repo" zricethezav/gitleaks:v8.21.2 detect --source /repo --log-opts="--all" --redact` |

CI en GitHub Actions (`.github/workflows/ci.yml`, acciones fijadas por SHA): pytest, Gitleaks sobre todo el historial, gate de seguridad y evals rápidos; si el gate falla, un job adicional publica sugerencias de corrección en el resumen (y en el PR).

## Flujo y skills (`.claude/skills/`)
1. `analizar-requerimiento` -> `specs/NNN-*/spec.md` (Dado/Cuando/Entonces, validada por `validar_spec.py`), con `plan.md` y `tasks.md`.
2. `construir-iac` -> módulos en `infra/modules/`, entorno en `infra/envs/local/`.
3. `seguridad-iac` -> gate con excepciones documentadas y vencibles en `policies/excepciones.json`.
4. `bitacora` -> `bitacora/` (reales verificables; simuladas aparte y marcadas).
Jenkins (`jenkins/Jenkinsfile`): validate -> lint -> security -> plan -> **aprobación manual** -> apply -> pruebas de humo.

## Estado real frente a los criterios de aceptación globales
| Criterio | Estado |
|---|---|
| `docker compose up` levanta emulador, Jenkins y Grafana sanos | **Verificado:** `down` + un solo `up -d --wait`: los cuatro contenedores `healthy` en 14 s y respondiendo |
| Un requerimiento recorre el flujo completo y deja recursos en el emulador | **Verificado en Jenkins** (build #2: gate, plan, aprobación, apply de 15 recursos, pruebas de humo) |
| Trazas OpenTelemetry del pipeline | **Exportación a archivo OTLP/JSON, sin colector**: no hay visor ni latencia por etapa (un span por build). Ver `docs/fase-17.md` |
| SLI del pipeline | Ventana de 20 builds: bruto 85 %; **ajustado 100 %** (con #1 y #5 aún dentro: 75 % / 93,8 %; excluye pruebas negativas deliberadas, `policies/builds-prueba-negativa.json`) |
| Staging aislado y promoción controlada a `local` | **Verificado en Jenkins** (builds #12 a #18, 10 comprobaciones PASS): compuerta por huella de `infra/`, un cambio la invalida, destruir staging la revoca. Ver `docs/fase-16.md` y `specs/003-promocion-entornos/` |
| El pipeline falla ante un recurso inseguro | **Verificado también dentro de Jenkins** (build #6: el gate rechazó un bucket público; Plan, aprobación y Apply omitidos; emulador sin buckets). Ver `docs/fase-15.md` |
| No aplica sin aprobación manual | **Verificado:** con el build esperando, el emulador estaba vacío; un destroy rechazado (#3) terminó ABORTED sin cambios (`docs/fase-10.md`) |
| Bitácora y dashboard reflejan cada sesión con evidencia | Verificado: 9 paneles devuelven datos; aspecto visual no revisado |
| Sin secretos; versiones fijadas | Gitleaks sin hallazgos en todo el historial. Excepciones: RPM del emulador `LTS/latest` y plugins de Jenkins sin fijar |

## Límites conocidos
- Emulador: sin tabla de fidelidad publicada; Lambda `Invoke` y partes de EC2/VPC no funcionan.
- Los evals deterministas no ejecutan el LLM. Los `evals_modelo.py` sí (ambigüedad, inyección de prompt, requerimiento inviable), pero son locales, no deterministas y de pocos casos: detectan regresiones groseras, no demuestran robustez.
- ChatOps: solo la capa de comandos de solo lectura; sin conexión con un canal de chat (ver [diseño](docs/chatops-diseno.md)).
- Un solo usuario en Jenkins: no hay separación entre quien solicita y quien aprueba.
- `main` está protegida con un ruleset (verificado en la API de GitHub): pull request obligatorio con solo método *merge*, los 4 checks del CI requeridos, sin borrado ni force push. Con 0 aprobaciones requeridas, porque hay un único colaborador.
- SLI del pipeline 75 % con 4 builds (1 fallo por un defecto ya corregido): ver [observabilidad](docs/observabilidad.md).

## Archivos locales (no versionados)
`docs/seguimiento.md` (en la raíz del repo), `bitacora/bitacora.json`, `bitacora/resumen.json`, `bitacora/simuladas.local.json`, `bitacora/temas.local.json`, `bitacora/pipeline-eventos.json`, `bitacora/chatops-auditoria.jsonl` y `.env`. Los cuatro primeros son material confidencial del curso o derivados de él. En un clon nuevo, `python scripts/bitacora.py generar` produce lo que falte.

## Ramas
Las fases 0 a 13 se integraron en `main` con el PR #1 (merge commit `d679087`). Las 14 ramas `feature/fase-N-*` **se conservan a propósito**: la bitácora cita commits por SHA y el CI comprueba que existan, así que no se borran ni se hace squash. El trabajo nuevo va en una rama `feature/*` desde `main`, con PR y los 4 checks en verde.
