# Guía de presentación

Mapa del proyecto y guion de demo (unos 10 minutos). Todo se ejecuta desde `agente-iac/`; en Git Bash, con `MSYS_NO_PATHCONV=1` si un argumento empieza con `/`.

## 1. Mapa: dónde está cada cosa
| Pieza | Dónde |
|---|---|
| **Agentes (skills)**: analizar requerimiento, construir IaC, seguridad, bitácora | `.claude/skills/` |
| Requerimiento → spec (criterios Dado/Cuando/Entonces) | `specs/001`, `002`, `003`, `004` y `scripts/validar_spec.py` |
| Terraform generado (módulos y entorno) | `infra/modules/`, `infra/envs/local/` |
| Gate de seguridad (fmt, validate, TFLint, Checkov, Trivy) y excepciones | `scripts/seguridad.sh`, `policies/` |
| **Jenkins**: pipeline con aprobación manual | `jenkins/Jenkinsfile`, `jenkins/casc/`, `scripts/jenkins.sh` |
| Staging y promoción a local | `scripts/promocion.py`, `docs/fase-16.md` |
| Observabilidad: SLI/SLO, Grafana, trazas OTLP | `grafana/`, `docs/observabilidad.md`, `scripts/otel_exportar.py` |
| ChatOps de solo lectura y evals con modelo | `scripts/chatops.py`, `evals/` |
| Bitácora de sesiones (real vs simulada) | `bitacora/`, `scripts/bitacora.py` |
| Reglas, riesgos y amenazas | `CLAUDE.md`, `docs/constitution.md`, `docs/seguridad/` |
| Evidencia real | `docs/evidencia/*.log` |

## 2. Antes de presentar (3 comandos)
```bash
docker compose up -d --wait                 # los tres servicios; esperar "healthy"
python -m pytest -q                         # 120 pruebas
python scripts/verificar_dashboard.py       # Grafana: "TODOS LOS PANELES CON DATOS"
```
Si recrean el emulador, recrea Jenkins: `docker compose up -d --force-recreate --wait jenkins`. Credenciales: tu `.env` local.

## 3. Guion de demo
| Min | Qué mostrar | Cómo |
|---|---|---|
| 0-1 | La idea y el flujo | README de la raíz |
| 1-3 | De requerimiento a spec | Abrir `specs/002-eventos-pedidos/requerimiento.md` y `spec.md`; `python scripts/validar_spec.py specs/002-eventos-pedidos/spec.md` |
| 3-4 | Terraform y el gate | `bash scripts/seguridad.sh` (todo PASS) |
| 4-7 | **Jenkins con aprobación manual** | `bash scripts/jenkins.sh disparar apply staging`, abrir `http://127.0.0.1:8080`, ver el plan y pulsar «Aprobar» (o `bash scripts/jenkins.sh aprobar`) |
| 7-8 | Promoción controlada | Intentar `disparar apply local` sin staging: falla en la compuerta (evidencia en `docs/evidencia/jenkins-promocion.log`) |
| 8-9 | El gate rechaza lo inseguro | Abrir `docs/evidencia/jenkins-gate-inseguro.log` (build #6) |
| 9-10 | Grafana, SLI y bitácora | `http://127.0.0.1:3000`, dashboard «Avance por sesión»; `docs/observabilidad.md` |

Para dejar el emulador limpio al terminar: `bash scripts/jenkins.sh disparar destroy staging` y aprobar.

## 4. Qué decir con honestidad
- Es una PoC local: workspaces aíslan el estado, no las credenciales; solicitante y aprobador son la misma persona.
- OpenTelemetry: hay exportación a archivo OTLP/JSON, sin colector ni latencia por etapa.
- El SLI ajustado excluye las pruebas negativas deliberadas (ver `docs/observabilidad.md`); el bruto también se informa.
- Las sesiones «simuladas» de la bitácora son reconstruidas y están marcadas como tales; las reales citan commits verificables.
- Pendiente: colector OTLP real, ChatOps con canal real, evals del modelo en CI, firmas de imágenes.
