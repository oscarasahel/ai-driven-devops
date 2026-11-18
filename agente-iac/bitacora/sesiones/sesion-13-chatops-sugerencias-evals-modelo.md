# Sesión 13 – ChatOps de solo lectura, sugerencias de corrección en CI y evals con modelo

- **Fecha:** 2026-11-17
- **Fase:** Fase 13
- **Rama:** feature/fase-13-chatops-sugerencias-evals-modelo
- **Temas del curso aplicados:** S6, S7, S14

## Objetivo
Cerrar brechas con el curso: implementar la capa de ChatOps de solo lectura, una revisión automática con sugerencias cuando falla el gate en CI, y evals que ejecuten el modelo.

## Qué se agregó
- `agente-iac/scripts/chatops.py`
- `agente-iac/scripts/sugerir_correccion.py`
- `agente-iac/scripts/evals_modelo.py`
- `agente-iac/policies/remediaciones.json`
- `agente-iac/evals/modelo/casos.json`
- `.github/workflows/ci.yml`

## Decisiones
- **Los comandos de ChatOps que cambian estado se rechazan siempre en código** — la única vía para cambiar infraestructura es la aprobación manual de Jenkins
- **Las sugerencias de corrección salen de un catálogo fijo, no del texto del informe** — el informe deriva de contenido del repo (dato no confiable)
- **Los evals con modelo son locales y no corren en CI** — exigirían una credencial del modelo en el repositorio

## Evidencia
- [commit] `ef8aa45` — ChatOps, job de sugerencias y evals con modelo
- [archivo] `agente-iac/docs/fase-13.md` — 90 pruebas, plan real explicado, job probado en GitHub
- [archivo] `agente-iac/docs/evidencia/evals-modelo.md` — 6 de 6 corridas con modelo pasan

## Cómo se validó
90 pruebas unitarias; los comandos que cambian estado se rechazan en código y se probaron; evals con modelo ejecutados en local.

## Qué acertó y qué falló la IA
- **Acertó:** Implementó ChatOps de solo lectura y sugerencias de corrección desde un catálogo fijo, sin usar el texto del informe.
- **Falló:** Los evals con modelo son pocos y no deterministas, y el comentario en PR no se ejercitó porque la prueba fue en una rama sin PR.

## Lección aprendida
Los evals con modelo detectan regresiones groseras; no demuestran robustez.

## Métricas
- recursos_terraform: 15
- pruebas_unitarias: 90

## Riesgos y pendientes
- Los evals con modelo son pocos y no deterministas: detectan regresiones groseras, no demuestran robustez
- ChatOps sin gateway ni identidad real; solicitante y aprobador siguen siendo el mismo usuario en Jenkins
- El comentario en PR del job de sugerencias no se ejercitó (la prueba fue en una rama sin PR)

## Siguiente paso
Revisión humana y decisión sobre la fusión de ramas y el historial público.
