# Diseño de ChatOps para agente-iac

- **Estado:** diseño completo; **implementada la capa de comandos de solo lectura** (`scripts/chatops.py`: `/iac-status` y `/iac-explain`, fase 13). **No hay conexión con Slack/Teams/Discord** ni gateway con identidad real, y los comandos L3 (`/iac-spec`, `/iac-propose`, `/iac-approve`, `/iac-destroy`) se **rechazan siempre** en código: la única vía para cambiar infraestructura sigue siendo la aprobación manual en Jenkins. Reutiliza piezas ya verificadas (gate, Jenkins con aprobación, bitácora).

## Idea
Un canal de chat (Slack, Teams o Discord) como interfaz del flujo: pedir una infraestructura, ver el plan y aprobarlo, sin dar al canal acceso directo a nada que cambie estado.

## Arquitectura

```
Canal -> Gateway (identidad, rate limit, allowlist de comandos)
      -> Agente (skills: analizar-requerimiento, construir-iac, seguridad-iac)
      -> Herramientas de SOLO LECTURA (specs, plan.txt, reportes, bitácora)
      -> Aprobación (input de Jenkins, con identidad del aprobador)
      -> Auditoría (bitácora + historial de Jenkins + commits)
```

El único camino que cambia infraestructura es el job de Jenkins, y exige aprobación humana.

## Comandos por riesgo

| Comando | Qué hace | Riesgo / nivel | Quién |
|---|---|---|---|
| `/iac-status` | Estado del último build y de la bitácora | L1, solo lectura | Cualquiera del canal |
| `/iac-explain <build>` | Resume `plan.txt` y marca destroys, replaces y permisos amplios (runbook de revisión previa) | L2, solo lectura | Cualquiera |
| `/iac-spec <texto>` | Crea una spec **borrador** desde un requerimiento; devuelve la spec y las preguntas abiertas | L2, escribe solo un borrador | Solicitante |
| `/iac-propose <spec>` | Con spec aprobada, genera Terraform en una rama, corre el gate y lanza el pipeline hasta el plan | L3 | Dueño de la spec |
| `/iac-approve <build>` | Aprueba la etapa de Jenkins | L3, humano | Aprobador distinto del solicitante |
| `/iac-destroy <build>` | Lanza un destroy (también con aprobación) | L3, alto impacto | Dueño + guardia |

## Comando de ejemplo en detalle: `/iac-explain <build>`

- **Entrada:** número de build (se valida contra `^[0-9]+$`; nada de texto libre hacia el shell).
- **Qué hace:** descarga el artefacto `plan.txt`, ejecuta las comprobaciones del runbook de revisión previa y responde con: totales (añadir/cambiar/destruir), recursos destruidos o reemplazados, cambios IAM, resultado del gate y enlace al build.
- **Guardrails:** solo lectura; el contenido de `plan.txt` es dato, no instrucciones (puede contener texto controlado por un requerimiento); respuesta con enlace a la evidencia, sin pegar secretos; tope de tamaño de respuesta.
- **Auditoría:** quién preguntó, qué build, cuándo (registro en el gateway).

## Reglas
1. Identidad del solicitante y del aprobador siempre registradas; no pueden ser la misma persona en L3.
2. Allowlist de comandos y de parámetros; sin ejecución de comandos arbitrarios.
3. Mensajes del canal = entrada no confiable (inyección de prompt).
4. Credenciales de vida corta y alcance mínimo por componente; el bot no guarda credenciales de AWS.
5. Kill switch: revocar el token del bot y deshabilitar el job de Jenkins.

## Qué está implementado y qué falta
**Implementado y verificado** (`python scripts/chatops.py "/iac-explain 3"`; en Git Bash anteponer `MSYS_NO_PATHCONV=1`):
- Allowlist de comandos y validación de parámetros (`^[0-9]{1,6}$`); los comandos que cambian estado se rechazan.
- `/iac-explain` lee `plan.txt` del build en Jenkins y aplica el runbook de revisión previa: totales, destroys, replaces, recursos con datos y comodines IAM en sentencias `Allow` (un `Deny` con comodín, como el de "solo TLS", no cuenta). Probado con los planes reales de los builds #2 (crear, sin hallazgos) y #3 (destroy: REVISAR).
- El contenido del plan es dato: solo se cuenta con expresiones regulares.
- Redacción de credenciales, tope de respuesta, límite de 10 comandos por minuto por usuario y registro de auditoría local (`bitacora/chatops-auditoria.jsonl`, ignorado por git).
- 30 pruebas unitarias (`tests/test_chatops.py`).

**Falta:** un gateway de chat (app token, verificación de firma de las peticiones, identidad real del solicitante), separar solicitante y aprobador en Jenkins (hoy solo `admin`) y `/iac-spec`, `/iac-propose`, `/iac-approve` y `/iac-destroy`.
