#!/usr/bin/env bash
# Gate de seguridad de IaC: fmt, validate, TFLint, Checkov y Trivy.
# Uso (desde agente-iac/): bash scripts/seguridad.sh [directorio-infra]   (por defecto ./infra)
# Informes en reports/ (JUnit y SARIF). Sale con 1 si algún gate falla.
# No requiere el emulador: usa imágenes con versión fijada y terraform init -backend=false.
set -u
export MSYS_NO_PATHCONV=1

TF_IMG="hashicorp/terraform:1.9.8"
TFLINT_IMG="ghcr.io/terraform-linters/tflint:v0.53.0"
CHECKOV_IMG="bridgecrew/checkov:3.2.255"
TRIVY_IMG="aquasec/trivy:0.58.1"
PY_IMG="python:3.12-slim"

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ" || exit 1
INFRA="${1:-infra}"
ENVDIR="$INFRA/envs/local"
mkdir -p reports
rm -f reports/*.xml reports/*.sarif reports/resumen.txt

fallos=0
paso() { printf '\n== %s ==\n' "$1"; }
resultado() { # nombre rc
  if [ "$2" -eq 0 ]; then echo "PASS  $1" | tee -a reports/resumen.txt
  else echo "FAIL  $1" | tee -a reports/resumen.txt; fallos=$((fallos + 1)); fi
}
py() { docker run --rm -v "$RAIZ:/w" -w /w $PY_IMG python -I "$@"; }

paso "Excepciones documentadas"
CKV_SKIP="$(py scripts/excepciones.py checkov)"; rc=$?
py scripts/excepciones.py trivy > reports/.trivyignore 2>/dev/null || rc=1
resultado "excepciones válidas y vigentes" $rc
[ $rc -ne 0 ] && CKV_SKIP=""

paso "terraform fmt"
docker run --rm -v "$RAIZ/$INFRA:/infra" $TF_IMG fmt -recursive -check -diff /infra
resultado "terraform fmt -check" $?

paso "terraform validate"
docker run --rm --entrypoint sh -v "$RAIZ/$INFRA:/infra" -w "/infra/envs/local" $TF_IMG -c \
  'terraform init -backend=false -input=false -no-color >/dev/null && terraform validate -no-color'
rc=$?
rm -rf "$ENVDIR/.terraform" 2>/dev/null
resultado "terraform validate" $rc

paso "TFLint"
docker run --rm -v "$RAIZ:/w" -w /w $TFLINT_IMG --init >/dev/null 2>&1
docker run --rm -v "$RAIZ:/w" -w /w $TFLINT_IMG --config=/w/.tflint.hcl --chdir="/w/$INFRA" --recursive --minimum-failure-severity=warning
resultado "tflint" $?
docker run --rm -v "$RAIZ:/w" -w /w $TFLINT_IMG --config=/w/.tflint.hcl --chdir="/w/$INFRA" --recursive --format=junit > reports/tflint.xml 2>/dev/null

paso "Checkov"
docker run --rm -v "$RAIZ:/w" -w /w $CHECKOV_IMG -d "/w/$INFRA" --framework terraform --compact --quiet \
  --skip-check "$CKV_SKIP" --output cli --output junitxml --output sarif --output-file-path /w/reports \
  | grep -E "^Check:|FAILED for|Passed checks"
rc=${PIPESTATUS[0]}
# Checkov escribe results_cli.txt, results_junitxml.xml y results_sarif.sarif en reports/
resultado "checkov (sin excepciones documentadas)" $rc

paso "Trivy config (HIGH/CRITICAL)"
cp reports/.trivyignore reports/trivyignore.tmp 2>/dev/null
docker run --rm -v "$RAIZ:/w" -w /w $TRIVY_IMG config --quiet --severity HIGH,CRITICAL --exit-code 1 \
  --ignorefile /w/reports/trivyignore.tmp "/w/$INFRA"
resultado "trivy HIGH/CRITICAL" $?
docker run --rm -v "$RAIZ:/w" -w /w $TRIVY_IMG config --quiet --severity HIGH,CRITICAL \
  --ignorefile /w/reports/trivyignore.tmp --format sarif --output /w/reports/trivy.sarif "/w/$INFRA" >/dev/null 2>&1
rm -f reports/trivyignore.tmp

echo
if [ "$fallos" -eq 0 ]; then echo "GATE DE SEGURIDAD: OK"; exit 0
else echo "GATE DE SEGURIDAD: FALLÓ ($fallos etapa(s))"; exit 1; fi
