# Fase 19 – Spec 004: bucket de secretos reutilizando `secure-bucket` (2026-11-17)

## Qué se hizo
Un requerimiento nuevo recorrió el flujo con las skills: `analizar-requerimiento` -> `construir-iac` -> gate de seguridad -> `apply` en el emulador.

Requerimiento (texto libre): un bucket S3 para secretos de una aplicación, cifrado, versionado, sin acceso público, con objetos que se borran a los 30 días, reutilizando el módulo `secure-bucket`.

| Paso | Resultado |
|---|---|
| Spec | `specs/004-bucket-secretos/spec.md`: 8 criterios Dado/Cuando/Entonces; `validar_spec.py` en OK |
| Preguntas abiertas | 3, resueltas por el usuario: sin rol IAM aún, versiones antiguas 7 días, sin KMS propia |
| Construcción | Una instancia nueva de `secure-bucket` (`secrets_bucket`) en `infra/envs/local/main.tf`; el módulo no cambió |
| Gate de seguridad | PASS en excepciones, fmt, validate, TFLint, Checkov y Trivy; sin excepciones nuevas |
| Emulador | `apply` de 21 recursos; `verificar-criterios.sh` "TODO OK"; segundo plan sin cambios (código 0); `destroy` de 21 recursos |

## Cambio en las skills
`analizar-requerimiento` tiene un paso 0: antes de escribir nada comprueba la rama y, si está en `main` u otra rama base, crea `feature/<cambio>`. Nunca hace commit ni push sin petición.

## Decisiones
- **Reutilizar el módulo sin tocarlo:** menos código y los mismos controles ya verificados.
- **Aprobación de la spec delegada al agente:** queda registrada en la spec; no la revisó un humano línea a línea.
- **Nombre `<prefijo>-secrets`:** funciona con el prefijo de staging de la spec 003.
- **Sin rol IAM:** se pedirá en una spec posterior cuando exista el principal que lo asuma.

## Límites y riesgos
- S3 es un almacén débil para secretos frente a Secrets Manager o SSM Parameter Store; el bucket se despliega vacío y sin valores reales. Secrets Manager no está verificado en el emulador.
- Con versionado, la expiración a 30 días solo crea un marcador de borrado; el borrado definitivo lo hace la regla de versiones no vigentes (7 días).
- No se ejecutó en Jenkins: la aprobación manual y las pruebas de humo de este recurso siguen pendientes (T8 de `tasks.md`).
- Tras ejecutar `scripts/seguridad.sh` hay que repetir `terraform init`: el primer `plan` posterior falló con "Required plugins are not installed".
