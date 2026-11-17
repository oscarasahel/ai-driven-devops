# Fase 13 – ChatOps de solo lectura, sugerencias de corrección en CI y evals con modelo (2026-11-17)

## Qué se entregó
- **S14 – ChatOps:** `scripts/chatops.py` con `/iac-status` y `/iac-explain <build>`. Allowlist en código, parámetros validados, contenido del plan tratado como dato, credenciales redactadas, tope de respuesta, límite por usuario y auditoría. Los comandos que cambian estado se rechazan siempre. No hay conexión con un canal de chat (ver `docs/chatops-diseno.md`).
- **S6 – revisión automática en CI (sin n8n):** si el job del gate falla, el nuevo job `sugerencias` descarga los informes, ejecuta `scripts/sugerir_correccion.py` y publica la corrección sugerida en el resumen del job (y como comentario si es un PR del mismo repo). Las sugerencias salen de un catálogo fijo (`policies/remediaciones.json`); lo que dice el informe se sanea y nunca se copia como instrucción.
- **S7 – evals que ejecutan el modelo:** `scripts/evals_modelo.py` + `evals/modelo/casos.json`: requerimiento ambiguo, con inyección de prompt y no soportado por el emulador. Comprueban la spec devuelta con reglas objetivas (validador, estado, credenciales, HCL, palabras clave).
- 46 pruebas nuevas (90 en total).

## Verificación real
- `/iac-explain 2` y `/iac-explain 3` sobre los `plan.txt` reales de Jenkins: #2 sin hallazgos; #3 "REVISAR" (15 destroys, recursos con datos). Un falso positivo propio (un `Deny` con `s3:*` de "solo TLS" se marcaba como IAM amplio) apareció al probar con datos reales y se corrigió.
- Comandos hostiles (`/iac-explain 3; rm -rf /`, `../../x`, `/iac-approve 3`): rechazados y auditados; el límite por minuto se activó en la prueba.
- `sugerir_correccion.py` sobre los informes reales de un recurso inseguro (4 controles de Checkov): sugerencia correcta para cada uno.
- actionlint 1.7.4 sin avisos sobre el workflow; acciones fijadas por SHA.
- Evals con modelo (CLI `claude -p`, sin herramientas): ver resultados abajo.
- Mutaciones: 5 roturas deliberadas del código nuevo fueron detectadas por las pruebas.

## Resultados de los evals con modelo
Primera corrida, 3 casos: 3 de 3 pasan (en las specs: borrador, sin credenciales, intento de inyección registrado en Riesgos, Lambda `Invoke` y EC2/VPC señalados como no soportados). Repetí el caso de inyección 3 veces más: 3 de 3 (6 de 6 corridas en total; ver `docs/evidencia/evals-modelo.md`).

## Límites
- Los evals con modelo son **no deterministas** y **locales** (no corren en CI: exigirían una credencial del modelo en el repositorio). Prueban las instrucciones de la skill y el modelo, no todo el harness de Claude Code. Son pocos casos: no demuestran robustez, solo detectan regresiones groseras.
- El job `sugerencias` se validó con actionlint y con informes reales, **pero** su ejecución en GitHub depende de que el gate falle; ver el estado en el cierre de esta fase.
- ChatOps: solo la capa de comandos. Sin gateway ni identidad real; solicitante y aprobador siguen siendo el mismo usuario `admin` en Jenkins.
