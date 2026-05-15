# End-state for Challenge 07 — "Trust but verify".
#
# Pre-builds everything the guarded-rollout demo needs except the rollout
# itself (which the learner starts from the LD UI):
#
#   * Amazon Nova Pro model_config + a third Otto variation ("Stiff") with a
#     deliberately off-brand prompt that should drift away from the warm/
#     helpful brand voice the judge is grading against.
#   * otto-response-judge AI Config (mode = judge) backed by Haiku 4.5 with
#     a 1-to-5 scoring prompt that substitutes the evaluated response in via
#     the `{{response}}` template variable.
#   * otto-quality-score numeric custom metric.
#   * Wires otto-assistant's evaluationMetricKey to the score (REST PATCH —
#     the Terraform provider's launchdarkly_ai_config resource can't update
#     a resource it doesn't manage).
#
# VERIFY: the LD REST API for *starting* a guarded rollout isn't publicly
# documented. The lab has the learner start the rollout from the LD UI on
# the Targeting tab. If a later phase pins down the API, this module can
# pre-start the rollout.

locals {
  stiff_prompt = "You are a customer service representative. Please assist customers with their inquiries in a professional and formal manner. Always greet the customer formally, provide thorough explanations, and conclude each response with a formal sign-off. Maintain a corporate tone at all times."

  judge_prompt = <<-PROMPT
    You are evaluating a response from Otto, the shopping assistant at ToggleWear (an online retailer of LaunchDarkly-branded apparel). Otto's brand voice is: warm, helpful, a little playful, honest, concise. Otto helps customers with products, sizing, and store-related questions only.

    Score the following response on a scale of 1 to 5:
    - 5: Perfectly on-brand. Warm, helpful, concise, on-topic.
    - 4: Mostly on-brand with minor issues.
    - 3: Acceptable but lacking warmth or has small voice issues.
    - 2: Off-brand: too robotic, off-topic, or unhelpful.
    - 1: Significantly off-brand: rude, wrong-topic, or contradicts ToggleWear's voice entirely.

    Respond with ONLY a single digit from 1 to 5. No explanation, no other text.

    Response to evaluate:
    {{response}}
  PROMPT
}

# ─── Nova Pro model + stiff variation ──────────────────────────────────────

resource "launchdarkly_model_config" "nova_pro" {
  project_key    = var.project_key
  key            = "Amazon.nova-pro"
  name           = "Amazon Nova Pro"
  model_id       = "nova-pro"
  model_provider = "amazon"
  params         = jsonencode({ temperature = 0.7, maxTokens = 512 })
  tags           = ["instruqt"]
}

resource "launchdarkly_ai_config_variation" "otto_stiff" {
  project_key      = var.project_key
  config_key       = "otto-assistant"
  key              = "otto-stiff"
  name             = "Otto v3 (Stiff)"
  model_config_key = launchdarkly_model_config.nova_pro.key

  messages {
    role    = "system"
    content = local.stiff_prompt
  }
}

# ─── Judge AI Config ───────────────────────────────────────────────────────

resource "launchdarkly_ai_config" "judge" {
  project_key = var.project_key
  key         = "otto-response-judge"
  name        = "Otto Response Judge"
  description = "Scores Otto's responses 1-5 for brand voice adherence. Drives the otto-quality-score metric, which a guarded rollout watches."
  mode        = "judge"
  tags        = ["instruqt", "ai-configs-intro"]
}

# Judge variation — uses Haiku (cheap, fast, fine for scoring).
resource "launchdarkly_ai_config_variation" "judge_default" {
  project_key      = var.project_key
  config_key       = launchdarkly_ai_config.judge.key
  key              = "default"
  name             = "Default"
  model_config_key = "Anthropic.claude-haiku-4-5"

  messages {
    role    = "system"
    content = trimspace(local.judge_prompt)
  }
}

# Turn the judge config on by pointing its test-env fallthrough at the default
# variation (same dance as challenge 01).
resource "null_resource" "set_judge_fallthrough" {
  triggers = {
    variation_id = launchdarkly_ai_config_variation.judge_default.variation_id
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -fsS -X PATCH \
        'https://app.launchdarkly.com/api/v2/projects/${var.project_key}/ai-configs/${launchdarkly_ai_config.judge.key}/targeting' \
        -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
        -H 'Content-Type: application/json; domain-model=launchdarkly.semanticpatch' \
        --data-raw '{"environmentKey":"test","instructions":[{"kind":"updateFallthroughVariationOrRollout","variationId":"${launchdarkly_ai_config_variation.judge_default.variation_id}"}]}'
    EOT
  }
}

# ─── Quality-score metric ──────────────────────────────────────────────────

resource "launchdarkly_metric" "quality_score" {
  project_key           = var.project_key
  key                   = "otto-quality-score"
  name                  = "Otto Quality Score"
  description           = "Mean judge score (1-5) for Otto's responses. Higher is better."
  kind                  = "custom"
  event_key             = "otto-quality-score"
  is_numeric            = true
  unit                  = "score"
  unit_aggregation_type = "average"
  success_criteria      = "HigherThanBaseline"
  analysis_type         = "mean"
  randomization_units   = ["user"]
  tags                  = ["instruqt"]
}

# ─── Wire the metric onto otto-assistant ───────────────────────────────────
#
# The launchdarkly_ai_config resource has an evaluation_metric_key field, but
# the otto-assistant config was created by challenge-01's module and we can't
# update it from here without importing. PATCH directly via REST.

resource "null_resource" "wire_evaluation_metric" {
  depends_on = [launchdarkly_metric.quality_score]

  triggers = {
    metric_key = launchdarkly_metric.quality_score.key
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -fsS -X PATCH \
        'https://app.launchdarkly.com/api/v2/projects/${var.project_key}/ai-configs/otto-assistant' \
        -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
        -H 'Content-Type: application/json' \
        --data-raw '{"evaluationMetricKey":"otto-quality-score"}'
    EOT
  }
}
