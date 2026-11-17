# Runbook: el pipeline de Jenkins `agente-iac` falla o no avanza

- **Estado:** probado parcialmente con incidentes reales del 2026-11-16/17 (builds #1 y el cliente `jenkins.sh`).
- **Versión:** 0.2 · **Autonomía recomendada:** L2

## 1. Disparador
El build termina en `FAILURE`/`ABORTED`, o queda en "esperando aprobación" más de 30 min, o `scripts/jenkins.sh` devuelve errores HTTP.

## 2. Contexto
Etapas: Preparar -> Validate/lint/seguridad -> Plan -> Aprobación manual -> Apply -> Pruebas de humo. Jenkins comparte la red del emulador (su certificado solo vale para `localhost`/`127.0.0.1`). El repo se monta de solo lectura en `/repo` (que es la carpeta `agente-iac/`).

## 3. Diagnóstico (solo lectura)
1. Qué etapa falló: `bash scripts/jenkins.sh log <N> | grep -vE '^\[Pipeline\]' | tail -40`.
2. Estado: `bash scripts/jenkins.sh estado <N>` (indica si espera aprobación).
3. Salud de las piezas: `docker compose ps`; `docker compose logs --tail 50 jenkins aws-emulator`.
4. Si falla la etapa de seguridad: leer `reports/resumen.txt` en los artefactos del build.

## 4. Hipótesis frecuentes
| Síntoma | Causa conocida | Confirmación |
|---|---|---|
| `rsync ... change_dir "/repo/agente-iac" failed` | Ruta equivocada: `/repo` ya es `agente-iac/` | `docker compose exec jenkins ls /repo` |
| Etapa de seguridad FAIL | Hallazgo nuevo o excepción vencida | `reports/resumen.txt`; `python scripts/excepciones.py checkov` |
| Errores TLS al llamar al emulador | Jenkins no comparte la red del emulador o el emulador se reinició (cambia el certificado) | `docker compose exec jenkins curl -s --cacert /emulator/9297/ca.pem https://127.0.0.1:9297/__admin/health` |
| Jenkins "healthy" pero la UI/API no responde ("connection closed", curl código 000) | Jenkins comparte la red del contenedor del emulador (`network_mode`); si el emulador se **recreó**, Jenkins queda pegado a la red del contenedor anterior | `docker ps --format '{{.Names}} {{.Status}}'`: el emulador es más joven que Jenkins. Remedio: `docker compose up -d --force-recreate jenkins` (ocurrió el 2026-11-17 tras relanzar el emulador) |
| El cliente da HTTP 400/404 | Cabecera crumb mal formada o id de aprobación no reconocido | `curl -u ... /crumbIssuer/api/json`; revisar `scripts/jenkins.sh` |
| Espera aprobación para siempre | Nadie aprobó | `bash scripts/jenkins.sh estado <N>` |

## 5. Remediación (requiere aprobación del dueño)
- Corregir el código o la excepción y volver a lanzar; **máximo 3 reintentos** con diagnóstico, luego escalar con el log.
- Reinicio del emulador: relanzar el build (el certificado se regenera).
- **Nunca** aprobar un plan sin leer `plan.txt`; si hay `destroy` inesperado, rechazar.
- **Rollback:** un `apply` mal aprobado se revierte lanzando `destroy` (con su propia aprobación) o corrigiendo el código y aplicando de nuevo.

## 6. Validación
Build en `SUCCESS` y `scripts/verificar-criterios.sh` en "TODO OK"; tras un destroy, `awscli s3 ls` vacío.
