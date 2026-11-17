#!/usr/bin/env python3
"""Gestión de la bitácora de sesiones (stdlib, sin dependencias).

Fuentes:
  bitacora/sesiones.json         sesiones REALES (versionado en git)
  bitacora/simuladas.local.json  sesiones SIMULADAS/reconstruidas (local, ignorado por git; opcional)
Salidas:
  bitacora/bitacora.json         unión de ambas, para Grafana (ignorado por git; confidencial)
  bitacora/BITACORA.md           índice de sesiones REALES
  bitacora/sesiones/sesion-NN-<slug>.md   una por sesión real

Comandos:  validar | generar | agregar <archivo.json>
- validar: esquema; toda sesión real debe tener evidencia, y cada commit citado debe existir en git
           y cada archivo citado debe existir. Toda sesión simulada debe llevar simulado=true y no citar commits.
- generar: valida y regenera las salidas.
- agregar: añade una sesión real desde un JSON (la valida primero).
Veracidad: nunca se marca como real una sesión sin evidencia verificable.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REPO = RAIZ.parent  # raíz del repo git: las rutas de evidencia son relativas a ella
B = RAIZ / "bitacora"
REALES = B / "sesiones.json"
SIMULADAS = B / "simuladas.local.json"
SALIDA_JSON = B / "bitacora.json"
SALIDA_MD = B / "BITACORA.md"
REQUERIDOS = ["numero", "fecha", "fase", "tema", "slug", "simulado", "temas_curso", "objetivo",
              "archivos", "decisiones", "evidencia", "metricas", "riesgos", "siguiente"]


def cargar(ruta, defecto):
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else defecto


def commit_existe(sha):
    r = subprocess.run(["git", "-C", str(RAIZ), "cat-file", "-e", f"{sha}^{{commit}}"],
                       capture_output=True)
    return r.returncode == 0


def validar_sesion(s, simulada):
    e = []
    for k in REQUERIDOS:
        if k not in s:
            e.append(f"falta '{k}'")
    if e:
        return e
    if bool(s["simulado"]) != simulada:
        e.append("el campo 'simulado' no coincide con el archivo de origen")
    if simulada:
        if any(ev.get("tipo") == "commit" for ev in s["evidencia"]):
            e.append("una sesión simulada no puede citar commits")
        return e
    if not s["evidencia"]:
        e.append("sesión real sin evidencia")
    for ev in s["evidencia"]:
        if ev.get("tipo") == "commit":
            if not commit_existe(ev.get("ref", "")):
                e.append(f"el commit {ev.get('ref')} no existe en git")
        elif ev.get("tipo") == "archivo":
            if not (REPO / ev.get("ref", "")).exists():
                e.append(f"el archivo {ev.get('ref')} no existe")
    if not any(ev.get("tipo") == "commit" for ev in s["evidencia"]):
        e.append("sesión real sin ningún commit como evidencia")
    return e


def validar():
    reales = cargar(REALES, {"sesiones": []})
    sim = cargar(SIMULADAS, {"sesiones": []})
    errores, numeros = [], set()
    for s in reales["sesiones"]:
        errores += [f"real #{s.get('numero')}: {m}" for m in validar_sesion(s, False)]
        if s.get("numero") in numeros:
            errores.append(f"número duplicado {s.get('numero')}")
        numeros.add(s.get("numero"))
    for s in sim["sesiones"]:
        errores += [f"simulada {s.get('numero')}: {m}" for m in validar_sesion(s, True)]
    return reales, sim, errores


def md_sesion(s):
    L = [f"# Sesión {s['numero']:02d} – {s['tema']}", "",
         f"- **Fecha:** {s['fecha']}", f"- **Fase:** {s['fase']}",
         f"- **Rama:** {s.get('rama', '-')}", f"- **Temas del curso aplicados:** {', '.join(s['temas_curso']) or '-'}", "",
         "## Objetivo", s["objetivo"], "", "## Qué se agregó"]
    L += [f"- `{a}`" for a in s["archivos"]] or ["- (nada)"]
    L += ["", "## Decisiones"]
    L += [f"- **{d['decision']}** — {d['porque']}" for d in s["decisiones"]]
    L += ["", "## Evidencia"]
    for ev in s["evidencia"]:
        L.append(f"- [{ev['tipo']}] `{ev['ref']}`" + (f" — {ev['detalle']}" if ev.get("detalle") else ""))
    L += ["", "## Métricas"] + [f"- {k}: {v}" for k, v in s["metricas"].items()]
    L += ["", "## Riesgos y pendientes"] + [f"- {r}" for r in s["riesgos"]]
    L += ["", "## Siguiente paso", s["siguiente"], ""]
    return "\n".join(L)


def generar():
    reales, sim, errores = validar()
    if errores:
        print("BITÁCORA INVÁLIDA:")
        for m in errores:
            print(f"  - {m}")
        return 1
    (B / "sesiones").mkdir(parents=True, exist_ok=True)
    filas = ["# Bitácora de sesiones (reales)", "",
             "Solo sesiones con evidencia verificable (commit y archivos existentes). Las sesiones simuladas del curso "
             "viven en un archivo local y se distinguen en Grafana.", "",
             "| # | Fecha | Fase | Tema | Rama | Commit |", "|---|---|---|---|---|---|"]
    for s in sorted(reales["sesiones"], key=lambda x: x["numero"]):
        commits = ", ".join(e["ref"] for e in s["evidencia"] if e["tipo"] == "commit")
        archivo = f"sesion-{s['numero']:02d}-{s['slug']}.md"
        (B / "sesiones" / archivo).write_text(md_sesion(s), encoding="utf-8", newline="\n")
        filas.append(f"| {s['numero']} | {s['fecha']} | {s['fase']} | [{s['tema']}](sesiones/{archivo}) | "
                     f"{s.get('rama', '-')} | {commits} |")
    SALIDA_MD.write_text("\n".join(filas) + "\n", encoding="utf-8", newline="\n")
    union = {k: v for k, v in reales.items() if k != "sesiones"}
    union["sesiones"] = reales["sesiones"] + sim["sesiones"]
    SALIDA_JSON.write_text(json.dumps(union, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(f"OK: {len(reales['sesiones'])} reales + {len(sim['sesiones'])} simuladas -> {SALIDA_JSON.name}, {SALIDA_MD.name}")
    return 0


def agregar(ruta):
    nueva = json.loads(Path(ruta).read_text(encoding="utf-8"))
    reales = cargar(REALES, {"sesiones": []})
    errs = validar_sesion(nueva, False)
    if errs:
        print("NO SE AGREGÓ:", *errs, sep="\n  - ")
        return 1
    reales["sesiones"] = [s for s in reales["sesiones"] if s["numero"] != nueva["numero"]] + [nueva]
    REALES.write_text(json.dumps(reales, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return generar()


def main(a):
    if a and a[0] == "validar":
        _, _, errores = validar()
        for m in errores:
            print("  -", m)
        print("OK" if not errores else "INVÁLIDA")
        return 1 if errores else 0
    if a and a[0] == "generar":
        return generar()
    if len(a) == 2 and a[0] == "agregar":
        return agregar(a[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
