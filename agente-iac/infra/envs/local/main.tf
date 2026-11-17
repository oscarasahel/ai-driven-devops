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
      env        = "local"
      managed_by = "terraform"
    }
  }
}

variable "smoke_bucket_name" {
  description = "Nombre del bucket de prueba de humo."
  type        = string
  default     = "agente-iac-smoke-test"
}

resource "aws_s3_bucket" "smoke" {
  bucket = var.smoke_bucket_name
}

output "smoke_bucket_arn" {
  description = "ARN del bucket de prueba de humo."
  value       = aws_s3_bucket.smoke.arn
}
