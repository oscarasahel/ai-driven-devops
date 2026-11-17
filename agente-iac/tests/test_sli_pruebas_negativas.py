import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import eventos_pipeline as ep


def _ev(n, outcome):
    return {"trace_id": f"agente-iac-pipeline-{n}", "outcome": outcome}


def _lista(*pares):
    return ep.marcar_negativas([_ev(n, o) for n, o in pares], {6, 12})


def test_la_prueba_negativa_se_excluye_del_sli_pero_no_del_bruto():
    s = ep.calcular_sli(_lista((1, "success"), (2, "success"), (6, "failure"), (3, "failure")))
    assert (s["buenos"], s["malos"], s["excluidos"], s["builds"]) == (2, 1, 1, 3)
    assert s["sli_pct"] == 66.7 and s["sli_bruto_pct"] == 50.0


def test_un_defecto_real_sigue_contando():
    s = ep.calcular_sli(_lista((1, "success"), (5, "failure")))
    assert s["sli_pct"] == s["sli_bruto_pct"] == 50.0 and s["excluidos"] == 0


def test_solo_se_excluye_si_el_build_fallo():
    ev = _lista((6, "success"), (12, "rejected"))
    assert not any(e["prueba_negativa"] for e in ev)
    assert ep.calcular_sli(ev)["sli_pct"] == 100.0


def test_sin_builds_o_solo_negativas():
    assert ep.calcular_sli([])["sli_pct"] is None
    assert ep.calcular_sli(_lista((6, "failure")))["sli_pct"] is None


def test_politica_versionada_declara_los_builds_con_motivo():
    pol = json.loads((RAIZ / "policies" / "builds-prueba-negativa.json").read_text(encoding="utf-8"))
    assert ep.cargar_negativas() == {6, 12, 15, 17}
    assert all(m.strip() for m in pol["builds"].values())


def test_sin_archivo_de_politica_no_excluye_nada(tmp_path):
    assert ep.cargar_negativas(tmp_path / "no-existe.json") == set()
