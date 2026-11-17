#!/usr/bin/env bash
# Evals deterministas: cada caso declara el código de salida esperado y el real. No requiere LLM ni el emulador.
# Uso (desde agente-iac/, con Docker): bash evals/run_evals.sh            (rápidos + gate, ~3 min)
#                                       bash evals/run_evals.sh rapido     (solo casos sin gate)
# Sale con 0 si todos los casos coinciden con lo esperado.
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
MODO="${1:-completo}"
T="reports/evals"; rm -rf "$T"; mkdir -p "$T"
PY="docker run --rm -v $PWD:/w -w /w python:3.12-slim python -I"
total=0; mal=0

caso() { # <nombre> <rc-esperado> <comando...>
  local nombre="$1" esperado="$2"; shift 2
  "$@" >"$T/ultimo.log" 2>&1; local rc=$?
  total=$((total + 1))
  if [ "$rc" -eq "$esperado" ]; then printf 'PASS  %-62s esperado=%s real=%s\n' "$nombre" "$esperado" "$rc"
  else printf 'FAIL  %-62s esperado=%s real=%s\n' "$nombre" "$esperado" "$rc"; tail -5 "$T/ultimo.log" | sed 's/^/        /'; mal=$((mal + 1)); fi
}

S1=specs/001-bucket-artefactos/spec.md
S2=specs/002-eventos-pedidos/spec.md

echo "== Specs (analizar-requerimiento) =="
caso "spec 001 válida"                                     0 $PY scripts/validar_spec.py $S1
caso "spec 002 válida"                                     0 $PY scripts/validar_spec.py $S2

# Requerimiento ambiguo: una spec que acumula >5 preguntas abiertas no es válida (hay que preguntar lo prioritario).
python - "$S1" "$T/ambigua.md" <<'EOF'
import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
t=re.sub(r"(## Preguntas abiertas\n).*?(\n## Riesgos)",r"\1"+"".join(f"- pregunta {i}\n" for i in range(7))+r"\2",t,flags=re.S)
open(sys.argv[2],'w',encoding='utf-8').write(t)
EOF
caso "negativa: ambigüedad sin priorizar (7 preguntas)"      1 $PY scripts/validar_spec.py $T/ambigua.md

# Spec con Terraform embebido (la skill no debe generar código)
{ cat $S1; printf '\n```hcl\nresource "aws_s3_bucket" "x" {}\n```\n'; } > $T/con_hcl.md
caso "negativa: spec con HCL embebido"                       1 $PY scripts/validar_spec.py $T/con_hcl.md

# Spec sin estado (no se puede aprobar lo que no declara estado)
grep -v '^- \*\*Estado:\*\*' $S1 > $T/sin_estado.md
caso "negativa: spec sin campo Estado"                       1 $PY scripts/validar_spec.py $T/sin_estado.md

# Criterio sin Dado/Cuando/Entonces
sed 's/^- Entonces /- Resultado /' $S1 > $T/sin_gwt.md
caso "negativa: criterios sin Entonces"                      1 $PY scripts/validar_spec.py $T/sin_gwt.md

echo "== Controles de proceso (inyección de prompt / aprobación) =="
# Un requerimiento malicioso no puede saltarse la aprobación: es una propiedad del pipeline, no del prompt.
caso "Jenkinsfile: 'Aprobación manual' antecede a 'Apply'"   0 $PY -c "
import re,sys
t=open('jenkins/Jenkinsfile',encoding='utf-8').read()
a=t.index(\"stage('Aprobación manual')\"); b=t.index(\"stage('Apply')\")
sys.exit(0 if a<b and 'input message' in t[a:b] else 1)"
caso "Jenkinsfile sin -auto-approve"                         1 grep -n -- "-auto-approve" jenkins/Jenkinsfile
caso "sin credenciales tipo AKIA en archivos versionados"    1 git grep -qE 'AKIA[0-9A-Z]{16}' -- ':!evals/run_evals.sh'
caso ".env no está versionado"                               1 sh -c "git ls-files | grep -E '(^|/)\.env$'"

echo "== Bitácora (veracidad) =="
cat > $T/commit_falso.json <<'EOF'
{"numero":99,"fecha":"2026-11-16","fase":"x","tema":"x","slug":"x","simulado":false,"temas_curso":[],"objetivo":"x","archivos":[],"decisiones":[],"evidencia":[{"tipo":"commit","ref":"deadbee"}],"metricas":{},"riesgos":[],"siguiente":"x"}
EOF
caso "negativa: sesión real con commit inexistente"          1 python scripts/bitacora.py agregar $T/commit_falso.json
caso "bitácora actual válida"                                0 python scripts/bitacora.py validar

echo "== Excepciones =="
caso "excepciones vigentes hoy"                              0 $PY scripts/excepciones.py checkov
caso "negativa: excepciones vencidas (fecha simulada 2028)"  1 $PY scripts/excepciones.py checkov --hoy 2028-01-01

if [ "$MODO" != "rapido" ]; then
  echo "== Gate de seguridad (lento) =="
  caso "gate sobre infra/ actual"                            0 bash scripts/seguridad.sh
  rm -rf .evals-neg && cp -r infra .evals-neg && rm -rf .evals-neg/envs/local/.terraform
  cat >> .evals-neg/envs/local/main.tf <<'EOF'

resource "aws_s3_bucket" "inseguro" { bucket = "bucket-inseguro" }
resource "aws_s3_bucket_acl" "publico" {
  bucket = aws_s3_bucket.inseguro.id
  acl    = "public-read"
}
EOF
  caso "negativa: recurso inseguro (S3 público sin cifrar)"  1 bash scripts/seguridad.sh .evals-neg
  rm -rf .evals-neg
fi

echo
echo "Casos: $total, discrepancias: $mal"
[ "$mal" -eq 0 ] && { echo "EVALS OK"; exit 0; } || { echo "EVALS CON DISCREPANCIAS"; exit 1; }
