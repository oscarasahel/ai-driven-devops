import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REPO = RAIZ.parent


def test_gitattributes_fuerza_lf():
    """Jenkins y Docker (Linux) leen el árbol de trabajo de Windows: los scripts con CRLF no se ejecutan."""
    t = (REPO / ".gitattributes").read_text(encoding="utf-8")
    assert "eol=lf" in t


def test_scripts_y_jenkinsfile_sin_crlf():
    archivos = list((RAIZ / "scripts").glob("*.sh")) + [RAIZ / "jenkins" / "Jenkinsfile", RAIZ / "docker-compose.yml"]
    con_crlf = [str(a.relative_to(RAIZ)) for a in archivos if b"\r\n" in a.read_bytes()]
    assert con_crlf == []


def test_los_archivos_versionados_se_normalizan_a_lf():
    r = subprocess.run(["git", "ls-files", "--eol"], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        return  # sin git disponible: no se puede comprobar
    assert [l for l in r.stdout.splitlines() if l.startswith("i/crlf")] == []
