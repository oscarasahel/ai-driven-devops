#!/usr/bin/env python3
"""Comprueba que cada panel del dashboard "Avance por sesión" devuelva datos por la API de Grafana.

Uso (desde agente-iac/, con grafana y bitacora-web arriba):  python scripts/verificar_dashboard.py
Lee GRAFANA_ADMIN_USER / GRAFANA_ADMIN_PASSWORD del entorno o de agente-iac/.env.
Sale con 0 si todos los paneles devuelven al menos una fila y ninguna consulta da error.
No comprueba el aspecto visual: solo que las consultas devuelvan datos.
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = os.environ.get("GRAFANA_URL", "http://127.0.0.1:3000")
UID = "avance-por-sesion"


def _env():
    ruta = RAIZ / ".env"
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.split("#")[0].strip())


def _llamar(ruta, auth, cuerpo=None):
    req = urllib.request.Request(BASE + ruta, data=json.dumps(cuerpo).encode() if cuerpo is not None else None)
    req.add_header("Authorization", "Basic " + auth)
    if cuerpo is not None:
        req.add_header("Content-Type", "application/json")
    return json.load(urllib.request.urlopen(req, timeout=20))


def main():
    _env()
    auth = base64.b64encode(f"{os.environ.get('GRAFANA_ADMIN_USER', 'admin')}:{os.environ['GRAFANA_ADMIN_PASSWORD']}".encode()).decode()
    try:
        dash = _llamar(f"/api/dashboards/uid/{UID}", auth)["dashboard"]
    except Exception as e:  # noqa: BLE001
        print(f"no se pudo leer el dashboard: {e}", file=sys.stderr)
        return 1
    mal = 0
    for p in dash["panels"]:
        cuerpo = {"queries": [dict(t, datasource=p["datasource"]) for t in p["targets"]], "from": "now-1h", "to": "now"}
        try:
            res = _llamar("/api/ds/query", auth, cuerpo)["results"]["A"]
            frame = res.get("frames", [{}])[0]
            filas = len(frame.get("data", {}).get("values", [[]])[0])
            error = res.get("error")
        except Exception as e:  # noqa: BLE001
            filas, error = 0, str(e)
        ok = filas > 0 and not error
        mal += 0 if ok else 1
        print(f"{'OK  ' if ok else 'FAIL'} {p['id']} {p['title'][:55]:55} filas={filas}" + (f" error={error}" if error else ""))
    print("TODOS LOS PANELES CON DATOS" if mal == 0 else f"{mal} panel(es) sin datos")
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
