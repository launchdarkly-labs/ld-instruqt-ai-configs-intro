# End-state for Challenge 05 — "Otto for everyone".
#
# Adds a premium-tier variation (Sonnet 4.5) and a targeting rule that routes
# contexts with `tier: "premium"` to it. Free-tier shoppers keep getting the
# Haiku-backed Otto from earlier challenges.
#
# Assumes Challenges 01-03 have been completed: otto-assistant exists with
# otto-born as the test fallthrough, and brand-voice + safety-rules snippets
# exist in the project.
#
# Anthropic.claude-sonnet-4-5 is a GLOBAL model config (shipped by LD), so
# unlike Haiku we don't have to create it ourselves.
#
# VERIFY: the `{{ldsnippet.<key>}}` reference syntax is a placeholder shared
# with challenge-03. Adjust here too if the click-through reveals it differs.

locals {
  premium_prompt = <<-PROMPT
    {{ldsnippet.brand-voice}}

    You work at ToggleWear and you're talking to a premium customer. Take a little more time with them. Offer thoughtful recommendations, mention complementary items when relevant, and share interesting product details (materials, care, the story behind a design). You can be a bit warmer and more conversational.

    {{ldsnippet.safety-rules}}
  PROMPT
}

resource "launchdarkly_ai_config_variation" "otto_premium" {
  project_key      = var.project_key
  config_key       = "otto-assistant"
  key              = "otto-premium"
  name             = "Otto v2 (Premium)"
  model_config_key = "Anthropic.claude-sonnet-4-5"

  messages {
    role    = "system"
    content = trimspace(local.premium_prompt)
  }
}

# Add a targeting rule: contexts with tier=premium → otto-premium.
# AI Config targeting isn't yet in the Terraform provider — use semantic patch.
resource "null_resource" "add_premium_rule" {
  triggers = {
    variation_id = launchdarkly_ai_config_variation.otto_premium.variation_id
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -fsS -X PATCH \
        'https://app.launchdarkly.com/api/v2/projects/${var.project_key}/ai-configs/otto-assistant/targeting' \
        -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
        -H 'Content-Type: application/json; domain-model=launchdarkly.semanticpatch' \
        --data-raw "$(jq -n --arg vid "${launchdarkly_ai_config_variation.otto_premium.variation_id}" '
          {
            environmentKey: "test",
            instructions: [{
              kind: "addRule",
              variationId: $vid,
              clauses: [{
                contextKind: "user",
                attribute: "tier",
                op: "in",
                negate: false,
                values: ["premium"]
              }]
            }]
          }')"
    EOT
  }
}
