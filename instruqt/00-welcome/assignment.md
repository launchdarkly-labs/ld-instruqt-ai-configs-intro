---
slug: welcome
id: u9h6ac326vm8
type: challenge
title: Welcome to ToggleWear
teaser: Meet ToggleWear, meet Otto-to-be, and get oriented before you start building.
notes:
- type: text
  contents: ToggleWear sells LaunchDarkly-branded apparel. They want an AI shopping
    assistant on the site. Over the next eight challenges you'll build, refine, brand,
    personalize, measure, and govern that assistant. His name is going to be Otto.
tabs:
- id: x4bfh4g2uh11
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: 449i812xi2h2
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: 3fzxr3qqqgtj
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 300
enhanced_loading: null
---

# Welcome

Over the next ~2 hours, you're going to build an AI shopping assistant for **ToggleWear**, a fictional online retailer of LaunchDarkly-branded apparel. The assistant's name is **Otto**. Right now Otto doesn't exist — by the end, he'll be live in the [ToggleWear](#tab-1) storefront, targeted by user tier, monitored in production, and guarded by an AI judge that auto-rolls-back regressions.

You're going to do this using **LaunchDarkly AI Configs**: prompts, models, and rollout strategy as runtime configuration instead of hardcoded values.

# What you'll do

| # | Beat |
|---|---|
| 01 | Create Otto's first AI Config and wire him into the app. |
| 02 | Change Otto's personality without redeploying. |
| 03 | Factor reusable brand voice into snippets. |
| 04 | Quick quiz to consolidate. |
| 05 | Add a premium-tier Otto, target it by user attribute. |
| 06 | Look at Otto's production data in the monitoring view. |
| 07 | Roll out a risky new model behind a judge-backed guarded rollout. |
| 08 | Wrap up. |

# Assumptions

This track assumes you already know the LaunchDarkly basics — flags, contexts, environments, targeting rules. If you don't, the [LaunchDarkly Basics](https://launchdarkly.com) track is a better starting point.

The tabs on the right will all be useful: [LaunchDarkly](#tab-0) for the LD UI, [ToggleWear](#tab-1) for the live storefront, [Code Editor](#tab-2) for `server.py` and other repo files.

# Prerequisites

This variant runs on **your own** LaunchDarkly account and **your own** AWS Bedrock access. Before you start:

- A **LaunchDarkly account** with **AI Configs** enabled.
- An **AWS account** with **Bedrock model access** enabled in the **US regions** for **Claude Sonnet 4.5**, **Claude Haiku 4.5**, **Claude 3.5 Haiku**, and **Amazon Nova Pro**. Model-access grants are not always instant — [enable them](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) *before* this lab.
- AWS credentials with `bedrock:InvokeModel`. **Long-lived IAM user keys are recommended** (temporary/SSO credentials work but can expire mid-session).

# Bring your own credentials

1. Open the [LaunchDarkly](#tab-0) tab and log in to your LaunchDarkly account.
2. **Create a project**: project dropdown → **Create project**. Name it anything (e.g. `otto-demo`). New projects come with a **Test** environment — that's the one we use.
3. Grab the project's values:
   - **SDK key**: Project settings → **Environments** → **Test** → copy the **SDK key**.
   - **Project key**: shown in Project settings (e.g. `otto-demo`).
4. **Create an API access token**: **Account settings → Authorization → Access tokens → Create token**, role **Writer** (or higher — a Reader token validates here but fails later challenges). Copy it.
5. Open the [Code Editor](#tab-2) tab, open **`app/.env`**, fill in and **save**:
   - `LD_SDK_KEY=` your Test SDK key
   - `LD_PROJECT_KEY=` your project key
   - `LAUNCHDARKLY_ACCESS_TOKEN=` your Writer token
   - `AWS_ACCESS_KEY_ID=` / `AWS_SECRET_ACCESS_KEY=` your AWS keys (`AWS_SESSION_TOKEN` *only* for temporary/SSO creds); leave `AWS_REGION=us-east-1`.

> These values are visible on screen as you paste. Use a short-lived token and revoke it after.

Click **Check** below. It confirms your project + token are valid, wires the app to your SDK key, and verifies Bedrock works.
