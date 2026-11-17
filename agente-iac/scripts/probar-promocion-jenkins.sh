#!/usr/bin/env bash
# Prueba de extremo a extremo de la spec 003 en Jenkins (staging aislado + compuerta de promoción).
# Requisitos: emulador y Jenkins arriba y SIN recursos desplegados (0 buckets). Modifica temporalmente
# infra/envs/local/main.tf (comentario) y lo restaura siempre (trap). Deja el emulador limpio al terminar.
# Uso (desde agente-iac/): bash scripts/probar-promocion-jenkins.sh   -> docs/evidencia/jenkins-promocion.log
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
TF="infra/envs/local/main.tf"; COPIA="$(mktemp)"; cp "$TF" "$COPIA"
trap 'cp "$COPIA" "$TF"; rm -f "$COPIA"' EXIT
LOG="docs/evidencia/jenkins-promocion.log"; : > "$LOG"
fallos=0
ok()  { echo "PASS  $1"; }
mal() { echo "FAIL  $1"; fallos=$((fallos + 1)); }
J() { bash scripts/jenkins.sh "$@"; }
buckets() { docker compose run --rm --no-deps -T awscli s3api list-buckets --query 'Buckets[].Name' --output text 2>/dev/null | grep -v '^ Container' | tr '\t' ' '; }

# lanzar <accion> <entorno> <aprobar|sin> -> deja el número en $N y el resultado en $RES; agrega el log a $LOG
lanzar() {
  local salida; salida="$(J disparar "$1" "$2")" || { echo "$salida"; mal "no se pudo lanzar $1 $2"; return 1; }
  N="$(echo "$salida" | sed -nE 's/.*#([0-9]+).*/\1/p')"; echo "== build #$N: $1 en $2"
  if [ "$3" = aprobar ]; then J esperar-aprobacion "$N" >/dev/null && J aprobar "$N" >/dev/null; fi
  RES="$(J esperar-fin "$N")"
  { echo "################ build #$N ($1 en $2) ################"; J log "$N"; } >> "$LOG"
  echo "   $RES"
}
bloqueado() { # el build N falló en la compuerta sin llegar a plan ni aprobación
  echo "$RES" | grep -q '"result":"FAILURE"' && J log "$N" | grep -q "PROMOCIÓN BLOQUEADA" \
    && ! J log "$N" | grep -qE "Plan: [0-9]+ to |Input requested|Apply complete"
}

[ -z "$(buckets)" ] || { echo "El emulador debe estar sin buckets; hay: $(buckets)"; exit 1; }

lanzar apply local sin
bloqueado && ok "CA-2 apply en local sin staging verificado: bloqueado en la compuerta (build #$N)" || mal "CA-2 la compuerta no bloqueó (#$N)"

lanzar apply staging aprobar
echo "$RES" | grep -q '"result":"SUCCESS"' && ok "CA-6 apply en staging pidió aprobación y terminó en SUCCESS (#$N)" || mal "apply staging no terminó bien (#$N)"
b="$(buckets)"
[ "$b" = "agente-iac-stg-artifacts" ] && ok "CA-1 staging creó solo agente-iac-stg-artifacts; local sin cambios" || mal "CA-1 buckets inesperados: '$b'"
J log "$N" | grep -q "TODO OK" && ok "pruebas de humo de staging con el prefijo agente-iac-stg: TODO OK" || mal "pruebas de humo de staging no están en verde"

lanzar apply local aprobar
echo "$RES" | grep -q '"result":"SUCCESS"' && J log "$N" | grep -q "promoción permitida" \
  && ok "CA-3 apply en local permitido tras staging y con aprobación manual (#$N)" || mal "CA-3 apply en local no terminó bien (#$N)"
b="$(buckets)"
{ echo "$b" | grep -q "agente-iac-artifacts"; } && { echo "$b" | grep -q "agente-iac-stg-artifacts"; } \
  && ok "ambos entornos conviven en el emulador: $b" || mal "buckets inesperados tras promover: '$b'"

echo "# cambio de prueba que invalida la promoción" >> "$TF"
lanzar apply local sin
bloqueado && ok "CA-4 un cambio en infra/ invalida la promoción (#$N)" || mal "CA-4 la compuerta no bloqueó tras el cambio (#$N)"
cp "$COPIA" "$TF"

lanzar destroy staging aprobar
echo "$RES" | grep -q '"result":"SUCCESS"' || mal "destroy staging no terminó bien (#$N)"
b="$(buckets)"
[ "$b" = "agente-iac-artifacts" ] && ok "CA-5 destruir staging dejó intacto local ($b)" || mal "CA-5 buckets tras destruir staging: '$b'"
lanzar apply local sin
bloqueado && ok "CA-5 destruir staging revocó la promoción (#$N)" || mal "CA-5 la promoción no se revocó (#$N)"

lanzar destroy local aprobar
[ -z "$(buckets)" ] && ok "limpieza: emulador sin buckets" || mal "limpieza: quedan buckets: $(buckets)"

echo
[ "$fallos" -eq 0 ] && echo "PRUEBA DE PROMOCIÓN EN JENKINS: OK" || echo "PRUEBA DE PROMOCIÓN EN JENKINS: $fallos fallo(s)"
exit $((fallos > 0))
