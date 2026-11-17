#!/usr/bin/env bash
# Cliente mínimo de la API de Jenkins para el job agente-iac (http://127.0.0.1:8080).
# Credenciales: JENKINS_ADMIN_USER / JENKINS_ADMIN_PASSWORD (de agente-iac/.env).
# Uso: bash scripts/jenkins.sh <disparar [apply|destroy]|estado [N]|aprobar [N]|rechazar [N]|log [N]|esperar-aprobacion [N]|esperar-fin [N]>
set -u
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$RAIZ/.env" ] && set -a && . "$RAIZ/.env" && set +a
URL="${JENKINS_URL:-http://127.0.0.1:8080}"
JOB="agente-iac"
AUTH="${JENKINS_ADMIN_USER:-admin}:${JENKINS_ADMIN_PASSWORD:?define JENKINS_ADMIN_PASSWORD}"
JAR="$(mktemp)"; trap 'rm -f "$JAR"' EXIT

api() { curl -fsS -u "$AUTH" -b "$JAR" -c "$JAR" "$@"; }
crumb() { api "$URL/crumbIssuer/api/json" | sed -E 's/.*"crumbRequestField":"([^"]+)","crumb":"([^"]+)".*/\1:\2/'; }
ultimo() { api "$URL/job/$JOB/api/json?tree=lastBuild[number]" | sed -E 's/.*"number":([0-9]+).*/\1/'; }
N="${2:-}"
cmd="${1:-estado}"

case "$cmd" in
  disparar)
    accion="${2:-apply}"
    C="$(crumb)"
    # La primera ejecución no tiene parámetros definidos aún: se usa /build sin parámetros (ACCION=apply).
    if api -H "$C" -X POST "$URL/job/$JOB/buildWithParameters?ACCION=$accion" -o /dev/null 2>/dev/null; then :
    else api -H "$C" -X POST "$URL/job/$JOB/build" -o /dev/null; fi
    sleep 3; echo "disparado build #$(ultimo) (ACCION=$accion)";;
  estado)
    N="${N:-$(ultimo)}"
    api "$URL/job/$JOB/$N/api/json?tree=number,building,result" ; echo
    api "$URL/job/$JOB/$N/wfapi/describe" | tr '{' '\n' | grep -E '"name":"[^"]+","execNode"' | sed -E 's/.*"name":"([^"]+)".*"status":"([^"]+)".*/  \2  \1/' ;;
  esperar-aprobacion)
    N="${N:-$(ultimo)}"
    for _ in $(seq 1 180); do
      if api "$URL/job/$JOB/$N/wfapi/nextPendingInputAction" 2>/dev/null | grep -q '"id"'; then echo "build #$N esperando aprobación"; exit 0; fi
      r="$(api "$URL/job/$JOB/$N/api/json?tree=building,result")"
      echo "$r" | grep -q '"building":false' && { echo "build #$N terminó sin llegar a la aprobación: $r"; exit 1; }
      sleep 5
    done; echo "timeout esperando aprobación"; exit 1;;
  aprobar|rechazar)
    N="${N:-$(ultimo)}"
    C="$(crumb)"
    pid="$(api "$URL/job/$JOB/$N/wfapi/nextPendingInputAction" | sed -E 's/.*"id":"([^"]+)".*/\1/')"
    [ -z "$pid" ] && { echo "no hay aprobación pendiente en #$N"; exit 1; }
    if [ "$cmd" = aprobar ]; then api -H "$C" -X POST "$URL/job/$JOB/$N/input/$pid/proceedEmpty" -o /dev/null && echo "aprobado #$N"
    else api -H "$C" -X POST "$URL/job/$JOB/$N/input/$pid/abort" -o /dev/null && echo "rechazado #$N"; fi;;
  esperar-fin)
    N="${N:-$(ultimo)}"
    for _ in $(seq 1 240); do
      r="$(api "$URL/job/$JOB/$N/api/json?tree=building,result")"
      echo "$r" | grep -q '"building":false' && { echo "$r"; exit 0; }
      sleep 5
    done; echo "timeout"; exit 1;;
  log)
    N="${N:-$(ultimo)}"; api "$URL/job/$JOB/$N/consoleText";;
  *) sed -n 2,5p "$0"; exit 2;;
esac
