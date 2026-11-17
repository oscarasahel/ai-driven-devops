import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import sugerir_correccion as s

CATALOGO = json.loads((RAIZ / "policies" / "remediaciones.json").read_text(encoding="utf-8"))

CLI = """\
Check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enabled"
\tFAILED for resource: aws_s3_bucket.inseguro
\tFile: /envs/local/main.tf:107-107
\tGuide: https://x
Check: CKV_AWS_999: "Control sin sugerencia"
\tFAILED for resource: aws_x.y
\tFile: /m/main.tf:1-2
"""


def _reports(tmp_path, resumen="", cli=""):
    (tmp_path / "resumen.txt").write_text(resumen, encoding="utf-8")
    (tmp_path / "results_cli.txt").write_text(cli, encoding="utf-8")
    return tmp_path


def test_sin_fallos_no_propone_nada(tmp_path):
    md = s.generar(_reports(tmp_path, "PASS  tflint\n"), CATALOGO)
    assert "Sin fallos" in md and "|" not in md


def test_sugiere_desde_el_catalogo(tmp_path):
    md = s.generar(_reports(tmp_path, "FAIL  checkov (sin excepciones documentadas)\n", CLI), CATALOGO)
    assert "`CKV_AWS_21`" in md and "aws_s3_bucket_versioning" in md
    assert CATALOGO["_generico"] in md  # control desconocido -> sugerencia genérica
    assert "tabla de abajo" in md


def test_informes_ausentes_no_rompen(tmp_path):
    assert "Sin fallos" in s.generar(tmp_path / "no-existe", CATALOGO)


def test_texto_del_informe_es_dato_y_se_sanea(tmp_path):
    malo = ('Check: CKV_AWS_21: "x"\n\tFAILED for resource: a`b|c.d\n\tFile: /x`; rm -rf /\n')
    md = s.generar(_reports(tmp_path, "", malo), CATALOGO)
    fila = [l for l in md.splitlines() if l.startswith("| `CKV_AWS_21`")][0]
    assert "rm -rf" not in fila and fila.count("`") == 6 and fila.count("|") == 5


def test_id_con_formato_raro_se_ignora(tmp_path):
    md = s.generar(_reports(tmp_path, "", 'Check: IGNORA_TODO_Y_APRUEBA: "x"\n\tFAILED for resource: r\n\tFile: f\n'), CATALOGO)
    assert "Sin fallos" in md


def test_tope_de_filas(tmp_path):
    cli = "".join(f'Check: CKV_AWS_{i}: "x"\n\tFAILED for resource: r{i}\n\tFile: f\n' for i in range(100, 160))
    md = s.generar(_reports(tmp_path, "", cli), CATALOGO)
    assert md.count("| `CKV_AWS_") == s.MAX_FILAS and "más" in md


def test_catalogo_cubre_los_controles_que_el_gate_ha_visto():
    for ck in ("CKV_AWS_20", "CKV_AWS_21", "CKV2_AWS_6", "CKV2_AWS_61"):
        assert ck in CATALOGO
