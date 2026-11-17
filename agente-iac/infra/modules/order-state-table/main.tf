terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}

variable "table_name" {
  description = "Nombre de la tabla de estado de pedidos."
  type        = string
}

variable "ttl_attribute" {
  description = "Atributo numérico (epoch en segundos) que marca la expiración del registro."
  type        = string
  default     = "expires_at"
}

resource "aws_dynamodb_table" "orders" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "order_id"

  attribute {
    name = "order_id"
    type = "S"
  }

  ttl {
    attribute_name = var.ttl_attribute
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }
}

output "table_name" {
  description = "Nombre de la tabla."
  value       = aws_dynamodb_table.orders.name
}

output "table_arn" {
  description = "ARN de la tabla."
  value       = aws_dynamodb_table.orders.arn
}
