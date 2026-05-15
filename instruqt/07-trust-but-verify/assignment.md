---
slug: trust-but-verify
id: hj0tbpikhbgv
type: challenge
title: Trust but Verify
teaser: Try a new model behind a guarded rollout — and watch LaunchDarkly roll back
  automatically when an AI judge says the answers don't measure up.
notes:
- type: text
  contents: Otto wants to try a new model. But what if it goes wrong? In this final
    challenge you'll roll out a third variation behind a guarded rollout backed by
    an AI judge — and see LaunchDarkly automatically pull the plug when quality slips.
tabs:
- id: od2xl8x8ek6e
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: gjottwyvrahj
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: ocvshb8njmpm
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 1200
enhanced_loading: null
---

# Otto wants to try a new model

Marketing has heard about Amazon Nova Pro and asked us to test it for Otto. Cool, except: a new model could be off-brand. Could be too formal. Could be too verbose. Could be wrong. We're going to roll it out *cautiously* — and we're going to have LaunchDarkly automatically pull the plug if anything goes wrong.

Setup has already done four things for you:

1. **Created a new variation, "Otto v3 (Stiff)", backed by Nova Pro** with a deliberately corporate prompt. (We want this variation to score badly. The point of the lab is to watch LaunchDarkly catch the regression.)
2. **Created a *judge* AI Config** — `Otto Response Judge` — that scores each Otto answer 1-5 for brand voice. The judge is a small Haiku-backed Otto that grades the bigger Otto's answers.
3. **Wired the server** so every time Otto answers a chat, the judge scores the answer and records it as an `otto-quality-score` metric event.
4. **Started a low-rate background traffic generator** so the rollout has organic data to evaluate against.

Take a moment to look at the pre-built pieces before you start the rollout.

# Tour the pre-built pieces

Open the [LaunchDarkly](#tab-0) tab.

1. **The Stiff variation.** Go to **AI Configs** → **Otto Assistant** → **Variations**. You should see three: Born, Premium, and **Otto v3 (Stiff)**. Open Stiff and look at its prompt — notice how corporate it is compared to the brand voice. <!-- VERIFY: variations tab UX -->

2. **The judge.** Go to **AI Configs** → **Otto Response Judge**. Open the **Default** variation. Notice the system message describing Otto's brand voice and the rubric. The `{{response}}` placeholder is where the SDK substitutes Otto's answer at evaluation time. <!-- VERIFY: judge config detail UX -->

3. **The metric.** Go to **Metrics** in the left nav. Find **Otto Quality Score** (key: `otto-quality-score`). Open it — notice it's a numeric custom metric with success criteria **HigherThanBaseline**. <!-- VERIFY: metrics nav path -->

4. **The wiring.** Back on the Otto Assistant config, open **Settings**. The **Evaluation metric** should be set to **Otto Quality Score**. That's what makes the guarded rollout know what "regression" means. <!-- VERIFY: settings tab name and field label -->

# Start the guarded rollout

This is the part you do yourself, because it's the most important moment in the track.

Open Otto Assistant → **Targeting** (environment: **test**).

1. Click the **default rule** (the one currently serving Otto v1 (Born) to everyone). <!-- VERIFY: default rule click target -->
2. Change the **Serve** option to **Guarded rollout**. <!-- VERIFY: exact UI label for guarded rollout option -->
3. Pick:
   - **Initial variation**: Otto v1 (Born)
   - **New variation**: Otto v3 (Stiff)
   - **Metric**: Otto Quality Score (should already be selected based on the Evaluation metric)
   - **Roll back on regression**: **On**
   - **Stages**: leave the defaults <!-- VERIFY: rollout stage UX -->
4. Click **Start rollout**. <!-- VERIFY: start button label -->

# Watch it work

The background traffic generator is feeding ~one chat per two seconds into the system, weighted so the Stiff variation scores poorly (1-3) while Born/Premium score well (4-5).

Switch to the **Releases** view for Otto Assistant (or the guarded rollout panel — wherever LaunchDarkly shows the rollout's progress). <!-- VERIFY: where rollout progress lives in the UI -->

Within a few minutes, one of two things will happen:

- **The rollout proceeds, then rolls back.** The metric divergence between Stiff and Born exceeds the regression threshold, LaunchDarkly detects it, and the rollout reverts to 100% Born. No human action required. You'll see a regression event in the rollout history.
- **You get impatient.** That's fair. Open a terminal in the [Code Editor](#tab-2) tab and run:

```bash
/opt/ld/ai-configs-intro/app/.venv/bin/python /opt/ld/ai-configs-intro/traffic-generator/sabotage.py
```

That emits 60 score-of-1 events. Within a minute, the rollout should detect the regression and roll back.

# What just happened

You shipped a known-bad variation to production, with safety on. LaunchDarkly:

- Sampled a small percentage of traffic to the new variation.
- Watched the quality-score metric for that variation against the metric for the baseline.
- Detected statistically that the new variation was performing worse.
- **Rolled back automatically** to the safe variation, with no human in the loop.

That's the workshop's center of gravity. AI Configs let you treat AI features like any other feature: ship them with control, observability, and a safety net.

Click **Check** when the rollout has either completed or rolled back.
