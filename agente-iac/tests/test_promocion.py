import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import promocion as p


@pytest.fixture
def infra(tmp_path):
    i = tmp_path / "infra"
    (i / "envs" / "local").mkdir(parents=True)
    (i / "envs" / "local" / "main.tf").write_text('resource "a" "b" {}\n', encoding="utf-8")
    (i / "envs" / "local" / "terraform.tfvars").write_text('owner = "x"\n', encoding="utf-8")
    return i


def test_sin_staging_la_promocion_se_bloquea(infra, tmp_path):
    assert p.exigir(infra, tmp_path / "m")[1] is False
    assert p.main(["exigir", "--infra", str(infra), "--dir", str(tmp_path / "m")]) == 1


def test_con_staging_verificado_se_permite(infra, tmp_path):
    p.marcar(infra, tmp_path / "m")
    assert p.exigir(infra, tmp_path / "m")[1] is True


def test_cambiar_un_tf_invalida_la_promocion(infra, tmp_path):
    p.marcar(infra, tmp_path / "m")
    (infra / "envs" / "local" / "main.tf").write_text('resource "a" "c" {}\n', encoding="utf-8")
    assert p.exigir(infra, tmp_path / "m")[1] is False


def test_agregar_un_modulo_invalida_la_promocion(infra, tmp_path):
    p.marcar(infra, tmp_path / "m")
    (infra / "extra.tf").write_text("# nuevo\n", encoding="utf-8")
    assert p.exigir(infra, tmp_path / "m")[1] is False


def test_tfvars_estado_y_terraform_no_cambian_la_huella(infra, tmp_path):
    h = p.huella(infra)
    (infra / "envs" / "local" / "staging.tfvars").write_text('env = "staging"\n', encoding="utf-8")
    (infra / "envs" / "local" / "terraform.tfstate").write_text("{}", encoding="utf-8")
    (infra / "envs" / "local" / ".terraform").mkdir()
    (infra / "envs" / "local" / ".terraform" / "x.tf").write_text("basura", encoding="utf-8")
    assert p.huella(infra) == h


def test_crlf_y_lf_dan_la_misma_huella(infra):
    f = infra / "envs" / "local" / "main.tf"
    f.write_bytes(b'resource "a" "b" {}\n')
    h = p.huella(infra)
    f.write_bytes(b'resource "a" "b" {}\r\n')
    assert p.huella(infra) == h


def test_revocar_quita_los_marcadores(infra, tmp_path):
    p.marcar(infra, tmp_path / "m")
    assert p.revocar(tmp_path / "m") == 1
    assert p.exigir(infra, tmp_path / "m")[1] is False


def test_sin_archivos_terraform_falla(tmp_path):
    (tmp_path / "vacio").mkdir()
    with pytest.raises(SystemExit):
        p.huella(tmp_path / "vacio")
