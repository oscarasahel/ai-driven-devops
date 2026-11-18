# Sesión 17 – Spec 004: bucket de secretos reutilizando secure-bucket

- **Fecha:** 2026-11-17
- **Fase:** Fase 19
- **Rama:** feature/spec-004-bucket-secretos
- **Temas del curso aplicados:** -

## Objetivo
Recorrer el flujo con un requerimiento nuevo (bucket S3 para secretos) reutilizando el módulo secure-bucket, y hacer que analizar-requerimiento cree siempre una rama feature.

## Qué se agregó
- `agente-iac/specs/004-bucket-secretos/spec.md`
- `agente-iac/specs/004-bucket-secretos/plan.md`
- `agente-iac/specs/004-bucket-secretos/tasks.md`
- `agente-iac/infra/envs/local/main.tf`
- `agente-iac/scripts/verificar-criterios.sh`
- `agente-iac/.claude/skills/analizar-requerimiento/SKILL.md`
- `agente-iac/docs/fase-19.md`

## Decisiones
- **Reutilizar secure-bucket sin modificarlo** — ya aporta cifrado, versionado, bloqueo público, ciclo de vida y HTTPS verificados
- **Sin rol IAM en esta spec** — todavía no existe el principal que lo asuma; se hará en una spec posterior
- **Aprobación de la spec delegada por el usuario al agente** — queda registrada en la spec; no la revisó un humano línea a línea

## Evidencia
- [commit] `2a3e317` — regla de rama en analizar-requerimiento
- [commit] `968a620` — spec 004 con plan y tareas
- [commit] `0dba369` — instancia secrets_bucket y criterios de verificación
- [archivo] `agente-iac/docs/fase-19.md` — apply de 21 recursos, TODO OK, plan sin cambios y destroy en el emulador

## Cómo se validó
Spec 004 validada; 8 criterios de aceptación comprobados contra el emulador con verificar-criterios.sh; gate de seguridad en verde.

## Qué acertó y qué falló la IA
- **Acertó:** Aplicó la skill al requerimiento, preguntó lo ambiguo (rol, versiones, KMS) y reutilizó el módulo secure-bucket.
- **Falló:** La primera ejecución en Jenkins (build 28) falló porque mis ediciones dejaron finales de línea CRLF en un script bash; se convirtió a LF.

## Lección aprendida
En Windows hay que escribir con LF explícito; un fallo en Jenkins que no sale en local suele ser de entorno.

## Métricas
- recursos_terraform: 21

## Riesgos y pendientes
- S3 es un almacén débil para secretos frente a Secrets Manager o SSM; el bucket se despliega vacío
- No se ejecutó en Jenkins: aprobación manual y pruebas de humo pendientes (T8)
- Tras seguridad.sh hay que repetir terraform init

## Siguiente paso
Ejecutar la spec 004 en Jenkins con aprobación manual; spec del rol IAM cuando exista el principal.
