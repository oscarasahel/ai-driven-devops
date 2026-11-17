import copy
import subprocess

import pytest

import bitacora
from conftest import RAIZ


@pytest.fixture(scope="module")
def sha():
    return subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def _sesion(sha, **cambios):
    s = {"numero": 1, "fecha": "2026-11-16", "fase": "F", "tema": "T", "slug": "t", "simulado": False,
         "temas_curso": ["S1"], "objetivo": "o", "archivos": [],
         "decisiones": [], "evidencia": [{"tipo": "commit", "ref": sha}], "metricas": {},
         "riesgos": [], "siguiente": "x"}
    s.update(cambios)
    return s


def test_sesion_real_valida(sha):
    assert bitacora.validar_sesion(_sesion(sha), False) == []


def test_commit_inexistente_se_rechaza():
    errs = bitacora.validar_sesion(_sesion("deadbee"), False)
    assert any("no existe" in e for e in errs)


def test_real_sin_evidencia_se_rechaza():
    assert bitacora.validar_sesion(_sesion("x", evidencia=[]), False)


def test_real_solo_con_archivo_se_rechaza():
    s = _sesion("x", evidencia=[{"tipo": "archivo", "ref": "agente-iac/README.md"}])
    assert any("ningún commit" in e for e in bitacora.validar_sesion(s, False))


def test_archivo_inexistente_se_rechaza(sha):
    s = _sesion(sha, evidencia=[{"tipo": "commit", "ref": sha}, {"tipo": "archivo", "ref": "no/existe.txt"}])
    assert any("no existe" in e for e in bitacora.validar_sesion(s, False))


def test_falta_campo_requerido(sha):
    s = _sesion(sha)
    del s["objetivo"]
    assert "falta 'objetivo'" in bitacora.validar_sesion(s, False)


def test_simulada_no_puede_citar_commits(sha):
    assert any("commits" in e for e in bitacora.validar_sesion(_sesion(sha, simulado=True), True))


def test_simulada_valida_sin_evidencia():
    assert bitacora.validar_sesion(_sesion("x", simulado=True, evidencia=[]), True) == []


def test_flag_simulado_debe_coincidir_con_el_archivo(sha):
    assert any("no coincide" in e for e in bitacora.validar_sesion(_sesion(sha, simulado=True), False))


def test_resumen_solo_cuenta_temas_de_sesiones_reales(sha):
    union = {"temas_curso": [{"id": "S1", "nombre": "a"}, {"id": "S2", "nombre": "b"}],
             "pipeline": {"estado": "no verificado", "detalle": ""},
             "sesiones": [_sesion(sha, temas_curso=["S1"]),
                          _sesion("x", numero=101, simulado=True, temas_curso=["S2"], evidencia=[])]}
    r = bitacora.resumen(union)
    estados = {t["id"]: t["estado"] for t in r["temas"]}
    assert estados == {"S1": "aplicado", "S2": "pendiente"}
    assert r["totales"][0]["sesiones_simuladas"] == 1


def test_resumen_agrega_hallazgos(sha):
    m = {"hallazgos_antes": {"alta": 2}, "hallazgos_despues": {"alta": 1}}
    union = {"temas_curso": [], "sesiones": [_sesion(sha, metricas=m), _sesion(sha, numero=2, metricas=copy.deepcopy(m))]}
    assert bitacora.resumen(union)["hallazgos"] == [{"severidad": "alta", "antes": 4, "despues": 2}]


def test_md_sesion_incluye_evidencia(sha):
    md = bitacora.md_sesion(_sesion(sha))
    assert sha in md and "# Sesión 01" in md


def test_bitacora_real_del_repo_es_valida():
    _, _, errores = bitacora.validar()
    assert errores == []
