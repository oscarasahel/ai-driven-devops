terraform {
  required_version = ">= 1.9.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}

# Endpoint, credenciales y CA llegan por variables de entorno del emulador
# (AWS_ENDPOINT_URL, AWS_SHARED_CREDENTIALS_FILE, AWS_CA_BUNDLE); ver docker-compose.yml.
provider "aws" {
  region = "us-east-1"

  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  s3_use_path_style           = true

  default_tags {
    tags = {
      project    = "agente-iac"
      env        = var.env
      owner      = var.owner
      managed_by = "terraform"
    }
  }
}

variable "owner" {
  description = "Responsable de los recursos (etiqueta owner). Obligatorio."
  type        = string

  validation {
    condition     = length(trim(var.owner, " ")) > 0
    error_message = "owner no puede estar vacío."
  }
}

variable "env" {
  description = "Nombre del entorno (etiqueta env)."
  type        = string
  default     = "local"
}

variable "name_prefix" {
  description = "Prefijo de nombres de recursos."
  type        = string
  default     = "agente-iac"
}

# --- Spec 001: bucket de artefactos y rol de pipeline ---
module "artifact_bucket" {
  source      = "../../modules/secure-bucket"
  bucket_name = "${var.name_prefix}-artifacts"
}

module "pipeline_role" {
  source     = "../../modules/pipeline-role"
  role_name  = "${var.name_prefix}-pipeline"
  bucket_arn = module.artifact_bucket.bucket_arn
}

# --- Spec 002: eventos de pedidos ---
module "order_events" {
  source      = "../../modules/order-events"
  name_prefix = var.name_prefix
}

module "order_state" {
  source     = "../../modules/order-state-table"
  table_name = "${var.name_prefix}-order-state"
}

output "artifact_bucket_arn" {
  description = "ARN del bucket de artefactos."
  value       = module.artifact_bucket.bucket_arn
}

output "pipeline_role_arn" {
  description = "ARN del rol de pipeline."
  value       = module.pipeline_role.role_arn
}

output "order_topic_arn" {
  description = "ARN del tema de eventos de pedidos."
  value       = module.order_events.topic_arn
}

output "order_queue_url" {
  description = "URL de la cola de pedidos."
  value       = module.order_events.queue_url
}

output "order_dlq_arn" {
  description = "ARN de la DLQ de pedidos."
  value       = module.order_events.dlq_arn
}

output "order_state_table" {
  description = "Nombre de la tabla de estado."
  value       = module.order_state.table_name
}
