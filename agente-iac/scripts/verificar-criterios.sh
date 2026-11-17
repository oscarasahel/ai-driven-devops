#!/usr/bin/env bash
# Verifica los criterios de aceptación de las specs 001, 002 y 004 contra el emulador.
# Uso (desde agente-iac/, con el emulador y los recursos desplegados): [NAME_PREFIX=agente-iac-stg] bash scripts/verificar-criterios.sh
# Sale con 0 si todo pasa, 1 si algún criterio falla.
set -u
export MSYS_NO_PATHCONV=1

P="${NAME_PREFIX:-agente-iac}"   # staging usa agente-iac-stg (NAME_PREFIX)
B="$P-artifacts"
S="$P-secrets"
ROLE="$P-pipeline"
TOPIC="arn:aws:sns:us-east-1:000000000000:$P-order-events"
QURL="https://sqs.us-east-1.amazonaws.com/000000000000/$P-order-events"
DURL="https://sqs.us-east-1.amazonaws.com/000000000000/$P-order-events-dlq"
TABLE="$P-order-state"
POLICY_ARN="arn:aws:iam::000000000000:policy/$ROLE-bucket-rw"

fallos=0
# VERIFICAR_MODO=nativo (Jenkins): usa el binario aws del PATH; por defecto, el servicio awscli del compose.
if [ "${VERIFICAR_MODO:-docker}" = "nativo" ]; then
  aws() { command aws "$@" 2>/dev/null; }
else
  aws() { docker compose run --rm -T awscli "$@" 2>/dev/null | grep -v '^ Container'; }
fi

# chk <nombre> <patrón-regex-esperado> <salida>
chk() {
  if printf '%s' "$3" | grep -Eq "$2"; then
    echo "OK    $1"
  else
    echo "FAIL  $1  (esperado /$2/, obtenido: $(printf '%s' "$3" | tr '\n' ' ' | cut -c1-160))"
    fallos=$((fallos + 1))
  fi
}
# nochk <nombre> <patrón-regex-prohibido> <salida>
nochk() {
  if printf '%s' "$3" | grep -Eq "$2"; then
    echo "FAIL  $1  (aparece /$2/)"
    fallos=$((fallos + 1))
  else
    echo "OK    $1"
  fi
}

echo "== Spec 001 =="
chk "001 CA-1 bloqueo público" '^True\s+True\s+True\s+True$' "$(aws s3api get-public-access-block --bucket $B --query 'PublicAccessBlockConfiguration.[BlockPublicAcls,IgnorePublicAcls,BlockPublicPolicy,RestrictPublicBuckets]' --output text)"
chk "001 CA-2 cifrado" '^(AES256|aws:kms)$' "$(aws s3api get-bucket-encryption --bucket $B --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm' --output text)"
chk "001 CA-3 versionado" '^Enabled$' "$(aws s3api get-bucket-versioning --bucket $B --query Status --output text)"
pol="$(aws s3api get-bucket-policy --bucket $B --query Policy --output text)"
chk "001 CA-4 solo HTTPS" 'Deny' "$pol"
chk "001 CA-4 condición SecureTransport" 'aws:SecureTransport' "$pol"
chk "001 CA-5 retención 30/7" '^30\s+7$' "$(aws s3api get-bucket-lifecycle-configuration --bucket $B --query 'Rules[0].[Expiration.Days,NoncurrentVersionExpiration.NoncurrentDays]' --output text)"
doc="$(aws iam get-policy-version --policy-arn $POLICY_ARN --version-id v1 --query PolicyVersion.Document --output json)"
chk "001 CA-6 acciones permitidas" 's3:GetObject' "$doc"
nochk "001 CA-6 sin comodín s3:*" '"s3:\*"' "$doc"
nochk "001 CA-6 sin Resource *" '"Resource": *"\*"' "$doc"
btags="$(aws s3api get-bucket-tagging --bucket $B --output text)"
rtags="$(aws iam list-role-tags --role-name $ROLE --output text)"
for k in project env owner; do
  chk "001 CA-7 etiqueta $k en bucket" "$k" "$btags"
  chk "001 CA-7 etiqueta $k en rol" "$k" "$rtags"
done

echo "== Spec 002 =="
aws sns publish --topic-arn "$TOPIC" --message "verificar-$(date +%s)" >/dev/null
chk "002 CA-1 entrega tema->cola" 'verificar-' "$(aws sqs receive-message --queue-url $QURL --wait-time-seconds 5 --query 'Messages[0].Body' --output text)"
chk "002 CA-2 maxReceiveCount 3" 'maxReceiveCount.{1,4}3' "$(aws sqs get-queue-attributes --queue-url $QURL --attribute-names RedrivePolicy --query Attributes.RedrivePolicy --output text)"
chk "002 CA-2 apunta a la DLQ" 'order-events-dlq' "$(aws sqs get-queue-attributes --queue-url $QURL --attribute-names RedrivePolicy --query Attributes.RedrivePolicy --output text)"
chk "002 CA-3 retención DLQ 14d" '^1209600$' "$(aws sqs get-queue-attributes --queue-url $DURL --attribute-names MessageRetentionPeriod --query Attributes.MessageRetentionPeriod --output text)"
chk "002 CA-4 cifrado cola" '^true$' "$(aws sqs get-queue-attributes --queue-url $QURL --attribute-names SqsManagedSseEnabled --query Attributes.SqsManagedSseEnabled --output text)"
chk "002 CA-4 cifrado DLQ" '^true$' "$(aws sqs get-queue-attributes --queue-url $DURL --attribute-names SqsManagedSseEnabled --query Attributes.SqsManagedSseEnabled --output text)"
chk "002 CA-5 clave order_id (S)" '^order_id\s+HASH$' "$(aws dynamodb describe-table --table-name $TABLE --query 'Table.KeySchema[0].[AttributeName,KeyType]' --output text)"
chk "002 CA-5 PAY_PER_REQUEST" 'PAY_PER_REQUEST' "$(aws dynamodb describe-table --table-name $TABLE --query 'Table.BillingModeSummary.BillingMode' --output text)"
chk "002 CA-6 TTL habilitado" '^ENABLED$' "$(aws dynamodb describe-time-to-live --table-name $TABLE --query 'TimeToLiveDescription.TimeToLiveStatus' --output text)"
chk "002 CA-6 PITR habilitado" '^ENABLED$' "$(aws dynamodb describe-continuous-backups --table-name $TABLE --query 'ContinuousBackupsDescription.PointInTimeRecoveryDescription.PointInTimeRecoveryStatus' --output text)"
qpol="$(aws sqs get-queue-attributes --queue-url $QURL --attribute-names Policy --query Attributes.Policy --output text)"
chk "002 CA-7 solo SendMessage" 'sqs:SendMessage' "$qpol"
chk "002 CA-7 principal SNS" 'sns.amazonaws.com' "$qpol"
chk "002 CA-7 SourceArn del tema" "aws:SourceArn.*$P-order-events" "$qpol"
for k in project env owner; do
  chk "002 CA-8 etiqueta $k en tema" "$k" "$(aws sns list-tags-for-resource --resource-arn $TOPIC --output text)"
  chk "002 CA-8 etiqueta $k en cola" "$k" "$(aws sqs list-queue-tags --queue-url $QURL --query "keys(Tags)" --output text)"
  chk "002 CA-8 etiqueta $k en DLQ" "$k" "$(aws sqs list-queue-tags --queue-url $DURL --query "keys(Tags)" --output text)"
  chk "002 CA-8 etiqueta $k en tabla" "$k" "$(aws dynamodb list-tags-of-resource --resource-arn arn:aws:dynamodb:us-east-1:000000000000:table/$TABLE --output text)"
done

echo "== Spec 004 =="
chk "004 CA-1 bloqueo público" '^True\s+True\s+True\s+True$' "$(aws s3api get-public-access-block --bucket $S --query 'PublicAccessBlockConfiguration.[BlockPublicAcls,IgnorePublicAcls,BlockPublicPolicy,RestrictPublicBuckets]' --output text)"
chk "004 CA-2 cifrado" '^(AES256|aws:kms)$' "$(aws s3api get-bucket-encryption --bucket $S --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm' --output text)"
chk "004 CA-3 versionado" '^Enabled$' "$(aws s3api get-bucket-versioning --bucket $S --query Status --output text)"
chk "004 CA-4 regla habilitada" '^Enabled$' "$(aws s3api get-bucket-lifecycle-configuration --bucket $S --query 'Rules[0].Status' --output text)"
chk "004 CA-4 retención 30/7" '^30\s+7$' "$(aws s3api get-bucket-lifecycle-configuration --bucket $S --query 'Rules[0].[Expiration.Days,NoncurrentVersionExpiration.NoncurrentDays]' --output text)"
spol="$(aws s3api get-bucket-policy --bucket $S --query Policy --output text)"
chk "004 CA-5 solo HTTPS" 'Deny' "$spol"
chk "004 CA-5 condición SecureTransport" 'aws:SecureTransport' "$spol"
stags="$(aws s3api get-bucket-tagging --bucket $S --output text)"
for k in project env owner; do
  chk "004 CA-7 etiqueta $k en bucket" "$k" "$stags"
done

echo
if [ "$fallos" -eq 0 ]; then echo "TODO OK"; exit 0; else echo "$fallos criterio(s) fallaron"; exit 1; fi
