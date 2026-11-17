# agente-iac

Prueba de concepto 100 % local (Docker Desktop, sin cuenta AWS) de un agente que convierte un requerimiento en lenguaje natural en Terraform: **spec -> Terraform -> gate de seguridad -> plan -> aprobación humana -> apply en un emulador de AWS -> bitácora y dashboard**.

Reglas del proyecto: [CLAUDE.md](CLAUDE.md) y [docs/constitution.md](docs/constitution.md). Decisiones: [docs/adr/](docs/adr/). Detalle y evidencia de cada fase: `docs/fase-N.md`.

## Arranque rápido (PowerShell o Git Bash, desde `agente-iac/`)
```bash
cp .env.example .env                       # solo valores ficticios; .env no se versiona
mkdir -p .data/emulator
docker compose up -d --wait aws-emulator   # emulador AWS (https://127.0.0.1:9297)
docker compose run --rm terraform init
docker compose run --rm terraform plan
docker compose run --rm terraform apply    # pide confirmación
bash scripts/verificar-criterios.sh        # comprueba los criterios de las specs contra el emulador
docker compose run --rm terraform destroy
```
Otros servicios: `docker compose up -d jenkins` (UI `127.0.0.1:8080`), `docker compose up -d grafana bitacora-web` (UI `127.0.0.1:3000`; antes, `python scripts/bitacora.py generar`).

## Comprobaciones
| Qué | Comando |
|---|---|
| Gate de seguridad (fmt, validate, TFLint, Checkov, Trivy) | `bash scripts/seguridad.sh` |
| Validar una spec | `python scripts/validar_spec.py specs/001-bucket-artefactos/spec.md` |
| Evals con resultado esperado (14 rápidos; 16 con el gate) | `bash evals/run_evals.sh [rapido]` |
| Validar la bitácora | `python scripts/bitacora.py validar` |

## Flujo y skills (`.claude/skills/`)
1. `analizar-requerimiento` -> `specs/NNN-*/spec.md` (Dado/Cuando/Entonces, validada por `validar_spec.py`).
2. `construir-iac` -> módulos en `infra/modules/`, entorno en `infra/envs/local/`.
3. `seguridad-iac` -> gate con excepciones documentadas y vencibles en `policies/excepciones.json`.
4. `bitacora` -> `bitacora/` (reales verificables; simuladas aparte y marcadas).
Jenkins (`jenkins/Jenkinsfile`): validate -> lint -> security -> plan -> **aprobación manual** -> apply -> pruebas de humo.

## Estado real frente a los criterios de aceptación globales
| Criterio | Estado |
|---|---|
| `docker compose up` levanta emulador, Jenkins y Grafana sanos | Verificado por separado (emulador+Jenkins, emulador+Grafana); **no** los tres a la vez en una sola corrida |
| Un requerimiento recorre el flujo completo y deja recursos en el emulador | Verificado **a mano** (apply directo con Terraform, 15 recursos, 29 criterios OK). **No** verificado a través de Jenkins |
| El pipeline falla ante un recurso inseguro | Verificado en el gate (script y pre-commit). **No** verificado dentro de Jenkins |
| No aplica sin aprobación manual | Implementado en el Jenkinsfile y comprobado de forma estática (eval); **sin ejecución real** del `input` |
| Bitácora y dashboard reflejan cada sesión con evidencia | Verificado: consultas de los 7 paneles devuelven datos; aspecto visual no revisado |
| Sin secretos; versiones fijadas | Sin secretos en archivos versionados (eval). Excepciones: el RPM del emulador es `LTS/latest` (se registra la versión efectiva) y los plugins de Jenkins no están fijados |

## Límites conocidos
- Emulador: sin tabla de fidelidad publicada; Lambda `Invoke` y partes de EC2/VPC no funcionan; la redirección real a la DLQ no se probó.
- Los evals no ejecutan el LLM: el comportamiento del modelo ante requerimientos ambiguos o con inyección de prompt **no se prueba automáticamente**. Lo que sí se impone en código: la validación de la spec, el gate, la aprobación en el pipeline y la veracidad de la bitácora.
- `docs/seguimiento.md`, `bitacora/bitacora.json`, `resumen.json` y las sesiones simuladas son material confidencial del curso: locales, ignorados por git.

## Ramas
Una rama por fase (`feature/fase-0-fundacion` ... `feature/fase-8-endurecimiento`), **apiladas**: cada una parte de la anterior. Para integrar: revisar en orden y fusionar solo la última (contiene todo) o fusionar una a una cambiando la base de cada PR. Nada se fusionó a `main`.
