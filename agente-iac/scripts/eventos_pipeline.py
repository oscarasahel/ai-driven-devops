#!/usr/bin/env python3
"""Convierte el historial de builds de Jenkins en eventos estructurados y calcula el SLI del pipeline.

Uso (desde agente-iac/, con Jenkins arriba):  python scripts/eventos_pipeline.py
Lee JENKINS_ADMIN_USER / JENKINS_ADMIN_PASSWORD del entorno o de agente-iac/.env.
Escribe bitacora/pipeline-eventos.json (ignorado por git) para Grafana.

Evento (un "wide event" por build): trace_id, service, operation, outcome, duration_ms, started_at, build_url.
SLI: proporción de builds "buenos" = success + rejected (un rechazo humano es una decisión correcta, no una falla).
     Builds "malos" = failure. Los que siguen en curso no cuentan.
SLO por defecto: 90 %. Con pocos builds el SLI es muy sensible: ver el campo "builds".
"""
import base64
import datetime
import json
import os
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "bitacora" / "pipeline-eventos.json"
SERVICIO = "agente-iac-pipeline"
SLO_PCT = 90.0


def a_evento(build, url_job):
    """Traduce un build de la API de Jenkins a un evento estructurado."""
    params = {p["name"]: p["value"] for a in build.get("actions", []) for p in a.get("parameters", [])}
    if build.get("building"):
        outcome = "running"
    else:
        outcome = {"SUCCESS": "success", "ABORTED": "rejected", "FAILURE": "failure"}.get(build.get("result"), "unknown")
    inicio = datetime.datetime.fromtimestamp(build["timestamp"] / 1000, tz=datetime.timezone.utc)
    return {
        "trace_id": f"{SERVICIO}-{build['number']}",
        "service": SERVICIO,
        "operation": params.get("ACCION", "apply"),
        "outcome": outcome,
        "duration_ms": build.get("duration", 0),
        "started_at": inicio.strftime("%Y-%m-%d %H:%M:%S"),
        "build_url": f"{url_job}/{build['number']}/",
    }


def calcular_sli(eventos, slo_pct=SLO_PCT):
    """SLI = (success + rejected) / (success + rejected + failure). Devuelve una fila lista para Grafana."""
    buenos = sum(1 for e in eventos if e["outcome"] in ("success", "rejected"))
    malos = sum(1 for e in eventos if e["outcome"] == "failure")
    total = buenos + malos
    pct = round(100.0 * buenos / total, 1) if total else None
    return {"builds": total, "buenos": buenos, "malos": malos, "sli_pct": pct, "slo_pct": slo_pct,
            "cumple_slo": (pct is not None and pct >= slo_pct)}


def _cargar_env():
    ruta = RAIZ / ".env"
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.split("#")[0].strip())


def main():
    _cargar_env()
    base = os.environ.get("JENKINS_URL", "http://127.0.0.1:8080")
    usuario = os.environ.get("JENKINS_ADMIN_USER", "admin")
    clave = os.environ.get("JENKINS_ADMIN_PASSWORD")
    if not clave:
        print("falta JENKINS_ADMIN_PASSWORD", file=sys.stderr)
        return 2
    url_job = f"{base}/job/agente-iac"
    tree = "builds[number,result,building,duration,timestamp,actions[parameters[name,value]]]"
    req = urllib.request.Request(f"{url_job}/api/json?tree={tree.replace('[', '%5B').replace(']', '%5D')}")
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{usuario}:{clave}".encode()).decode())
    try:
        datos = json.load(urllib.request.urlopen(req, timeout=15))
    except Exception as e:  # noqa: BLE001 - mensaje claro para el operador
        print(f"no se pudo leer Jenkins en {base}: {e}", file=sys.stderr)
        return 1
    eventos = sorted((a_evento(b, url_job) for b in datos.get("builds", [])), key=lambda e: e["trace_id"])
    resumen = {"eventos": eventos, "sli": [calcular_sli(eventos)]}
    SALIDA.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(f"OK: {len(eventos)} eventos; SLI={resumen['sli'][0]['sli_pct']}% (SLO {SLO_PCT}%) -> {SALIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
