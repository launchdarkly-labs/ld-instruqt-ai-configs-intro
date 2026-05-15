terraform {
  required_version = ">= 1.5.0"

  required_providers {
    launchdarkly = {
      source  = "launchdarkly/launchdarkly"
      version = "~> 2.29"
    }
  }
}

provider "launchdarkly" {
  # access_token is supplied via the LAUNCHDARKLY_ACCESS_TOKEN environment
  # variable populated by Instruqt secrets.
}
