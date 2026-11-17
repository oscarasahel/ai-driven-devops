terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}

variable "name_prefix" {
  description = "Prefijo de nombres de los recursos."
  type        = string
}

variable "max_receive_count" {
  description = "Recepciones fallidas antes de enviar el mensaje a la DLQ."
  type        = number
  default     = 3
}

variable "dlq_retention_seconds" {
  description = "Retención de la DLQ en segundos (14 días por defecto)."
  type        = number
  default     = 1209600
}

resource "aws_sns_topic" "orders" {
  name = "${var.name_prefix}-order-events"
}

resource "aws_sqs_queue" "dlq" {
  name                      = "${var.name_prefix}-order-events-dlq"
  message_retention_seconds = var.dlq_retention_seconds
  sqs_managed_sse_enabled   = true
}

resource "aws_sqs_queue" "main" {
  name                    = "${var.name_prefix}-order-events"
  sqs_managed_sse_enabled = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })
}

# Sin esta política SNS no puede entregar a la cola (verificado en el emulador).
data "aws_iam_policy_document" "sns_to_queue" {
  statement {
    sid       = "AllowTopicToSend"
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.main.arn]

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.orders.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "main" {
  queue_url = aws_sqs_queue.main.id
  policy    = data.aws_iam_policy_document.sns_to_queue.json
}

resource "aws_sns_topic_subscription" "main" {
  topic_arn = aws_sns_topic.orders.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.main.arn

  depends_on = [aws_sqs_queue_policy.main]
}

output "topic_arn" {
  description = "ARN del tema de eventos."
  value       = aws_sns_topic.orders.arn
}

output "queue_url" {
  description = "URL de la cola principal."
  value       = aws_sqs_queue.main.id
}

output "queue_arn" {
  description = "ARN de la cola principal."
  value       = aws_sqs_queue.main.arn
}

output "dlq_arn" {
  description = "ARN de la cola de mensajes fallidos."
  value       = aws_sqs_queue.dlq.arn
}
