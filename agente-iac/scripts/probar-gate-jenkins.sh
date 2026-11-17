#!/usr/bin/env bash
# Prueba negativa del gate DENTRO de Jenkins: inserta un recurso inseguro, lanza el pipeline y comprueba que
# (1) el build falla en 'Validate, lint y seguridad', (2) no llega a Plan, aprobación ni Apply, y
# (3) el emulador sigue sin buckets. Restaura el archivo original siempre (trap), aunque algo falle.
# Uso (desde agente-iac/, con emulador y Jenkins arriba): bash scripts/probar-gate-jenkins.sh
# Efecto: deja el log en docs/evidencia/jenkins-gate-inseguro.log. No modifica nada versionado al terminar.
# Requisito: Jenkins monta ./ en solo lectura, así que lee el archivo modificado del árbol de trabajo local.
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
TF="infra/envs/local/main.tf"
COPIA="$(mktemp)"
cp "$TF" "$COPIA"
restaurar() { cp "$COPIA" "$TF"; rm -f "$COPIA"; }
trap restaurar EXIT

fallos=0
ok()  { echo "PASS  $1"; }
mal() { echo "FAIL  $1"; fallos=$((fallos + 1)); }

cat >> "$TF" <<'EOF'

resource "aws_s3_bucket" "inseguro" { bucket = "bucket-inseguro" }
resource "aws_s3_bucket_acl" "publico" {
  bucket = aws_s3_bucket.inseguro.id
  acl    = "public-read"
}
EOF

salida="$(bash scripts/jenkins.sh disparar apply)" || { echo "$salida"; exit 1; }
echo "$salida"
N="$(echo "$salida" | sed -nE 's/.*#([0-9]+).*/\1/p')"
res="$(bash scripts/jenkins.sh esperar-fin "$N")"; echo "$res"
bash scripts/jenkins.sh log "$N" > docs/evidencia/jenkins-gate-inseguro.log

echo "$res" | grep -q '"result":"FAILURE"' && ok "el build #$N terminó en FAILURE" || mal "el build #$N no falló: $res"
grep -q "GATE DE SEGURIDAD: FALLÓ" docs/evidencia/jenkins-gate-inseguro.log && ok "el gate de seguridad rechazó el recurso" || mal "el log no muestra el rechazo del gate"
grep -qE "CKV_AWS_20|CKV2_AWS_6" docs/evidencia/jenkins-gate-inseguro.log && ok "Checkov señala el bucket público" || mal "no aparece el control de Checkov esperado"
if grep -qE "Apply complete|Plan: [0-9]+ to |Input requested" docs/evidencia/jenkins-gate-inseguro.log; then
  mal "el pipeline avanzó más allá del gate (plan, aprobación o apply)"
elif grep -q 'Stage "Plan" skipped' docs/evidencia/jenkins-gate-inseguro.log   && grep -q 'Stage "Apply" skipped' docs/evidencia/jenkins-gate-inseguro.log; then
  ok "Plan, Aprobación manual y Apply quedaron omitidos tras el fallo del gate"
else mal "no se pudo confirmar que Plan y Apply se omitieron"; fi
[ -z "$(bash scripts/jenkins.sh estado "$N" | grep 'esperando aprobación')" ] && ok "no hay aprobación pendiente" || mal "quedó una aprobación pendiente"
buckets="$(docker compose run --rm --no-deps -T awscli s3api list-buckets --query 'length(Buckets)' --output text 2>/dev/null | grep -v '^ Container' | tail -1)"
[ "$buckets" = "0" ] && ok "el emulador sigue sin buckets" || mal "el emulador tiene $buckets bucket(s)"

echo
[ "$fallos" -eq 0 ] && echo "PRUEBA NEGATIVA EN JENKINS: OK" || echo "PRUEBA NEGATIVA EN JENKINS: $fallos fallo(s)"
exit $((fallos > 0))
