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

Click **Check** below when you're ready to start.
