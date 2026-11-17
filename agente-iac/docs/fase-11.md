# Fase 11 – Runbooks, ChatOps, AI-BOM y modelo de amenazas (2026-11-17)

## Qué se entregó
- `docs/runbooks/`: tres runbooks con la estructura disparador, contexto, diagnóstico de solo lectura, hipótesis, remediación con aprobación y rollback, validación. Dos nacen de incidentes reales (construcción de la imagen de Jenkins; fallos del pipeline) y uno es de revisión previa al apply.
- `docs/chatops-diseno.md`: diseño (no implementado) de ChatOps con comandos por riesgo; ejemplo detallado de `/iac-explain`.
- `docs/seguridad/ai-bom.md`: inventario de modelos, agentes, herramientas y versiones, con las brechas de cadena de suministro.
- `docs/seguridad/modelo-de-amenazas.md`: recorrido de las listas OWASP para LLM y para agentes, con control, evidencia y riesgo residual.
- `specs/00{1,2}-*/plan.md` y `tasks.md`, **reconstruidos a posteriori** y marcados así.
- `scripts/probar-dlq.sh`: prueba de comportamiento de la DLQ en el emulador.

## Verificación real
- Los comandos de diagnóstico del runbook de revisión previa se ejecutaron sobre planes reales (logs de los builds #2 y #4): el plan de apply muestra 15 creaciones y ninguna destrucción; el de destroy, 15 destrucciones.
- `probar-dlq.sh`: tras superar `maxReceiveCount` el mensaje llegó a la DLQ (cierra la tarea T7 de la spec 002; antes solo se comprobaba por atributos).
- Specs válidas y 34 pruebas pasan.

## Límites
- Los runbooks se probaron parcialmente; el de revisión previa no se ejecutó contra un plan destructivo real inesperado.
- ChatOps es solo diseño.
- La numeración OWASP sigue las listas vistas en el curso; verificar contra la versión vigente.
- Las licencias del AI-BOM son las declaradas upstream, sin verificar a fondo.
