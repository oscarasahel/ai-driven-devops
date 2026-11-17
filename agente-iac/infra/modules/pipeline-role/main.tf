terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}

variable "role_name" {
  description = "Nombre del rol de pipeline."
  type        = string
}

variable "bucket_arn" {
  description = "ARN del bucket al que el rol puede acceder (único recurso permitido)."
  type        = string
}

variable "trusted_service" {
  description = "Servicio que puede asumir el rol (marcador; sustituir por la identidad real del pipeline)."
  type        = string
  default     = "ec2.amazonaws.com"
}

data "aws_iam_policy_document" "assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = [var.trusted_service]
    }
  }
}

data "aws_iam_policy_document" "bucket_rw" {
  statement {
    sid       = "ListBucket"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [var.bucket_arn]
  }

  statement {
    sid       = "ReadWriteObjects"
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${var.bucket_arn}/*"]
  }
}

resource "aws_iam_role" "this" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

resource "aws_iam_policy" "bucket_rw" {
  name   = "${var.role_name}-bucket-rw"
  policy = data.aws_iam_policy_document.bucket_rw.json
}

resource "aws_iam_role_policy_attachment" "bucket_rw" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.bucket_rw.arn
}

output "role_arn" {
  description = "ARN del rol de pipeline."
  value       = aws_iam_role.this.arn
}

output "policy_arn" {
  description = "ARN de la política de acceso al bucket."
  value       = aws_iam_policy.bucket_rw.arn
}
