---
slug: welcome
id: uvbuwlh0qoyp
type: challenge
title: Welcome to AgentControl — Evaluate
teaser: Otto is built. Now make sure he's any good.
notes:
- type: text
  contents: In Build, Otto went from a placeholder line in server.py to a live,
    targeted, monitored AI shopping assistant. This track is about asking the
    next question — how do you know he's actually any good? Over the next nine
    challenges you'll test Otto offline, judge him in production, experiment on
    him, and protect customers from regressions with two different kinds of
    safety net.
tabs:
- id: s5uc943jvkal
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: iron4t6c2mfm
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: hx7rfdmakh37
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 300
enhanced_loading: null
---

# Where Otto is

Otto exists. He has a personality. The track setup has materialized the post-Build state in your project — Otto (Born) is the default variation, Otto (Premium) targets `tier: "premium"` users, the `brand-voice` and `safety-rules` snippets are in place, and ToggleWear's monitoring view already has traffic flowing through. If you completed Build, this should all feel familiar.

If you skipped Build, that's fine too — everything you need is set up.

# What you'll do

| # | Beat |
|---|---|
| 01 | Test Otto offline against a labeled dataset of customer questions. |
| 02 | Attach built-in judges (Accuracy, Relevance, Toxicity) to watch Otto in production. |
| 03 | Write a custom brand-voice judge whose criteria reuse the snippet you wrote in Build. |
| 04 | Write a second custom judge that grades Otto against the product catalog. |
| 05 | Quick quiz to consolidate. |
| 06 | Run a prompt experiment comparing two Otto variations and promote the winner. |
| 07 | Roll out a risky new model behind a guarded rollout watched by your brand-voice judge. |
| 08 | Wire an in-app loop that flips Otto's targeting when judge scores tank. |
| 09 | Wrap up. |

# What you'll leave with

By the end:

- Otto is measured by built-in judges *and* two custom judges you authored.
- The same `brand-voice` snippet you wrote in Build now drives both Otto's behavior *and* the judge's criteria — one definition of "on-brand" for the whole pipeline.
- A guarded rollout has caught a regression and rolled itself back.
- An adaptive loop in your app is watching for regressions in flight and reacting between requests.

This is Track 2 of three. **Build** introduced Otto; **Coordinate** (Track 3) will grow him into a team.

The tabs on the right: [LaunchDarkly](#tab-0) for the LD UI, [ToggleWear](#tab-1) for the live storefront, [Code Editor](#tab-2) for the small server.py patches a few challenges will ask you to paste.

Click **Check** when you're ready to start.
