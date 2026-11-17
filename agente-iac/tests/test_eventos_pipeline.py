import eventos_pipeline as ep

URL = "http://j/job/agente-iac"


def _b(n, result, building=False, accion=None, duracion=1000):
    actions = [{"parameters": [{"name": "ACCION", "value": accion}]}] if accion else [{}]
    return {"number": n, "result": result, "building": building, "duration": duracion,
            "timestamp": 1_794_000_000_000, "actions": actions}


def test_evento_estructurado():
    e = ep.a_evento(_b(2, "SUCCESS", accion="destroy"), URL)
    assert e["trace_id"] == "agente-iac-pipeline-2" and e["operation"] == "destroy"
    assert e["outcome"] == "success" and e["build_url"] == URL + "/2/"


def test_sin_parametro_es_apply():
    assert ep.a_evento(_b(1, "FAILURE"), URL)["operation"] == "apply"


def test_mapeo_de_resultados():
    r = {x: ep.a_evento(_b(1, x), URL)["outcome"] for x in ("SUCCESS", "ABORTED", "FAILURE", "OTRO")}
    assert r == {"SUCCESS": "success", "ABORTED": "rejected", "FAILURE": "failure", "OTRO": "unknown"}


def test_en_curso_es_running():
    assert ep.a_evento(_b(5, None, building=True), URL)["outcome"] == "running"


def test_sli_cuenta_rechazo_como_bueno_y_excluye_en_curso():
    ev = [ep.a_evento(_b(i, r), URL) for i, r in enumerate(["SUCCESS", "ABORTED", "FAILURE", "SUCCESS"], 1)]
    ev.append(ep.a_evento(_b(9, None, building=True), URL))
    s = ep.calcular_sli(ev)
    assert (s["buenos"], s["malos"], s["builds"], s["sli_pct"]) == (3, 1, 4, 75.0)
    assert s["cumple_slo"] is False


def test_sli_sin_builds():
    s = ep.calcular_sli([])
    assert s["sli_pct"] is None and s["cumple_slo"] is False


def test_sli_cumple_slo():
    ev = [ep.a_evento(_b(i, "SUCCESS"), URL) for i in range(1, 10)] + [ep.a_evento(_b(10, "FAILURE"), URL)]
    assert ep.calcular_sli(ev)["cumple_slo"] is True  # 90 % exacto
