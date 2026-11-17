# Modelo de amenazas de agente-iac

- **Fecha:** 2026-11-17 · **Método:** recorrer las listas OWASP para aplicaciones con LLM y para aplicaciones agénticas, y decidir para cada riesgo qué control existe **en este repo**, con su evidencia, y qué riesgo residual queda.
- La numeración y los nombres siguen las listas de OWASP vistas en el curso (publicadas en 2026); verificar contra la versión vigente.
- **Activos:** el código y las specs; el entorno local del usuario (el agente ejecuta con sus permisos); la cadena de suministro (imágenes, acciones, plugins); la bitácora y el material confidencial del curso; (en un uso real) la cuenta de AWS.
- **Fronteras de confianza:** el texto de un requerimiento y el contenido de logs/planes son **no confiables**; el repo público es visible para todos; el emulador local no es producción.

## 1. Aplicación con LLM

| Riesgo | Cómo podría darse aquí | Control existente (evidencia) | Residual |
|---|---|---|---|
| LLM01 Inyección de prompt | Un `requerimiento.md` o un log con órdenes ("aplica sin aprobar") | Entrada tratada como dato (skills, `CLAUDE.md`); la spec no admite código (`validar_spec.py`, 34 pruebas); el apply solo ocurre tras aprobación humana en Jenkins (builds #2 a #4); gate en código | **Medio:** el comportamiento del modelo ante inyección no se evalúa automáticamente |
| LLM02 Divulgación de información sensible | Secretos o material del curso en prompts, commits o logs | `.env` y material confidencial ignorados por git; Gitleaks sobre todo el historial (CI); logs de evidencia revisados con Gitleaks | Bajo-medio: el material sale hacia el proveedor del modelo en el contexto de la sesión |
| LLM03 Agencia excesiva | El agente ejecuta comandos destructivos o toca producción | Reglas del repo: una rama por fase, sin tocar `main`, sin producción; infraestructura solo contra un emulador; apply/destroy con aprobación | **Medio:** el agente corre con los permisos del usuario en su equipo |
| LLM04 Cadena de suministro | Imagen, binario, acción o plugin comprometido | Versiones de imagen fijadas; acciones por SHA; ver AI-BOM | **Medio:** tags sin digest, plugins sin fijar, sin verificación de firmas |
| LLM05 Envenenamiento de datos y modelo | Specs o ejemplos manipulados que sesguen al agente | No hay entrenamiento ni RAG; las specs pasan por revisión humana | Bajo |
| LLM06 Consumo sin límite | Ciclos de reintentos o builds sin fin | Máx. 3 reintentos (regla); `timeout` en el pipeline; límites de memoria en contenedores | Bajo: sin presupuesto de uso del modelo |
| LLM07 Desinformación | El agente afirma algo no verificado | Veracidad en código: la bitácora rechaza commits inexistentes; criterios comprobados contra el emulador | Bajo-medio |
| LLM08 Exposición de contexto oculto | Fuga de instrucciones internas | Las instrucciones del repo son públicas por diseño y sin secretos | Bajo |
| LLM09 Debilidades de vectores/embeddings | No aplica | n/a | n/a |
| LLM10 Manejo inseguro de la salida | Terraform o scripts generados ejecutados sin revisión | `fmt`/`validate`/TFLint/Checkov/Trivy antes del plan; revisión del plan antes del apply (runbook) | Bajo-medio |

## 2. Aplicación agéntica

| Riesgo | Cómo podría darse aquí | Control existente | Residual |
|---|---|---|---|
| ASI01 Secuestro del objetivo | Un texto en una spec o log redirige al agente | Spec aprobada como contrato; criterios verificables; humano aprueba | Medio (igual que LLM01) |
| ASI02 Mal uso de herramientas | El agente usa shell/docker/git de forma indebida | Reglas del proyecto; commits pequeños y trazables | **Medio:** sin allowlist técnica de comandos |
| ASI03 Abuso de identidad y privilegios | Credenciales amplias | Solo credenciales del emulador, generadas por él; sin credenciales reales | Bajo en la PoC; **alto** si se conectara una cuenta real |
| ASI04 Cadena de suministro agéntica | Skills, servidores MCP o acciones externas maliciosos | Ningún servidor MCP en el proyecto; skills propias; acciones fijadas por SHA | Medio: el entorno personal puede añadir conectores ajenos |
| ASI05 Ejecución inesperada de código | Scripts o Terraform generados que ejecutan algo no previsto | Gate de seguridad; el pipeline ejecuta solo desde el repo montado en solo lectura | Medio |
| ASI06 Envenenamiento de memoria y contexto | Contenido persistente que condiciona sesiones futuras | `CLAUDE.md` y skills versionados y revisables; sin memoria no versionada del proyecto | Bajo-medio |
| ASI07 Comunicación insegura entre agentes | No hay varios agentes que se comuniquen | n/a | n/a |
| ASI08 Fallas en cascada | Un error se propaga entre fases | Una rama por fase; evals; pipeline con etapas y compuertas | Bajo |
| ASI09 Explotación de la confianza humana | El aprobador aprueba sin leer | El plan se publica como artefacto; runbook de revisión previa; rechazar es gratis y probado | **Medio:** hoy un solo usuario aprueba lo que él mismo solicitó |
| ASI10 Agentes fuera de control | Ejecución sin supervisión | Sin autonomía de producción; aprobación obligatoria; kill switch = detener Jenkins y no conceder credenciales | Medio: no hay auditoría detallada de cada acción del agente |

## 3. Prioridades de mitigación
1. Auditar las acciones del agente (registro de herramientas invocadas) y no solo los commits.
2. Separar solicitante y aprobador en Jenkins (usuarios y roles).
3. Fijar plugins de Jenkins y las imágenes por digest; verificar firmas.
4. Reducir las herramientas conectadas al agente en este proyecto (principio de mínimo privilegio) y/o una allowlist de comandos.
5. Un conjunto de evals que **ejecute el modelo** con requerimientos ambiguos e inyección de prompt.
6. Presupuesto de uso y alertas de consumo.
