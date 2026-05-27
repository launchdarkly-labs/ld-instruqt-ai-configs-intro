terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# ---------- Variables ----------

variable "account_id" {
  description = "AWS account ID where the role will be created"
  type        = string
}

variable "gcp_azp" {
  description = "The azp (authorized party) claim from the GCP service account JWT. Maps to accounts.google.com:aud."
  type        = string
}

variable "gcp_aud" {
  description = "The aud (audience) claim from the GCP JWT — the audience string you pass when requesting the token. Maps to accounts.google.com:oaud."
  type        = string
}

variable "gcp_sub" {
  description = "The sub (subject) claim from the GCP service account JWT — the numeric service account ID. Maps to accounts.google.com:sub."
  type        = string
}

# ---------- Role with trust policy ----------

data "aws_iam_policy_document" "trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = ["accounts.google.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "accounts.google.com:aud"
      values   = [var.gcp_azp]
    }

    condition {
      test     = "StringEquals"
      variable = "accounts.google.com:oaud"
      values   = [var.gcp_aud]
    }

    condition {
      test     = "StringEquals"
      variable = "accounts.google.com:sub"
      values   = [var.gcp_sub]
    }
  }
}

resource "aws_iam_role" "instruqt" {
  name               = "RoleForAccessFromInstruqt"
  assume_role_policy = data.aws_iam_policy_document.trust.json
  max_session_duration = 3600
}

# ---------- Bedrock permissions policy ----------

data "aws_iam_policy_document" "bedrock" {
  statement {
    sid    = "InvokeBedrockModels"
    effect = "Allow"

    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
      "bedrock:Converse",
      "bedrock:ConverseStream",
    ]

    resources = [
      "arn:aws:bedrock:us-east-1:${var.account_id}:inference-profile/us.anthropic.claude-sonnet-4-6",
      "arn:aws:bedrock:us-east-1:${var.account_id}:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
      "arn:aws:bedrock:us-east-1:${var.account_id}:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0",
      "arn:aws:bedrock:us-east-1:${var.account_id}:inference-profile/us.amazon.nova-lite-v1:0",
      "arn:aws:bedrock:us-east-1:${var.account_id}:inference-profile/us.amazon.nova-pro-v1:0",

      "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-6",
      "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0",
      "arn:aws:bedrock:*::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0",
      "arn:aws:bedrock:*::foundation-model/amazon.nova-lite-v1:0",
      "arn:aws:bedrock:*::foundation-model/amazon.nova-pro-v1:0",
    ]
  }
}

resource "aws_iam_role_policy" "bedrock" {
  name   = "BedrockInvokeAccess"
  role   = aws_iam_role.instruqt.id
  policy = data.aws_iam_policy_document.bedrock.json
}

# ---------- Output ----------

output "role_arn" {
  description = "ARN to plug into /opt/bin/credentials.sh on the GCP VM"
  value       = aws_iam_role.instruqt.arn
}
