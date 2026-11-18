# Cierre del proyecto agente-iac

Resumen para quien revise el repositorio. Todo lo que está aquí sale de registros ya versionados: la [bitácora](../bitacora/BITACORA.md), las fichas por sesión, las specs y los documentos de fase. Las secciones marcadas **Borrador** son reflexiones que debe revisar y completar el autor.

## Qué se construyó

Un flujo local de infraestructura como código dirigido por IA:

requerimiento → spec verificable → Terraform → gate de seguridad → plan → aprobación humana → apply en el emulador de AWS → bitácora y Grafana.

- 5 specs aprobadas (`specs/001` a `005`) con criterios Dado/Cuando/Entonces.
- 4 skills: `analizar-requerimiento`, `construir-iac`, `seguridad-iac` y `bitacora`.
- Jenkins con aprobación manual antes de cualquier apply, staging, compuerta de promoción y lanzamiento automático tras el merge a `main` (polling cada 5 minutos).
- CI en GitHub Actions: pruebas, Gitleaks, gate de seguridad y evals rápidos; `main` protegida por pull request.
- 133 pruebas unitarias y 19 sesiones reales registradas con evidencia.

## Cómo se comprobó cada parte

| Parte | Cómo se comprobó | Dónde está la evidencia |
|---|---|---|
| Specs | Validador en código, con pruebas | `scripts/validar_spec.py`, sesión 2 |
| Recursos | Criterios de aceptación contra el emulador | `scripts/verificar-criterios.sh`, sesiones 3, 17 y 18 |
| Seguridad | TFLint, Checkov y Trivy; excepciones con vencimiento | `docs/seguridad/`, sesión 4 |
| Aprobación manual | Builds reales aprobados y rechazados | `docs/evidencia/jenkins-*.log`, sesión 10 |
| Rechazo de lo inseguro | Build real que falla antes de planificar | `docs/evidencia/jenkins-gate-inseguro.log`, sesión 14 |
| Promoción staging → local | Compuerta por huella de `infra/` | `docs/evidencia/jenkins-promocion.log`, sesión 15 |
| Lanzamiento tras el merge | Builds #30 a #38 | `docs/fase-20.md`, sesión 18 |
| Bitácora veraz | El validador exige commits y archivos existentes | `scripts/bitacora.py`, sesión 6 |

## Lo que salió mal y se corrigió

- Sesión 5: el pipeline se escribió pero no se ejecutó entero; se declaró no verificado hasta la sesión 10.
- Sesión 10: el build 1 falló por un defecto en la ruta de rsync.
- Sesión 14: finales de línea que rompían scripts en Jenkins; se fijaron con `.gitattributes`.
- Sesión 17: el build 28 falló por finales de línea CRLF en un script editado en Windows.
- Sesión 18: el primer clon desde Git borró el estado de Terraform y hubo que limpiar recursos de staging; el polling necesitó una línea base exitosa.

## Límites declarados

- El estado de Terraform sigue dentro del workspace de Jenkins: vaciarlo lo pierde.
- Polling, no webhook: hasta 5 minutos de retraso; cada commit a `main` lanza un build, también los de solo documentación.
- Un único usuario en Jenkins: no hay separación entre quien solicita y quien aprueba.
- Todo corre contra un emulador: los workspaces aíslan el estado, no las credenciales ni la cuenta.
- Los evals con modelo son pocos y no deterministas.
- Las trazas OpenTelemetry son un archivo; no hay colector.

## Borrador: evaluación del trabajo con la IA

Pendiente de que el autor la redacte con su criterio. Puntos de partida tomados de las fichas:

- **Dónde ayudó más:** pasar de un requerimiento a una spec con criterios comprobables, y repetir ese camino en las specs 004 y 005.
- **Dónde hubo que corregirla:** defectos propios de entorno (rutas, finales de línea) y afirmaciones sobre pipelines que no se habían ejecutado.
- **Qué controles resultaron decisivos:** la aprobación humana antes del apply, el validador de la bitácora y las pruebas negativas.
- **Qué haría distinto:** _por completar por el autor_.

## Borrador: temas del curso aplicados

El campo `temas_curso` de la bitácora sigue vacío. Los identificadores de los temas se completan cuando el autor indique cuáles corresponden a cada sesión; los nombres se guardan solo en un archivo local ignorado por git.
