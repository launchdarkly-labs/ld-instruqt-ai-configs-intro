locals {
  project_key  = "ai-configs-intro-${var.sandbox_id}"
  project_name = "AI Configs Intro — ${var.sandbox_id}"
}

resource "launchdarkly_project" "student" {
  key  = local.project_key
  name = local.project_name
  tags = ["instruqt", "ai-configs-intro"]

  environments {
    key   = "test"
    name  = "Test"
    color = "417505"
  }
}
