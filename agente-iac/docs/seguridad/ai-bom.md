# AI-BOM e inventario de componentes de agente-iac

- **Fecha:** 2026-11-17 · **Alcance:** todo lo que interviene en el flujo, con versión y procedencia.
- Las licencias son las declaradas por cada proyecto upstream; **verificarlas antes de redistribuir** este stack.

## 1. Modelos y agentes

| Componente | Detalle | Procedencia | Uso en el proyecto |
|---|---|---|---|
| Modelo de lenguaje | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | Anthropic, vía API gestionada por Claude Code | Asistente de desarrollo: redacta specs, Terraform, scripts y documentación |
| Harness del agente | Claude Code (extensión de VS Code) | Anthropic | Ejecuta herramientas locales (shell, archivos, git) bajo los permisos del usuario |
| Skills (prompts versionados) | `analizar-requerimiento`, `construir-iac`, `seguridad-iac`, `bitacora` | Este repo, `.claude/skills/` | Procedimientos con entradas, pasos y salida |
| Reglas del agente | `CLAUDE.md`, `docs/constitution.md` | Este repo | Restricciones no negociables |
| Pesos propios / fine-tuning / datasets / embeddings | **Ninguno** | n/a | El código no llama a ningún modelo en tiempo de ejecución |

Servidores MCP del proyecto: **ninguno**. (El entorno personal del usuario puede tener otras herramientas conectadas al agente; no forman parte del proyecto, pero amplían su superficie: ver el modelo de amenazas.)

## 2. Infraestructura y herramientas (versiones fijadas salvo lo indicado)

| Componente | Versión | Cómo se obtiene | Licencia (upstream) |
|---|---|---|---|
| AWS Emulator | 1.0.485 (**RPM `LTS/latest`, no fijable**) | Dockerfile propio, `downloads.aws.com` | CC0-1.0 (repo) |
| Terraform | 1.9.8 | Imagen `hashicorp/terraform:1.9.8` | BUSL-1.1 |
| Provider `hashicorp/aws` | 5.100.0 (lock file) | Terraform Registry | MPL-2.0 |
| TFLint | 0.53.0 | `ghcr.io/terraform-linters/tflint:v0.53.0` | MPL-2.0 |
| Checkov | 3.2.255 | `bridgecrew/checkov:3.2.255`; pip en Jenkins | Apache-2.0 |
| Trivy | 0.58.1 | `aquasec/trivy:0.58.1` | Apache-2.0 |
| Gitleaks | 8.21.2 | `zricethezav/gitleaks:v8.21.2` | MIT |
| Jenkins | 2.580.2 LTS (jdk21) | `jenkins/jenkins` | MIT |
| Plugins de Jenkins | **Última versión al construir (sin fijar)** | `jenkins-plugin-cli` | Varias (MIT en su mayoría) |
| AWS CLI | 2.22.0 | zip oficial / `amazon/aws-cli:2.22.0` | Apache-2.0 |
| Grafana OSS | 11.4.0 | `grafana/grafana-oss:11.4.0` | AGPL-3.0 |
| Plugin Infinity | 3.7.1 | `GF_INSTALL_PLUGINS` | Apache-2.0 |
| nginx | 1.27.3-alpine | Imagen oficial | BSD-2-Clause |
| actionlint | 1.7.4 | `rhysd/actionlint:1.7.4` | MIT |
| Python / pytest | 3.12 / 8.3.4 | `requirements-dev.txt` | PSF / MIT |
| Acciones de GitHub | `checkout` v4.2.2, `setup-python` v5.3.0, `upload-artifact` v4.4.3 | **Fijadas por SHA** en `.github/workflows/ci.yml` | MIT |

## 3. Brechas de la cadena de suministro
1. El RPM del emulador no se puede fijar: la versión efectiva se registra en cada sesión (`aws-emulator --version`).
2. Plugins de Jenkins sin fijar (causó un incidente real: ver `docs/runbooks/jenkins-falla-construccion-imagen.md`).
3. Imágenes referenciadas por tag, no por digest: un tag podría reapuntar. Mejora: fijar por digest.
4. No se verifican firmas de imágenes ni de los binarios copiados (cosign/Sigstore).
5. No hay SBOM generado de las imágenes propias (Trivy puede emitirlo).

## 4. Mantenimiento
Actualizar este inventario al cambiar cualquier versión; el job de seguridad y Gitleaks corren en cada push.
