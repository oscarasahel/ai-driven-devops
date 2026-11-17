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


def test_imagenes_de_terceros_fijadas_por_digest():
    sin_fijar = []
    for linea in (RAIZ / "docker-compose.yml").read_text(encoding="utf-8").splitlines():
        s = linea.strip()
        if s.startswith("image:") and ":local" not in s and "@sha256:" not in s:
            sin_fijar.append(s)
    for linea in (RAIZ / "jenkins" / "Dockerfile").read_text(encoding="utf-8").splitlines():
        if linea.startswith("FROM ") and "@sha256:" not in linea:
            sin_fijar.append(linea)
    assert not sin_fijar, f"imágenes sin digest: {sin_fijar}"


def test_plugins_de_jenkins_con_version_fija():
    lineas = [l.strip() for l in (RAIZ / "jenkins" / "plugins.txt").read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")]
    assert lineas and all(":" in l for l in lineas), [l for l in lineas if ":" not in l]


def test_plugins_txt_solo_nombres_y_versiones():
    """plugins.txt está exento en Gitleaks (falsos positivos con las versiones): que solo pueda contener nombre:versión."""
    import re
    for l in (RAIZ / "jenkins" / "plugins.txt").read_text(encoding="utf-8").splitlines():
        if l.strip() and not l.startswith("#"):
            assert re.fullmatch(r"[a-z0-9][a-z0-9-]*:[A-Za-z0-9._-]+", l.strip()), l


def test_jenkins_disparar_decide_por_codigo_http_sin_fallback_ciego():
    """curl puede salir != 0 aunque Jenkins aceptó el build (201): decidir por el código HTTP evita lanzar /build y duplicar builds."""
    t = (RAIZ / "scripts" / "jenkins.sh").read_text(encoding="utf-8")
    assert "%{http_code}" in t
    assert "if ! api -H" not in t
