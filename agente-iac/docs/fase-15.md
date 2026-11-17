# Fase 15 – El gate rechaza un recurso inseguro dentro de Jenkins (2026-11-17)

## Qué se entregó
- `scripts/probar-gate-jenkins.sh`: inserta un bucket público en `infra/envs/local/main.tf`, lanza el pipeline, comprueba el resultado y **restaura el archivo siempre** (trap). Deja el log en `docs/evidencia/jenkins-gate-inseguro.log`.
- `.gitattributes` con `* text=auto eol=lf` y `tests/test_higiene.py` que lo vigila.
- Entrada nueva en el runbook del pipeline y nota en `docs/observabilidad.md`.

## Verificación real (build #6)
| Comprobación | Resultado |
|---|---|
| El build termina en FAILURE | PASS |
| El log muestra "GATE DE SEGURIDAD: FALLÓ" | PASS |
| Checkov señala el bucket público (CKV_AWS_20 / CKV2_AWS_6) | PASS |
| Plan, Aprobación manual y Apply quedan omitidos | PASS |
| Sin aprobación pendiente | PASS |
| El emulador sigue sin buckets | PASS |

## Hallazgo: la primera prueba falló por otra causa (build #5)
El build #5 también terminó en FAILURE, pero **no** por el gate: `seguridad.sh` llegó a Jenkins con finales de línea CRLF (`$'\r': command not found`). Jenkins monta el árbol de trabajo de Windows, y Git lo había reconvertido a CRLF al cambiar de rama. Un criterio ingenuo ("el build falló, luego el gate funcionó") lo habría dado por bueno; las comprobaciones sobre el contenido del log lo descartaron. Era un defecto latente del proyecto, no solo de la prueba: cualquier build lanzado tras cambiar de rama en Windows habría fallado. Causa raíz corregida con `.gitattributes`.

## Efectos secundarios
- Al reescribir los archivos con LF, Compose recreó el emulador y Jenkins perdió su red compartida (efecto ya documentado en el runbook); se recreó Jenkins. El script usa ahora `--no-deps` para no tocar el emulador.
- El SLI del pipeline baja a 50 % (6 builds: #1, #5 y #6 malos). #6 es la prueba negativa deliberada, es decir, el control funcionando; el SLI no distingue la etapa del fallo (ver `docs/observabilidad.md`).

## Límites
- La prueba usa el árbol de trabajo local (Jenkins lo monta en solo lectura): no prueba el flujo con el código de un PR.
- Un solo recurso inseguro; no se probó cada control por separado.
