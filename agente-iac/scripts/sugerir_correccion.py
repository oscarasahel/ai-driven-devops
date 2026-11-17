#!/usr/bin/env python3
"""Propone correcciones a partir de los informes del gate de seguridad (equivalente ligero de la sesión 6:
un fallo en CI dispara una revisión automática que sugiere el arreglo, sin n8n).

Uso (desde agente-iac/): python scripts/sugerir_correccion.py [--reports reports] [--salida archivo.md]
Lee reports/resumen.txt (etapas FAIL) y reports/results_cli.txt (controles de Checkov FAILED).
Imprime Markdown. No modifica el repositorio ni aplica nada: solo sugiere.

Seguridad: los informes derivan de contenido del repo (nombres de recursos, rutas), que es dato no confiable.
Por eso las sugerencias salen de un catálogo fijo (policies/remediaciones.json); del informe solo se
reproduce el id del control, el recurso y el archivo, saneados y dentro de código en línea.
Sale con 0 siempre (la decisión de fallar es del gate, no de este script).
"""
import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "policies" / "remediaciones.json"
MAX_FILAS = 25

CONTROL = re.compile(r"^Check: (?P<id>[A-Z0-9_]+): ", re.M)
FALLO = re.compile(r"^Check: (?P<id>[A-Z0-9_]+): .*\n\tFAILED for resource: (?P<recurso>\S+)\n\tFile: (?P<archivo>\S+)", re.M)
ID_VALIDO = re.compile(r"CKV2?_[A-Z]+_[0-9]+")


def sanear(valor, largo=120):
    """Deja un token seguro para ir dentro de `código en línea` de Markdown."""
    return re.sub(r"[^A-Za-z0-9_./:\-\[\]]", "_", str(valor))[:largo]


def etapas_fallidas(resumen):
    return [l[6:].strip() for l in resumen.splitlines() if l.startswith("FAIL  ")]


def fallos_checkov(texto):
    vistos, salida = set(), []
    for m in FALLO.finditer(texto):
        clave = (m["id"], m["recurso"])
        if clave not in vistos and ID_VALIDO.fullmatch(m["id"]):
            vistos.add(clave)
            salida.append({"id": m["id"], "recurso": m["recurso"], "archivo": m["archivo"]})
    return salida


def generar(reports, catalogo):
    resumen_p, cli_p = Path(reports) / "resumen.txt", Path(reports) / "results_cli.txt"
    resumen = resumen_p.read_text(encoding="utf-8", errors="replace") if resumen_p.exists() else ""
    cli = cli_p.read_text(encoding="utf-8", errors="replace") if cli_p.exists() else ""
    etapas, fallos = etapas_fallidas(resumen), fallos_checkov(cli)

    if not etapas and not fallos:
        return "## Gate de seguridad\nSin fallos que corregir en los informes.\n"

    sal = ["## Sugerencias de corrección del gate de seguridad", ""]
    sal.append("_Generado automáticamente a partir de los informes. Son sugerencias de un catálogo fijo; "
               "no se aplica nada solo: la corrección pasa por el flujo normal (spec, gate, aprobación)._")
    sal.append("")
    if etapas:
        sal.append("### Etapas que fallaron")
        for e in etapas:
            conocida = e in catalogo.get("_etapas", {})
            sug = catalogo["_etapas"][e] if conocida else "Revisa el log del job para esta etapa."
            sal.append(f"- `{e if conocida else 'etapa desconocida'}`: {sug}")
        sal.append("")
    if fallos:
        sal.append(f"### Controles de Checkov fallidos ({len(fallos)})")
        sal.append("| Control | Recurso | Archivo | Sugerencia |")
        sal.append("|---|---|---|---|")
        for f in fallos[:MAX_FILAS]:
            sug = catalogo.get(f["id"], catalogo["_generico"]).replace("|", "/")
            sal.append(f"| `{f['id']}` | `{sanear(f['recurso'])}` | `{sanear(f['archivo'])}` | {sug} |")
        if len(fallos) > MAX_FILAS:
            sal.append(f"\n_... y {len(fallos) - MAX_FILAS} más; ver el informe completo._")
        sal.append("")
    return "\n".join(sal)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reports", default=str(RAIZ / "reports"))
    ap.add_argument("--salida")
    a = ap.parse_args(argv)
    md = generar(a.reports, json.loads(CATALOGO.read_text(encoding="utf-8")))
    if a.salida:
        Path(a.salida).write_text(md, encoding="utf-8")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
