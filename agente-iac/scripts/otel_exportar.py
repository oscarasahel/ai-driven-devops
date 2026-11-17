#!/usr/bin/env python3
"""Convierte bitacora/pipeline-eventos.json (un evento por build) a trazas OTLP/JSON.

Uso: python scripts/otel_exportar.py [--entrada RUTA] [--salida RUTA] [--enviar URL]
Por defecto solo escribe bitacora/trazas-otlp.json (local, ignorado por git). Con --enviar hace POST a un
colector OTLP/HTTP (p. ej. http://localhost:4318/v1/traces); no hay colector en el compose.
Cada build es una traza de un unico span: no hay latencia por etapa (los eventos son por build).
Los textos de los eventos son datos: solo se copian como atributos, nunca se interpretan.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HEX32 = re.compile(r"^[0-9a-f]{32}$")
HEX16 = re.compile(r"^[0-9a-f]{16}$")
SPAN_KIND_INTERNAL = 1
STATUS_OK, STATUS_ERROR = 1, 2


def trace_id(valor):
    """32 hex en minusculas; si el id original no lo es (p. ej. 'agente-iac-pipeline-9'), SHA-256 truncado."""
    v = str(valor).lower()
    if HEX32.match(v) and v != "0" * 32:
        return v
    return hashlib.sha256(str(valor).encode()).hexdigest()[:32]


def span_id(valor, operacion):
    """16 hex deterministas derivados del id de traza y la operacion."""
    return hashlib.sha256(f"{valor}|{operacion}".encode()).hexdigest()[:16]


def a_nanos(texto):
    """'YYYY-MM-DD HH:MM:SS' (UTC, como en los logs de Jenkins) -> nanosegundos epoch."""
    dt = datetime.strptime(str(texto)[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return int(dt.timestamp()) * 1_000_000_000


def attr(clave, valor):
    return {"key": clave, "value": {"stringValue": str(valor)}}


def span(ev):
    inicio = a_nanos(ev["started_at"])
    fin = inicio + max(int(ev.get("duration_ms") or 0), 0) * 1_000_000
    resultado = ev.get("outcome", "")
    # failure = ERROR; success, rejected (control humano funcionando) y running = OK
    estado = STATUS_ERROR if resultado == "failure" else STATUS_OK
    return {
        "traceId": trace_id(ev["trace_id"]),
        "spanId": span_id(ev["trace_id"], ev.get("operation", "")),
        "name": str(ev.get("operation", "pipeline")),
        "kind": SPAN_KIND_INTERNAL,
        "startTimeUnixNano": str(inicio),
        "endTimeUnixNano": str(fin),
        "attributes": [attr("ci.build_url", ev.get("build_url", "")), attr("pipeline.outcome", resultado)],
        "status": {"code": estado},
    }


def convertir(eventos):
    por_servicio = {}
    for ev in eventos:
        por_servicio.setdefault(str(ev.get("service", "agente-iac-pipeline")), []).append(span(ev))
    return {"resourceSpans": [
        {"resource": {"attributes": [attr("service.name", s)]},
         "scopeSpans": [{"scope": {"name": "agente-iac.otel_exportar"}, "spans": spans}]}
        for s, spans in sorted(por_servicio.items())]}


def validar(otlp):
    """Comprueba longitudes y formato; devuelve la lista de problemas (vacia si todo bien)."""
    problemas = []
    for rs in otlp["resourceSpans"]:
        for ss in rs["scopeSpans"]:
            for sp in ss["spans"]:
                if not HEX32.match(sp["traceId"]):
                    problemas.append(f"traceId invalido: {sp['traceId']}")
                if not HEX16.match(sp["spanId"]):
                    problemas.append(f"spanId invalido: {sp['spanId']}")
                if int(sp["endTimeUnixNano"]) < int(sp["startTimeUnixNano"]):
                    problemas.append(f"fin anterior al inicio en {sp['spanId']}")
    return problemas


def cargar_eventos(ruta):
    d = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d.get("eventos", [])


def enviar(otlp, url):
    req = urllib.request.Request(url, data=json.dumps(otlp).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrada", default=str(RAIZ / "bitacora" / "pipeline-eventos.json"))
    ap.add_argument("--salida", default=str(RAIZ / "bitacora" / "trazas-otlp.json"))
    ap.add_argument("--enviar", metavar="URL", help="POST opcional a un colector OTLP/HTTP (/v1/traces)")
    a = ap.parse_args(argv)
    eventos = cargar_eventos(a.entrada)
    otlp = convertir(eventos)
    problemas = validar(otlp)
    if problemas:
        print("\n".join(problemas), file=sys.stderr)
        return 1
    Path(a.salida).write_text(json.dumps(otlp, indent=2), encoding="utf-8")
    print(f"OK: {len(eventos)} trazas -> {a.salida}")
    if a.enviar:
        print(f"enviado a {a.enviar}: HTTP {enviar(otlp, a.enviar)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
