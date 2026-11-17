# ADR-001: Fundación del proyecto

Fecha: 2026-11-16 · Estado: aceptado

## Decisiones
1. **Ubicación:** `agente-iac/` dentro del repo `ai-driven-devops` (carpeta maestra). `docs/seguimiento.md` queda en la raíz del repo.
2. **Entorno:** Docker Desktop en Windows (no WSL2 con Docker Engine como suponía el prompt maestro). Compose y scripts deben funcionar desde PowerShell y contenedores Linux.
3. **Git:** una rama por fase `feature/fase-N-<tema>`; commits convencionales; push a la rama de la fase; merge a main lo decide el humano.
4. **Spec Kit:** no instalado; constitution como archivo plano (`docs/constitution.md`). Se puede adoptar después sin romper estructura.
5. **Emulador:** se construye con Dockerfile propio (no hay imagen publicada), con `--telemetry off` y puerto solo en 127.0.0.1.
6. **Bitácora:** `bitacora.json` no existe aún; fuente temporal `docs/seguimiento.md`. `bitacora.json` queda en `.gitignore` (confidencial) hasta decidir en fase 6.

## Consecuencias
- El RPM del emulador no se puede fijar a versión (`LTS/latest`): se registra la versión efectiva en cada sesión. Excepción consciente al principio de "versiones fijadas".
- Lambda Invoke y parte de EC2/VPC pueden no funcionar: los requerimientos de ejemplo (fase 2) se eligen sobre S3/IAM/DynamoDB/SQS/SNS salvo que la fase 1 demuestre lo contrario.
