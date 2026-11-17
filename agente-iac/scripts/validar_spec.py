#!/usr/bin/env python3
"""Valida que una spec cumpla el contrato de la skill analizar-requerimiento.

Uso: python scripts/validar_spec.py specs/NNN-nombre/spec.md [...]
Sale con 0 si todas son válidas, 1 si alguna falla.
"""
import re
import sys
from pathlib import Path

SECCIONES = [
    "Objetivo", "Alcance", "Fuera de alcance", "Recursos",
    "Criterios de aceptación", "Restricciones", "Compatibilidad con el emulador",
    "Supuestos", "Preguntas abiertas", "Riesgos", "Nivel de aprobación",
]
ESTADOS = {"borrador", "aprobada"}
MAX_PREGUNTAS = 5


def secciones(texto):
    partes = re.split(r"^## +(.+?)\s*$", texto, flags=re.M)
    return {partes[i].strip(): partes[i + 1] for i in range(1, len(partes) - 1, 2)}


def validar(ruta):
    errores = []
    texto = Path(ruta).read_text(encoding="utf-8")

    m = re.search(r"^- \*\*Estado:\*\*\s*(\w+)", texto, flags=re.M)
    if not m or m.group(1) not in ESTADOS:
        errores.append("falta 'Estado' (borrador|aprobada)")

    sec = secciones(texto)
    for s in SECCIONES:
        if s not in sec:
            errores.append(f"falta la sección '{s}'")
        elif not sec[s].strip():
            errores.append(f"la sección '{s}' está vacía")

    ca = sec.get("Criterios de aceptación", "")
    bloques = re.split(r"^\*\*CA-\d+", ca, flags=re.M)[1:]
    if len(bloques) < 3:
        errores.append("se requieren al menos 3 criterios de aceptación (CA-N)")
    for i, b in enumerate(bloques, 1):
        for kw in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^- {kw}\b", b, flags=re.M):
                errores.append(f"CA-{i} no tiene '{kw}'")

    if re.search(r"```|^\s*(resource|provider|module|variable)\s+\"?\w", texto, flags=re.M):
        errores.append("la spec no debe contener código ni HCL")

    preguntas = [l for l in sec.get("Preguntas abiertas", "").splitlines() if l.strip().startswith("-")]
    if len(preguntas) > MAX_PREGUNTAS:
        errores.append(f"más de {MAX_PREGUNTAS} preguntas abiertas")

    return errores


def main(args):
    if not args:
        print(__doc__)
        return 1
    fallo = False
    for ruta in args:
        errs = validar(ruta)
        if errs:
            fallo = True
            print(f"FAIL {ruta}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK   {ruta}")
    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
