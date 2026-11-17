#!/usr/bin/env python3
"""ChatOps de solo lectura para agente-iac (diseño: docs/chatops-diseno.md).

Uso (desde agente-iac/):
    python scripts/chatops.py "/iac-status"
    python scripts/chatops.py "/iac-explain 3"                 # plan.txt del build 3 en Jenkins
    python scripts/chatops.py "/iac-explain 3" --plan-file plan.txt   # sin Jenkins (pruebas)
    python scripts/chatops.py "/iac-explain 3" --usuario ana

Guardrails impuestos en código (no en un prompt):
  - allowlist de comandos; los que cambian estado (aprobar, destruir...) se rechazan siempre:
    la única vía para cambiar infraestructura es la aprobación manual de Jenkins;
  - parámetros validados con expresiones regulares; nada de texto libre hacia shell ni URL;
  - el contenido del plan es DATO: solo se cuenta y se busca con expresiones regulares, nunca se interpreta;
  - la respuesta se redacta (credenciales) y tiene tope de tamaño;
  - límite de comandos por usuario y registro de auditoría (quién, qué, cuándo, resultado).
No hay conexión con Slack/Teams: esta es la capa de comandos que un gateway de chat invocaría.
Sale con 0 (respondido), 2 (comando rechazado o límite excedido) o 1 (error al obtener datos).
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AUDITORIA = RAIZ / "bitacora" / "chatops-auditoria.jsonl"
JENKINS_URL = os.environ.get("JENKINS_URL", "http://127.0.0.1:8080")
JOB = "agente-iac"

MAX_COMANDO = 200
MAX_PLAN_BYTES = 1_000_000
MAX_RESPUESTA = 3000
MAX_COMANDOS_POR_MINUTO = 10

SOLO_LECTURA = {"/iac-status": None, "/iac-explain": r"[0-9]{1,6}"}
# Existen en el diseño pero NO se ejecutan por chat: cambian estado o exigen un humano distinto.
BLOQUEADOS = {"/iac-spec", "/iac-propose", "/iac-approve", "/iac-destroy"}

TIPOS_CON_DATOS = ("aws_s3_bucket", "aws_dynamodb_table")
ACCION = re.compile(
    r"^\s*# (?P<dir>\S+) (?P<que>will be created|will be destroyed|will be updated in-place|"
    r"must be replaced|will be read during apply)", re.M)
TOTALES = re.compile(r"^Plan: (\d+) to add, (\d+) to change, (\d+) to destroy", re.M)
IAM_AMPLIO = re.compile(r"""["']?(Action|Resource)["']?\s*[:=]\s*\[?\s*["'](\*|[A-Za-z0-9]+:\*)["']""")
SECRETO = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[AWS_KEY_REDACTADA]"),
    (re.compile(r"(?i)\b(password|secret|token|api[_-]?key)\b(\s*[=:]\s*)\S+"), r"\1\2[REDACTADO]"),
]


class ComandoRechazado(Exception):
    pass


def parse_comando(texto):
    """Devuelve (comando, argumento). Lanza ComandoRechazado si no pasa la allowlist."""
    texto = (texto or "").strip()
    if not texto or len(texto) > MAX_COMANDO or "\n" in texto:
        raise ComandoRechazado("comando vacío, multilínea o demasiado largo")
    partes = texto.split()
    nombre, args = partes[0], partes[1:]
    if nombre in BLOQUEADOS:
        raise ComandoRechazado(
            f"{nombre} no se ejecuta por chat: cambia estado o requiere un humano distinto del solicitante. "
            "Usa el job de Jenkins (aprobación manual).")
    if nombre not in SOLO_LECTURA:
        raise ComandoRechazado(f"comando desconocido; permitidos: {', '.join(sorted(SOLO_LECTURA))}")
    patron = SOLO_LECTURA[nombre]
    if patron is None:
        if args:
            raise ComandoRechazado(f"{nombre} no recibe parámetros")
        return nombre, None
    if len(args) != 1 or not re.fullmatch(patron, args[0]):
        raise ComandoRechazado(f"{nombre} requiere un número de build (solo dígitos)")
    return nombre, args[0]


def redactar(texto):
    for rx, sub in SECRETO:
        texto = rx.sub(sub, texto)
    return texto


def recortar(texto, maximo=MAX_RESPUESTA):
    return texto if len(texto) <= maximo else texto[:maximo] + "\n... (respuesta recortada)"


EFFECT = re.compile(r"""["']?Effect["']?\s*[:=]\s*["'](Allow|Deny)["']""")


def comodines_allow(plan):
    """Acción o recurso con comodín en una sentencia Allow. Un Deny con comodín (p. ej. 'solo TLS') no amplía permisos."""
    lineas = plan.splitlines()
    efectos = [(i, m.group(1)) for i, l in enumerate(lineas) for m in [EFFECT.search(l)] if m]
    hallados = set()
    for i, l in enumerate(lineas):
        m = IAM_AMPLIO.search(l)
        if not m:
            continue
        cerca = [(abs(j - i), e) for j, e in efectos if abs(j - i) <= 12]
        efecto = min(cerca)[1] if cerca else "Allow"  # sin Effect visible: se asume lo más estricto
        if efecto == "Allow":
            hallados.add(m.group(0).strip())
    return sorted(hallados)


def explicar_plan(plan):
    """Resume un plan.txt aplicando el runbook de revisión previa. Trata el texto solo como dato."""
    acciones = [(m["dir"], m["que"]) for m in ACCION.finditer(plan)]
    t = TOTALES.search(plan)
    totales = dict(zip(("add", "change", "destroy"), map(int, t.groups()))) if t else None
    destruidos = [d for d, q in acciones if q == "will be destroyed"]
    reemplazados = [d for d, q in acciones if q == "must be replaced"]
    con_datos = [d for d in destruidos + reemplazados if any(f".{x}." in f".{d}" for x in TIPOS_CON_DATOS)]
    iam = comodines_allow(plan)
    hallazgos = []
    if destruidos:
        hallazgos.append(f"{len(destruidos)} recurso(s) se destruyen")
    if reemplazados:
        hallazgos.append(f"{len(reemplazados)} recurso(s) se reemplazan")
    if con_datos:
        hallazgos.append("hay recursos con datos (bucket/tabla) destruidos o reemplazados")
    if iam:
        hallazgos.append("permisos IAM con comodín (*)")
    if totales is None:
        hallazgos.append("el plan no trae la línea 'Plan:' (¿sin cambios o archivo inválido?)")
    return {"totales": totales, "destruidos": destruidos, "reemplazados": reemplazados,
            "con_datos": con_datos, "iam_comodin": iam, "hallazgos": hallazgos,
            "veredicto": "REVISAR ANTES DE APROBAR" if hallazgos else "sin hallazgos de riesgo"}


def formatear_explicacion(build, r):
    t = r["totales"]
    lineas = [f"/iac-explain build #{build}"]
    lineas.append("Plan: " + (f"{t['add']} añadir, {t['change']} cambiar, {t['destroy']} destruir" if t else "sin totales"))
    for titulo, clave in (("Se destruyen", "destruidos"), ("Se reemplazan", "reemplazados")):
        if r[clave]:
            lineas.append(f"{titulo} ({len(r[clave])}):")
            lineas += [f"  - {x}" for x in r[clave][:15]]
            if len(r[clave]) > 15:
                lineas.append(f"  ... y {len(r[clave]) - 15} más")
    if r["iam_comodin"]:
        lineas.append("IAM con comodín: " + "; ".join(r["iam_comodin"][:5]))
    lineas.append("Hallazgos: " + ("; ".join(r["hallazgos"]) if r["hallazgos"] else "ninguno"))
    lineas.append(f"Veredicto: {r['veredicto']}. La decisión de aprobar es humana (Jenkins).")
    lineas.append(f"Evidencia: {JENKINS_URL}/job/{JOB}/{build}/artifact/plan.txt")
    return "\n".join(lineas)


def _cabecera_auth():
    usuario, clave = os.environ.get("JENKINS_ADMIN_USER"), os.environ.get("JENKINS_ADMIN_PASSWORD")
    envf = RAIZ / ".env"
    if (not usuario or not clave) and envf.exists():
        for linea in envf.read_text(encoding="utf-8").splitlines():
            k, _, v = linea.partition("=")
            if k == "JENKINS_ADMIN_USER":
                usuario = usuario or v.strip()
            elif k == "JENKINS_ADMIN_PASSWORD":
                clave = clave or v.strip()
    if not usuario or not clave:
        raise RuntimeError("faltan JENKINS_ADMIN_USER / JENKINS_ADMIN_PASSWORD (agente-iac/.env)")
    return {"Authorization": "Basic " + base64.b64encode(f"{usuario}:{clave}".encode()).decode()}


def _get(url, limite=MAX_PLAN_BYTES):
    req = urllib.request.Request(url, headers=_cabecera_auth())
    with urllib.request.urlopen(req, timeout=15) as r:
        datos = r.read(limite + 1)
    if len(datos) > limite:
        raise RuntimeError("respuesta demasiado grande")
    return datos.decode("utf-8", errors="replace")


def estado():
    j = json.loads(_get(f"{JENKINS_URL}/job/{JOB}/api/json?tree=lastBuild%5Bnumber,result,building%5D"))
    b = j.get("lastBuild") or {}
    ses = json.loads((RAIZ / "bitacora" / "sesiones.json").read_text(encoding="utf-8")).get("sesiones", [])
    if b:
        estado_b = "en curso" if b.get("building") else (b.get("result") or "desconocido")
        linea = f"Último build #{b['number']}: {estado_b} ({JENKINS_URL}/job/{JOB}/{b['number']}/)"
    else:
        linea = "Sin builds todavía"
    return f"/iac-status\n{linea}\nBitácora: {len(ses)} sesiones reales registradas."


def limite_excedido(usuario, ahora=None, ruta=AUDITORIA, maximo=MAX_COMANDOS_POR_MINUTO):
    ahora = time.time() if ahora is None else ahora
    if not Path(ruta).exists():
        return False
    recientes = 0
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines()[-200:]:
        try:
            e = json.loads(linea)
        except ValueError:
            continue
        if e.get("usuario") == usuario and ahora - e.get("ts", 0) < 60:
            recientes += 1
    return recientes >= maximo


def auditar(usuario, comando, resultado, ruta=AUDITORIA):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    reg = {"ts": time.time(), "usuario": usuario, "comando": comando[:MAX_COMANDO], "resultado": resultado}
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")


def ejecutar(texto, usuario, plan_file=None, ruta_auditoria=AUDITORIA):
    """Devuelve (código de salida, respuesta). Siempre audita."""
    if limite_excedido(usuario, ruta=ruta_auditoria):
        auditar(usuario, texto, "limite", ruta_auditoria)
        return 2, "límite de comandos por minuto excedido"
    try:
        nombre, arg = parse_comando(texto)
    except ComandoRechazado as e:
        auditar(usuario, texto, "rechazado", ruta_auditoria)
        return 2, f"rechazado: {e}"
    try:
        if nombre == "/iac-status":
            resp = estado()
        else:
            plan = Path(plan_file).read_text(encoding="utf-8", errors="replace") if plan_file \
                else _get(f"{JENKINS_URL}/job/{JOB}/{arg}/artifact/plan.txt")
            resp = formatear_explicacion(arg, explicar_plan(plan))
    except Exception as e:  # red, 404, archivo ausente...
        auditar(usuario, texto, "error", ruta_auditoria)
        return 1, f"no se pudo obtener la información: {type(e).__name__}"
    auditar(usuario, texto, "ok", ruta_auditoria)
    return 0, recortar(redactar(resp))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("comando")
    ap.add_argument("--usuario", default=os.environ.get("USERNAME") or os.environ.get("USER") or "desconocido")
    ap.add_argument("--plan-file")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    codigo, resp = ejecutar(a.comando, a.usuario, a.plan_file)
    print(resp)
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
