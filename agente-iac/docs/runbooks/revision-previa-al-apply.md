# Runbook: revisión previa al apply (plan de Terraform que puede destruir algo)

- **Estado:** borrador no probado contra un plan destructivo real; la mecánica de aprobación/rechazo sí se probó (docs/fase-10.md).
- **Versión:** 0.1 · **Autonomía:** L2-L3 (el agente resume el plan y marca riesgos; **solo un humano aprueba**)

## 1. Disparador
Cualquier ejecución del pipeline llega a "Aprobación manual" con un `plan.txt` publicado como artefacto.

## 2. Contexto necesario
`plan.txt` del build, la spec aprobada del cambio, `git diff` del commit, estado de los recursos actuales.

## 3. Diagnóstico (solo lectura)
```
grep -E "^(Plan:|  # .* (will be|must be) )" plan.txt          # resumen y acciones por recurso
grep -nE "will be destroyed|must be replaced|forces replacement" plan.txt
```
Preguntas que hay que poder responder antes de aprobar:
1. ¿Cuántos recursos se añaden, cambian y **destruyen**? ¿Coincide con la spec?
2. ¿Algún recurso con datos (bucket, tabla) aparece como `destroyed` o `replaced`?
3. ¿Algún permiso IAM se amplía (`*` en acciones o recursos)?
4. ¿Cambia algo fuera del alcance de la spec?
5. ¿Pasó el gate de seguridad sin excepciones nuevas o vencidas?

## 4. Hipótesis
Un `forces replacement` suele venir de cambiar un nombre o un atributo inmutable; un destroy inesperado, de renombrar un módulo o recurso (cambia la dirección en el estado).

## 5. Decisión
| Situación | Acción |
|---|---|
| Plan = lo que dice la spec, sin destroys inesperados | Aprobar |
| Destroy o replace sobre datos no previstos | **Rechazar** y corregir (p. ej. `moved` blocks) |
| Cambio de permisos más amplio que la spec | Rechazar |
| Dudas | Rechazar; rechazar es gratis (verificado: el build queda ABORTED y no cambia nada) |

## 6. Validación posterior
Tras aprobar: `terraform plan -detailed-exitcode` posterior en 0 y `scripts/verificar-criterios.sh` en "TODO OK".

## 7. Rollback
Revertir el commit y relanzar el pipeline (con su propia aprobación). Los datos destruidos no se recuperan: de ahí el punto 2 del diagnóstico.
