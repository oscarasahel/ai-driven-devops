import datetime

import excepciones

HOY = datetime.date(2026, 11, 17)


def _exc(**kw):
    base = {"herramienta": "checkov", "id": "CKV_X", "recurso": "r", "justificacion": "porque",
            "revision": "2027-02-16"}
    base.update(kw)
    return base


def test_vigente_devuelve_id():
    ids, errs = excepciones.evaluar({"excepciones": [_exc()]}, "checkov", HOY)
    assert ids == [("CKV_X", "2027-02-16")] and errs == []


def test_filtra_por_herramienta():
    datos = {"excepciones": [_exc(), _exc(herramienta="trivy", id="AVD-1")]}
    assert [i for i, _ in excepciones.evaluar(datos, "trivy", HOY)[0]] == ["AVD-1"]


def test_vencida_es_error():
    ids, errs = excepciones.evaluar({"excepciones": [_exc(revision="2026-01-01")]}, "checkov", HOY)
    assert ids == [] and "vencida" in errs[0]


def test_vence_hoy_aun_es_valida():
    ids, errs = excepciones.evaluar({"excepciones": [_exc(revision="2026-11-17")]}, "checkov", HOY)
    assert errs == [] and ids


def test_campo_faltante_es_error():
    _, errs = excepciones.evaluar({"excepciones": [_exc(justificacion="  ")]}, "checkov", HOY)
    assert "justificacion" in errs[0]


def test_fecha_invalida_es_error():
    _, errs = excepciones.evaluar({"excepciones": [_exc(revision="mañana")]}, "checkov", HOY)
    assert "inválida" in errs[0]


def test_excepcion_rota_de_otra_herramienta_tambien_rompe():
    # El gate es todo o nada: una excepción vencida de trivy invalida también la lectura de checkov.
    datos = {"excepciones": [_exc(), _exc(herramienta="trivy", id="AVD-1", revision="2020-01-01")]}
    assert excepciones.evaluar(datos, "checkov", HOY)[1]


def test_archivo_real_vigente_y_vencido_en_2028(capsys):
    assert excepciones.main(["checkov", "--hoy", "2026-11-17"]) == 0
    assert "CKV_AWS_145" in capsys.readouterr().out
    assert excepciones.main(["checkov", "--hoy", "2028-01-01"]) == 1


def test_formato_trivy(capsys):
    assert excepciones.main(["trivy", "--hoy", "2026-11-17"]) == 0
    assert "AVD-AWS-0132 exp:2027-02-16" in capsys.readouterr().out


def test_uso_incorrecto():
    assert excepciones.main([]) == 2
