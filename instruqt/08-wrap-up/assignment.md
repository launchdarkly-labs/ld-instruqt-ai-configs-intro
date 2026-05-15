---
slug: wrap-up
id: e4ya0cx6tntd
type: quiz
title: Wrap-Up
teaser: Otto is grown. So are you.
notes:
- type: text
  contents: You started with a "Coming Soon" page and ended with a guarded, monitored,
    targeted AI assistant. One last question to close the loop, and then you're done.
answers:
- LaunchDarkly's SDK auto-detects bad responses and switches models behind the scenes.
- The guarded rollout watched a metric (the judge's quality score) and rolled back automatically when scores regressed below baseline.
- The Bedrock API includes a built-in quality gate that rejects off-brand responses.
- The ToggleWear server cached good responses and returned them when the judge complained.
solution:
- 1
difficulty: basic
timelimit: 600
enhanced_loading: null
---
# Otto's arc

Otto started out as a placeholder line in `server.py`. From there:

- **Challenge 01** — born. First AI Config, first prompt, first words.
- **Challenge 02** — got a personality. Changed his voice without restarting the server.
- **Challenge 03** — got reusable. Brand voice and safety rules pulled into snippets shared across variations.
- **Challenge 05** — got tier-aware. Premium shoppers met a more capable Sonnet-backed Otto, free shoppers stayed with Haiku.
- **Challenge 06** — got measured. Tokens, latency, feedback all visible per variation.
- **Challenge 07** — got a guardian. A new model variation went live behind a guarded rollout watched by an AI judge — and LaunchDarkly automatically pulled the plug when quality slipped.

The point of the track wasn't to build a shopping assistant. It was to show that **AI behavior can be treated the same way you already treat features**: controllable, observable, and safe to change.

# One last question

Otto launched, gained a voice, learned to talk differently to premium customers, got monitored, and survived a botched experiment with Nova Pro — all without an emergency code change. What enabled the Challenge 07 rollback to happen without paging anyone?

# Where to go from here

- **AI Configs documentation:** [launchdarkly.com/docs/home/ai-configs](https://launchdarkly.com/docs/home/ai-configs)
- **Agents and tool use** — the natural next step beyond completion-mode configs. Deferred from this track because the API was still settling at authoring time.
- **Your own use case.** The pattern transfers: prompts you can iterate on, models you can swap, audiences you can target, metrics you can watch, rollouts you can guard.

# Otto says

> Thanks for shopping with us. Come back any time.
