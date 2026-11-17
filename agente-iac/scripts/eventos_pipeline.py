#!/usr/bin/env python3
"""Convierte el historial de builds de Jenkins en eventos estructurados y calcula el SLI del pipeline.

Uso (desde agente-iac/, con Jenkins arriba):  python scripts/eventos_pipeline.py
Lee JENKINS_ADMIN_USER / JENKINS_ADMIN_PASSWORD del entorno o de agente-iac/.env.
Escribe bitacora/pipeline-eventos.json (ignorado por git) para Grafana.

Evento (un "wide event" por build): trace_id, service, operation, outcome, duration_ms, started_at, build_url.
SLI: proporción de builds "buenos" = success + rejected (un rechazo humano es una decisión correcta, no una falla).
     Builds "malos" = failure. Los que siguen en curso no cuentan.
Pruebas negativas deliberadas (policies/builds-prueba-negativa.json): su "failure" es el control funcionando.
     Se marcan con prueba_negativa=true y quedan fuera del SLI (sli_pct); sli_bruto_pct las sigue contando.
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
POLITICA = RAIZ / "policies" / "builds-prueba-negativa.json"


def cargar_negativas(ruta=POLITICA):
    """Números de build (int) declarados como prueba negativa deliberada."""
    if not Path(ruta).exists():
        return set()
    return {int(n) for n in json.loads(Path(ruta).read_text(encoding="utf-8")).get("builds", {})}


def marcar_negativas(eventos, negativas):
    """Añade prueba_negativa a cada evento; solo cuenta como tal si además terminó en failure."""
    for e in eventos:
        n = int(e["trace_id"].rsplit("-", 1)[1])
        e["prueba_negativa"] = n in negativas and e["outcome"] == "failure"
    return eventos


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
    """SLI = (success + rejected) / (success + rejected + failure), sin las pruebas negativas deliberadas.

    sli_bruto_pct las incluye como fallos. Devuelve una fila lista para Grafana."""
    def pct(buenos, malos):
        return round(100.0 * buenos / (buenos + malos), 1) if buenos + malos else None
    buenos = sum(1 for e in eventos if e["outcome"] in ("success", "rejected"))
    malos_brutos = sum(1 for e in eventos if e["outcome"] == "failure")
    excluidos = sum(1 for e in eventos if e["outcome"] == "failure" and e.get("prueba_negativa"))
    malos = malos_brutos - excluidos
    sli = pct(buenos, malos)
    return {"builds": buenos + malos, "buenos": buenos, "malos": malos, "excluidos": excluidos,
            "sli_pct": sli, "sli_bruto_pct": pct(buenos, malos_brutos), "slo_pct": slo_pct,
            "cumple_slo": (sli is not None and sli >= slo_pct)}


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
    marcar_negativas(eventos, cargar_negativas())
    resumen = {"eventos": eventos, "sli": [calcular_sli(eventos)]}
    SALIDA.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    f = resumen["sli"][0]
    print(f"OK: {len(eventos)} eventos; SLI={f['sli_pct']}% (bruto {f['sli_bruto_pct']}%, {f['excluidos']} prueba(s) negativa(s) excluida(s); SLO {SLO_PCT}%) -> {SALIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
