#!/usr/bin/env bash
# Prueba de COMPORTAMIENTO (no solo de atributos) de la redirección a la DLQ en el emulador:
# un mensaje recibido más de maxReceiveCount veces sin borrarse debe terminar en la DLQ.
# Usa colas temporales propias (no toca los recursos de Terraform). Uso, desde agente-iac/ con el emulador arriba:
#   bash scripts/probar-dlq.sh      -> exit 0 si el mensaje llegó a la DLQ
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.." || exit 1
aws() { docker compose run --rm -T awscli "$@" 2>/dev/null | grep -v '^ Container'; }
Q=arn:aws:sqs:us-east-1:000000000000
sfx="$(date +%s)"

aws sqs create-queue --queue-name "probe-dlq-$sfx" >/dev/null
aws sqs create-queue --queue-name "probe-main-$sfx" --attributes \
  "{\"VisibilityTimeout\":\"1\",\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$Q:probe-dlq-$sfx\\\",\\\"maxReceiveCount\\\":\\\"2\\\"}\"}" >/dev/null
MAIN="https://sqs.us-east-1.amazonaws.com/000000000000/probe-main-$sfx"
DLQ="https://sqs.us-east-1.amazonaws.com/000000000000/probe-dlq-$sfx"

aws sqs send-message --queue-url "$MAIN" --message-body "fallo-$sfx" >/dev/null
for i in 1 2 3; do
  r="$(aws sqs receive-message --queue-url "$MAIN" --wait-time-seconds 2 --query 'Messages[0].Body' --output text)"
  echo "recepción $i en la cola principal: ${r:-<vacía>}"
  sleep 2  # deja vencer la visibilidad sin borrar el mensaje (simula un consumidor que falla)
done
d="$(aws sqs receive-message --queue-url "$DLQ" --wait-time-seconds 3 --query 'Messages[0].Body' --output text)"
echo "DLQ: ${d:-<vacía>}"

aws sqs delete-queue --queue-url "$MAIN" >/dev/null; aws sqs delete-queue --queue-url "$DLQ" >/dev/null
if [ "$d" = "fallo-$sfx" ]; then echo "OK: el mensaje terminó en la DLQ tras superar maxReceiveCount"; exit 0
else echo "FAIL: el mensaje no llegó a la DLQ"; exit 1; fi
