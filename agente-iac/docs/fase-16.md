# Fase 16 – Staging y promoción controlada (S5, spec 003) (2026-11-17)

## Decisiones (confirmadas por el usuario)
- **Workspaces de Terraform** sobre un único módulo raíz (`infra/envs/local`), en lugar de directorios duplicados: menos que mantener.
- **Aprobación manual en ambos entornos** (staging y local). Solicitante y aprobador son la misma persona en esta PoC; separarlos queda fuera de alcance.
- **Compuerta por contenido**: solo se aplica en `local` el código (huella de `infra/`) ya aplicado y verificado en staging.

## Qué se entregó
- `specs/003-promocion-entornos/` (requerimiento + spec validada por `validar_spec.py`).
- `infra/envs/local/staging.tfvars` (`env=staging`, `name_prefix=agente-iac-stg`).
- `jenkins/Jenkinsfile`: parámetro `ENTORNO` (staging por defecto), etapa «Entorno», «Compuerta de promoción», workspace por entorno y «Registrar promoción».
- `scripts/promocion.py`: huella SHA-256 de `.tf`/`.tf.json`/`.terraform.lock.hcl` de `infra/` (normaliza CRLF; ignora `.tfvars`, estado y `.terraform`); `marcar`, `exigir`, `revocar`. Marcadores en `/var/jenkins_home/promociones`.
- `scripts/verificar-criterios.sh` acepta `NAME_PREFIX` (por defecto `agente-iac`).
- `scripts/jenkins.sh disparar [apply|destroy] [staging|local]`.
- `scripts/probar-promocion-jenkins.sh`: prueba de extremo a extremo; evidencia en `docs/evidencia/jenkins-promocion.log`.
- `tests/test_promocion.py` (8 pruebas, con mutación comprobada sobre la normalización de CRLF).

## Cómo funciona la compuerta
1. Apply en staging aprobado y con pruebas de humo en verde → se guarda un marcador con la huella de `infra/`.
2. Apply en local → `promocion.py exigir` busca ese marcador **antes del plan**; si no existe, el build falla.
3. Cualquier cambio en un `.tf` cambia la huella e invalida la promoción.
4. Destroy de staging revoca todos los marcadores.

## Verificación real
`bash scripts/probar-promocion-jenkins.sh` (builds #12 a #18; log en `docs/evidencia/jenkins-promocion.log`): **10 PASS, 0 FAIL**.

| Criterio | Comprobación | Resultado |
|---|---|---|
| CA-2 | Apply en local sin staging: falla en la compuerta, sin plan ni aprobación (#12) | PASS |
| CA-6 | Apply en staging pide aprobación y termina en SUCCESS (#13) | PASS |
| CA-1 | Staging crea solo `agente-iac-stg-artifacts`; local sin cambios | PASS |
| — | Pruebas de humo con prefijo `agente-iac-stg`: TODO OK | PASS |
| CA-3 | Apply en local permitido tras staging, con aprobación manual (#14) | PASS |
| — | Ambos entornos conviven en el emulador | PASS |
| CA-4 | Un cambio en `infra/` invalida la promoción (#15) | PASS |
| CA-5 | Destruir staging deja local intacto (#16) | PASS |
| CA-5 | Destruir staging revoca la promoción (#17) | PASS |
| — | Limpieza: destroy de local (#18), emulador sin buckets | PASS |

Tras reconstruir Jenkins con los plugins y digests fijados, el build #19 (apply en staging) terminó en SUCCESS y el #20 destruyó staging; emulador sin buckets.

## Límites y riesgos
- Los workspaces aíslan el estado, no las credenciales ni la cuenta: mismo emulador y mismas credenciales.
- La huella solo cubre `infra/`; un cambio en scripts o en el Jenkinsfile no invalida la promoción.
- Recrear el emulador borra ambos entornos y deja marcadores obsoletos (revocar o destruir staging los limpia).
- Hallazgo operativo: tras cambiar los parámetros del Jenkinsfile, el primer build lanzado con parámetros nuevos puede ignorarlos hasta que Jenkins los registre; por eso se ejecutó un build previo.

## Extra: reproducibilidad (plugins y digests)
- `jenkins/plugins.txt` pasa de 5 plugins sin versión a los 65 instalados con su versión exacta (los 5 directos más dependencias).
- Las imágenes de terceros (base de Jenkins, nginx, Grafana, Terraform, AWS CLI) van fijadas por `tag@sha256` en `docker-compose.yml` y `jenkins/Dockerfile`.
- `tests/test_higiene.py` falla si reaparece una imagen sin digest o un plugin sin versión.
- Verificado: la imagen se reconstruyó con los plugins fijados y el pipeline funcionó (build #19, SUCCESS).
- Límite: la imagen del emulador sigue descargando el último RPM publicado (`.../LTS/latest/...`); no se puede fijar sin un RPM versionado. Las imágenes de `tflint` y similares usadas desde `seguridad.sh` están fijadas por tag, no por digest.
- `jenkins.sh disparar` muestra a veces `curl: (22) ... 400` y «no apareció un build nuevo» aunque el build sí se crea (visto en #20 y en los lanzamientos de la prueba); no afectó a los resultados, pero queda como defecto menor del cliente.
- Un solo lanzamiento a la vez: una ejecución anterior que detuve a medias dejó builds entrelazados (#8 a #10) y hubo que abortarlos y limpiar a mano antes de repetir.
