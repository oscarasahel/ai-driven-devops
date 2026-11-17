import re

import pytest

import validar_spec
from conftest import RAIZ

SPECS = ["specs/001-bucket-artefactos/spec.md", "specs/002-eventos-pedidos/spec.md"]


def _leer(ruta):
    return (RAIZ / ruta).read_text(encoding="utf-8")


def _escribir(tmp_path, texto):
    p = tmp_path / "spec.md"
    p.write_text(texto, encoding="utf-8")
    return p


@pytest.mark.parametrize("ruta", SPECS)
def test_specs_reales_son_validas(ruta):
    assert validar_spec.validar(RAIZ / ruta) == []


def test_sin_estado_falla(tmp_path):
    t = re.sub(r"^- \*\*Estado:\*\*.*\n", "", _leer(SPECS[0]), flags=re.M)
    assert any("Estado" in e for e in validar_spec.validar(_escribir(tmp_path, t)))


def test_estado_invalido_falla(tmp_path):
    t = re.sub(r"(\*\*Estado:\*\*)\s*\w+", r"\1 hecho", _leer(SPECS[0]), count=1)
    assert any("Estado" in e for e in validar_spec.validar(_escribir(tmp_path, t)))


def test_seccion_faltante_falla(tmp_path):
    t = _leer(SPECS[0]).replace("## Riesgos", "## Otra cosa")
    assert any("Riesgos" in e for e in validar_spec.validar(_escribir(tmp_path, t)))


def test_seccion_vacia_falla(tmp_path):
    t = re.sub(r"(## Supuestos\n).*?(\n## )", r"\1\2", _leer(SPECS[0]), count=1, flags=re.S)
    assert any("Supuestos" in e and "vacía" in e for e in validar_spec.validar(_escribir(tmp_path, t)))


def test_hcl_embebido_falla(tmp_path):
    t = _leer(SPECS[0]) + '\n```hcl\nresource "aws_s3_bucket" "x" {}\n```\n'
    assert any("HCL" in e for e in validar_spec.validar(_escribir(tmp_path, t)))


def test_menos_de_tres_criterios_falla(tmp_path):
    t = _leer(SPECS[0])
    ini = t.index("## Criterios de aceptación")
    fin = t.index("## Restricciones")
    criterios = re.split(r"(?=^\*\*CA-\d+)", t[ini:fin], flags=re.M)
    recortado = t[:ini] + "".join(criterios[:3]) + "\n" + t[fin:]  # encabezado + 2 criterios
    assert any("3 criterios" in e for e in validar_spec.validar(_escribir(tmp_path, recortado)))


def test_criterio_sin_entonces_falla(tmp_path):
    t = _leer(SPECS[0]).replace("- Entonces ", "- Resultado ", 1)
    assert any("Entonces" in e for e in validar_spec.validar(_escribir(tmp_path, t)))


def test_mas_de_cinco_preguntas_falla(tmp_path):
    t = re.sub(r"(## Preguntas abiertas\n).*?(\n## Riesgos)",
               r"\1" + "".join(f"- p{i}\n" for i in range(6)) + r"\2", _leer(SPECS[0]), flags=re.S)
    assert any("preguntas" in e for e in validar_spec.validar(_escribir(tmp_path, t)))


def test_main_codigos_de_salida(tmp_path):
    ok = RAIZ / SPECS[0]
    mala = _escribir(tmp_path, "# nada\n")
    assert validar_spec.main([str(ok)]) == 0
    assert validar_spec.main([str(mala)]) == 1
    assert validar_spec.main([]) == 1
