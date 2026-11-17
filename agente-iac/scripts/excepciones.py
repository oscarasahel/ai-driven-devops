#!/usr/bin/env python3
"""Valida policies/excepciones.json y lista los IDs de una herramienta.

Uso: python scripts/excepciones.py <checkov|trivy> [--hoy AAAA-MM-DD]
- checkov: imprime los IDs separados por comas (para --skip-check).
- trivy:   imprime líneas 'ID exp:FECHA' (formato de .trivyignore).
Sale con 1 si una excepción (de cualquier herramienta) no tiene los campos obligatorios,
tiene la justificación vacía o su fecha de revisión ya venció: el gate es todo o nada.
"""
import datetime
import json
import sys
from pathlib import Path

CAMPOS = ("herramienta", "id", "recurso", "justificacion", "revision")
RUTA = Path(__file__).resolve().parent.parent / "policies" / "excepciones.json"


def evaluar(datos, herramienta, hoy):
    """Devuelve (ids, errores): ids=[(id, revision)] de la herramienta; errores=lista de textos."""
    ids, errores = [], []
    for e in datos.get("excepciones", []):
        faltan = [c for c in CAMPOS if not str(e.get(c, "")).strip()]
        if faltan:
            errores.append(f"{e.get('id', '?')}: faltan campos {faltan}")
            continue
        try:
            vence = datetime.date.fromisoformat(e["revision"])
        except ValueError:
            errores.append(f"{e['id']}: fecha de revisión inválida")
            continue
        if vence < hoy:
            errores.append(f"{e['id']}: excepción vencida el {e['revision']}")
            continue
        if e["herramienta"] == herramienta:
            ids.append((e["id"], e["revision"]))
    return ids, errores


def main(argv):
    if not argv or argv[0] not in ("checkov", "trivy"):
        print(__doc__, file=sys.stderr)
        return 2
    herramienta = argv[0]
    hoy = datetime.date.today()
    if "--hoy" in argv:
        hoy = datetime.date.fromisoformat(argv[argv.index("--hoy") + 1])

    datos = json.loads(RUTA.read_text(encoding="utf-8"))
    ids, errores = evaluar(datos, herramienta, hoy)
    if errores:
        for m in errores:
            print(f"EXCEPCIÓN INVÁLIDA {m}", file=sys.stderr)
        return 1
    if herramienta == "checkov":
        print(",".join(i for i, _ in ids))
    else:
        for i, f in ids:
            print(f"{i} exp:{f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
