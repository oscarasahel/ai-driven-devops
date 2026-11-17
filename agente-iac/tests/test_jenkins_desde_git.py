"""Spec 005: Jenkins obtiene el código de Git y se dispara tras el merge, sin saltarse la aprobación manual."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
JENKINS = RAIZ / "jenkins"


def _leer(ruta):
    return Path(ruta).read_text(encoding="utf-8")


def _jenkinsfile():
    return _leer(JENKINS / "Jenkinsfile")


def test_el_job_usa_definicion_desde_git_y_polling():
    t = _leer(JENKINS / "casc" / "jobs.groovy")
    assert "cpsScm" in t and "git {" in t  # CA-1
    assert "scm('H/5 * * * *')" in t  # CA-3
    assert "REPO_BRANCH') ?: 'main'" in t
    assert "scriptPath('agente-iac/jenkins/Jenkinsfile')" in t
    assert "cps {" not in t and "new File(" not in t  # ya no se copia el Jenkinsfile de la imagen


def test_el_job_no_lleva_credenciales_en_claro():  # CA-9
    t = _leer(JENKINS / "casc" / "jobs.groovy")
    assert re.search(r"https://[^/@\s]+@", t) is None  # sin usuario:token en la URL
    assert not re.search(r"(password|token|secret)\s*[=(]", t, flags=re.I)


def test_los_valores_por_defecto_nunca_son_destroy():  # CA-4
    t = _jenkinsfile()
    entorno = re.search(r"name: 'ENTORNO', choices: \['(\w+)'", t).group(1)
    accion = re.search(r"name: 'ACCION', choices: \['(\w+)'", t).group(1)
    assert (entorno, accion) == ("staging", "apply")


def test_la_aprobacion_manual_precede_al_apply():  # CA-5
    t = _jenkinsfile()
    assert "input message" in t
    assert t.index("stage('Aprobación manual')") < t.index("stage('Apply')")


def test_encadenar_local_solo_encola_y_solo_tras_apply_de_staging():  # CA-6
    t = _jenkinsfile()
    bloque = t[t.index("stage('Encadenar local')"):t.rindex("\n  post {")]
    assert "ENTORNO_EFECTIVO == 'staging'" in bloque and "ACCION_EFECTIVA == 'apply'" in bloque
    assert "wait: false" in bloque
    assert "string(name: 'ENTORNO', value: 'local')" in bloque
    assert "string(name: 'ACCION', value: 'apply')" in bloque
    assert "destroy" not in bloque
    assert t.index("stage('Registrar promoción')") < t.index("stage('Encadenar local')")


def test_ninguna_ruta_automatica_dispara_destroy():  # CA-4
    t = _leer(JENKINS / "casc" / "jobs.groovy") + _jenkinsfile()
    for m in re.finditer(r"build job:.*?\]", t, flags=re.S):
        assert "destroy" not in m.group(0)


def test_la_imagen_tiene_git_y_el_plugin_fijado():
    d = _leer(JENKINS / "Dockerfile")
    assert re.search(r"apt-get install[^\n]*\bgit\b", d)
    assert "COPY Jenkinsfile" not in d
    plugins = [l for l in _leer(JENKINS / "plugins.txt").splitlines() if l and not l.startswith("#")]
    assert any(re.fullmatch(r"git:\d[\w.\-]*", p) for p in plugins)
    assert all(re.fullmatch(r"[\w\-]+:[^\s:]+", p) for p in plugins)  # todos con versión


def test_el_compose_no_monta_el_codigo_y_define_origen_con_valores_por_defecto():
    c = _leer(RAIZ / "docker-compose.yml")
    jenkins = c[c.index("  jenkins:"):c.index("  # Sirve bitacora.json")]
    assert "./:/repo" not in jenkins
    assert "REPO_BRANCH: ${REPO_BRANCH:-main}" in jenkins
    assert "REPO_URL: ${REPO_URL:-https://" in jenkins
