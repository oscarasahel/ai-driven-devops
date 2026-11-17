#!/usr/bin/env python3
"""Compuerta de promoción staging -> local por contenido de infra/.

La huella es el SHA-256 de los .tf, .tf.json y .terraform.lock.hcl de infra/ (rutas relativas y contenido,
en orden). Los .tfvars NO entran: staging y local difieren a propósito en ellos. Un apply en staging con
pruebas de humo en verde deja un marcador con esa huella; un apply en local exige que exista.

Uso: python3 scripts/promocion.py huella|marcar|exigir|revocar [--infra infra] [--dir DIRECTORIO]
El directorio de marcadores es $PROMOCIONES_DIR o /var/jenkins_home/promociones (fuera del workspace).
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

SUFIJOS = (".tf", ".tf.json")
EXCLUIDOS = {".terraform"}
DIR_POR_DEFECTO = "/var/jenkins_home/promociones"


def huella(infra):
    raiz = Path(infra)
    if not raiz.is_dir():
        raise SystemExit(f"no existe {infra}")
    h = hashlib.sha256()
    archivos = sorted(
        p for p in raiz.rglob("*")
        if p.is_file() and not (set(p.relative_to(raiz).parts) & EXCLUIDOS)
        and (p.name.endswith(SUFIJOS) or p.name == ".terraform.lock.hcl")
    )
    if not archivos:
        raise SystemExit(f"{infra} no contiene archivos de Terraform")
    for p in archivos:
        h.update(p.relative_to(raiz).as_posix().encode() + b"\0")
        h.update(p.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()


def marcar(infra, directorio):
    d = Path(directorio)
    d.mkdir(parents=True, exist_ok=True)
    hx = huella(infra)
    (d / hx).write_text("staging verificado\n", encoding="utf-8")
    return hx


def exigir(infra, directorio):
    hx = huella(infra)
    return hx, (Path(directorio) / hx).is_file()


def revocar(directorio):
    d = Path(directorio)
    n = 0
    if d.is_dir():
        for f in d.iterdir():
            if f.is_file() and len(f.name) == 64:
                f.unlink()
                n += 1
    return n


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["huella", "marcar", "exigir", "revocar"])
    ap.add_argument("--infra", default="infra")
    ap.add_argument("--dir", default=os.environ.get("PROMOCIONES_DIR", DIR_POR_DEFECTO))
    a = ap.parse_args(argv)
    if a.accion == "huella":
        print(huella(a.infra))
    elif a.accion == "marcar":
        print(f"promoción habilitada para {marcar(a.infra, a.dir)}")
    elif a.accion == "exigir":
        hx, ok = exigir(a.infra, a.dir)
        if not ok:
            print(f"PROMOCIÓN BLOQUEADA: la huella {hx[:12]} no tiene un apply verificado en staging")
            return 1
        print(f"promoción permitida: {hx[:12]} verificado en staging")
    else:
        print(f"{revocar(a.dir)} marcador(es) revocado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
