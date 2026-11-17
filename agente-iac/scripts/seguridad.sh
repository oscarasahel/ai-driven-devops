#!/usr/bin/env bash
# Gate de seguridad de IaC: fmt, validate, TFLint, Checkov y Trivy.
# Uso (desde agente-iac/): bash scripts/seguridad.sh [directorio-infra]   (por defecto ./infra)
# Modo por defecto: contenedores con versión fijada (requiere Docker).
# Modo nativo (Jenkins): SEGURIDAD_MODO=nativo usa los binarios instalados en el PATH.
# Informes en reports/ (JUnit y SARIF). Sale con 1 si algún gate falla.
# No requiere el emulador.
set -u
export MSYS_NO_PATHCONV=1

TF_IMG="hashicorp/terraform:1.9.8"
TFLINT_IMG="ghcr.io/terraform-linters/tflint:v0.53.0"
CHECKOV_IMG="bridgecrew/checkov:3.2.255"
TRIVY_IMG="aquasec/trivy:0.58.1"
PY_IMG="python:3.12-slim"
MODO="${SEGURIDAD_MODO:-docker}"

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ" || exit 1
INFRA="${1:-infra}"
ENVDIR="$INFRA/envs/local"
mkdir -p reports
rm -f reports/*.xml reports/*.sarif reports/resumen.txt reports/results_cli.txt

fallos=0
paso() { printf '\n== %s ==\n' "$1"; }
resultado() { # nombre rc
  if [ "$2" -eq 0 ]; then echo "PASS  $1" | tee -a reports/resumen.txt
  else echo "FAIL  $1" | tee -a reports/resumen.txt; fallos=$((fallos + 1)); fi
}

# --- Envoltorios por modo ---
if [ "$MODO" = "nativo" ]; then
  py()       { python3 -I "$@"; }
  tf_fmt()   { terraform fmt -recursive -check -diff "$RAIZ/$INFRA"; }
  tf_val()   { (cd "$RAIZ/$ENVDIR" && terraform init -backend=false -input=false -no-color >/dev/null && terraform validate -no-color); }
  tflint_()  { tflint --config="$RAIZ/.tflint.hcl" --chdir="$RAIZ/$INFRA" --recursive "$@"; }
  checkov_() { checkov -d "$RAIZ/$INFRA" --framework terraform --compact --quiet "$@"; }
  trivy_()   { trivy config --quiet "$@" "$RAIZ/$INFRA"; }
  RUTA_REP="$RAIZ/reports"
else
  py()       { docker run --rm -v "$RAIZ:/w" -w /w $PY_IMG python -I "$@"; }
  tf_fmt()   { docker run --rm -v "$RAIZ/$INFRA:/infra" $TF_IMG fmt -recursive -check -diff /infra; }
  tf_val()   { docker run --rm --entrypoint sh -v "$RAIZ/$INFRA:/infra" -w /infra/envs/local $TF_IMG -c \
                 'terraform init -backend=false -input=false -no-color >/dev/null && terraform validate -no-color'; }
  tflint_()  { docker run --rm -v "$RAIZ:/w" -w /w $TFLINT_IMG --config=/w/.tflint.hcl --chdir="/w/$INFRA" --recursive "$@"; }
  checkov_() { docker run --rm -v "$RAIZ:/w" -w /w $CHECKOV_IMG -d "/w/$INFRA" --framework terraform --compact --quiet "$@"; }
  trivy_()   { docker run --rm -v "$RAIZ:/w" -w /w $TRIVY_IMG config --quiet "$@" "/w/$INFRA"; }
  RUTA_REP="/w/reports"
fi

paso "Excepciones documentadas"
CKV_SKIP="$(py scripts/excepciones.py checkov)"; rc=$?
py scripts/excepciones.py trivy > reports/trivyignore.tmp 2>/dev/null || rc=1
resultado "excepciones válidas y vigentes" $rc
[ $rc -ne 0 ] && CKV_SKIP=""

paso "terraform fmt"
tf_fmt
resultado "terraform fmt -check" $?

paso "terraform validate"
tf_val
rc=$?
rm -rf "$RAIZ/$ENVDIR/.terraform" 2>/dev/null
resultado "terraform validate" $rc

paso "TFLint"
tflint_ --minimum-failure-severity=warning
resultado "tflint" $?
tflint_ --format=junit > reports/tflint.xml 2>/dev/null

paso "Checkov"
checkov_ --skip-check "$CKV_SKIP" --output cli --output junitxml --output sarif --output-file-path "$RUTA_REP" \
  | grep -E "^Check:|FAILED for|Passed checks"
rc=${PIPESTATUS[0]}
# Checkov escribe results_cli.txt, results_junitxml.xml y results_sarif.sarif en reports/
resultado "checkov (sin excepciones documentadas)" $rc

paso "Trivy config (HIGH/CRITICAL)"
if [ "$MODO" = "nativo" ]; then IGN="$RAIZ/reports/trivyignore.tmp"; else IGN="/w/reports/trivyignore.tmp"; fi
trivy_ --severity HIGH,CRITICAL --exit-code 1 --ignorefile "$IGN"
resultado "trivy HIGH/CRITICAL" $?
trivy_ --severity HIGH,CRITICAL --ignorefile "$IGN" --format sarif --output "$RUTA_REP/trivy.sarif" >/dev/null 2>&1
rm -f reports/trivyignore.tmp

echo
if [ "$fallos" -eq 0 ]; then echo "GATE DE SEGURIDAD: OK"; exit 0
else echo "GATE DE SEGURIDAD: FALLÓ ($fallos etapa(s))"; exit 1; fi
