#!/usr/bin/env bash
# Cliente mínimo de la API de Jenkins para el job agente-iac (http://127.0.0.1:8080).
# Credenciales: JENKINS_ADMIN_USER / JENKINS_ADMIN_PASSWORD (de agente-iac/.env).
# Uso: bash scripts/jenkins.sh <disparar [apply|destroy] [staging|local] | estado [N] | esperar-aprobacion [N] |
#                               aprobar [N] | rechazar [N] | esperar-fin [N] | log [N]>
# No depende del plugin pipeline-stage-view: el id de la aprobación se lee del formulario de /input/.
set -u
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$RAIZ/.env" ] && set -a && . "$RAIZ/.env" && set +a
URL="${JENKINS_URL:-http://127.0.0.1:8080}"
JOB="agente-iac"
AUTH="${JENKINS_ADMIN_USER:-admin}:${JENKINS_ADMIN_PASSWORD:?define JENKINS_ADMIN_PASSWORD}"
JAR="$(mktemp)"; trap 'rm -f "$JAR"' EXIT

api() { curl -fsS -u "$AUTH" -b "$JAR" -c "$JAR" "$@"; }
crumb() { # el orden de los campos del JSON no está garantizado
  local j; j="$(api "$URL/crumbIssuer/api/json")"
  echo "$(echo "$j" | sed -nE 's/.*"crumbRequestField":"([^"]+)".*/\1/p'):$(echo "$j" | sed -nE 's/.*"crumb":"([^"]+)".*/\1/p')"
}
ultimo() { api "$URL/job/$JOB/api/json?tree=lastBuild%5Bnumber%5D" | sed -nE 's/.*"number":([0-9]+).*/\1/p'; }
resultado() { api "$URL/job/$JOB/$1/api/json?tree=building,result"; }
pendiente() { # id de la aprobación pendiente del build $1 (vacío si no hay)
  api "$URL/job/$JOB/$1/input/" 2>/dev/null | grep -oE 'action="[A-Za-z0-9]+/submit"' | head -1 | sed -E 's/action="([A-Za-z0-9]+)\/submit"/\1/'
}
cmd="${1:-estado}"
N="${2:-}"

case "$cmd" in
  disparar)
    accion="${2:-apply}"; entorno="${3:-staging}"
    antes="$(ultimo)"; antes="${antes:-0}"
    C="$(crumb)"
    # Con el job recién creado aún no hay parámetros definidos: se cae a /build (ACCION=apply, ENTORNO=staging).
    if ! api -H "$C" -X POST "$URL/job/$JOB/buildWithParameters?ACCION=$accion&ENTORNO=$entorno" -o /dev/null 2>/dev/null; then
      api -H "$C" -X POST "$URL/job/$JOB/build" -o /dev/null
    fi
    for _ in $(seq 1 20); do
      n="$(ultimo)"; [ "${n:-0}" -gt "$antes" ] && { echo "disparado build #$n (ACCION=$accion, ENTORNO=$entorno)"; exit 0; }; sleep 1
    done
    echo "no apareció un build nuevo"; exit 1;;
  estado)
    N="${N:-$(ultimo)}"; resultado "$N"; echo
    [ -n "$(pendiente "$N")" ] && echo "esperando aprobación";;
  esperar-aprobacion)
    N="${N:-$(ultimo)}"
    for _ in $(seq 1 120); do
      [ -n "$(pendiente "$N")" ] && { echo "build #$N esperando aprobación"; exit 0; }
      r="$(resultado "$N")"
      echo "$r" | grep -q '"building":false' && { echo "build #$N terminó sin llegar a la aprobación: $r"; exit 1; }
      sleep 3
    done; echo "timeout esperando aprobación"; exit 1;;
  aprobar|rechazar)
    N="${N:-$(ultimo)}"
    pid="$(pendiente "$N")"
    [ -z "$pid" ] && { echo "no hay aprobación pendiente en #$N"; exit 1; }
    C="$(crumb)"
    if [ "$cmd" = aprobar ]; then
      api -H "$C" -X POST "$URL/job/$JOB/$N/input/$pid/proceedEmpty" -o /dev/null && echo "aprobado #$N"
    else
      api -H "$C" -X POST "$URL/job/$JOB/$N/input/$pid/abort" -o /dev/null && echo "rechazado #$N"
    fi;;
  esperar-fin)
    N="${N:-$(ultimo)}"
    for _ in $(seq 1 120); do
      r="$(resultado "$N")"
      echo "$r" | grep -q '"building":false' && { echo "$r"; exit 0; }
      sleep 3
    done; echo "timeout"; exit 1;;
  log)
    N="${N:-$(ultimo)}"; api "$URL/job/$JOB/$N/consoleText";;
  *) sed -n 2,6p "$0"; exit 2;;
esac
