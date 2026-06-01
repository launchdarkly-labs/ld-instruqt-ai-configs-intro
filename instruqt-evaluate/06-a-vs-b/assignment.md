---
slug: a-vs-b
id: r0tvyf5i3rff
type: challenge
title: A vs. B
teaser: Run a prompt experiment comparing two Otto variations on live traffic,
  read the results panel, and promote the winner.
notes:
- type: text
  contents: You've measured Otto in production (built-in + custom judges) and
    you've measured him offline (the dataset eval). What you haven't done yet
    is compare two versions of Otto head-to-head on real traffic. That's what
    experiments are for — split traffic, watch a metric, promote the winner.
tabs:
- id: zmgnl6gntfvo
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: r2gjohhzi92y
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: 81a8wjbxfnpq
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 900
enhanced_loading: null
---

# The experimental question

Otto's current prompt is concise — the brand-voice snippet says "keep answers short by default." But maybe being short trades off against being **helpful**. What if Otto proactively suggested one complementary item when someone asks about a product? Does that read as more helpful (good), or as more pushy and less concise (bad)?

You can argue either side from the prompts alone. That's the whole point. Run an experiment, let the brand-voice judge decide.

# Add the contender variation

Open the [LaunchDarkly](#tab-0) tab.

1. Go to **Configs → Otto Assistant**.
2. Click **Add variation**.
3. **Name**:
```text
Otto v3 (Recommender)
```
4. **Key**:
```text
otto-recommender
```
5. **Model**: **Anthropic → claude-haiku-4-5-20251001**. (Same as Born. We're isolating the prompt effect.)
6. With **System** selected, click **Load snippet** → **brand-voice**.
7. Below the snippet markup, paste:
```text
You work at ToggleWear, an online shop for LaunchDarkly-branded apparel. Help customers find products, answer questions about sizing and care, and guide them when they're not sure what they want. When recommending a product, briefly mention one complementary item from the catalog that pairs well with it — keep it natural, not pushy.
```
8. Click **Load snippet** → **safety-rules**.
9. Click **Review and save**, then **Save changes**.

Compare this prompt to **Otto v1 (Born)**'s in the same UI. The only delta is one sentence about complementary items. Everything else — brand voice, safety, model — is identical.

# Create the experiment

1. From the left-hand navigation, click **Experiments**.
<!-- VERIFY: confirm Experiments left-nav location. -->
2. Click **Create experiment**.
3. **Name**:
```text
Otto Prompt Experiment
```
4. **Key**:
```text
otto-prompt-experiment
```
5. **Environment**: **test**.
6. **Hypothesis**:
```text
Adding a one-sentence prompt to suggest a complementary item improves brand-voice score without going off-brand.
```
7. **Flag**: **otto-assistant**. Choose the **Default rule** (fallthrough) as the rule the experiment splits on.
<!-- VERIFY: confirm experiment creation lets you pick a rule and the default rule appears as an option. -->
8. **Treatments**:
   - **Control**: Otto v1 (Born), 50%, baseline.
   - **Contender**: Otto v3 (Recommender), 50%.
9. **Randomization unit**: **user**.
10. **Primary metric**: **otto-brand-voice-score**. Higher is better.
11. Click **Create experiment**.

# Start the iteration

The experiment is created in a draft state. To begin collecting data, start the first iteration.

1. On the experiment's detail page, click **Start iteration**.
<!-- VERIFY: button label. -->
2. Confirm in any dialog that appears.

A background traffic generator is already firing — about two simulated users per second, each scored by the brand-voice judge. Once the iteration starts, traffic splits ~50/50 between the two variations. After a minute or two, the results panel will have enough data to call a winner.

# Read the results

1. Click the **Results** tab on the experiment.
<!-- VERIFY: tab label. -->
2. Watch the per-treatment scores accumulate. The contender's confidence interval will start wide and tighten as samples accumulate.
3. Once the panel shows a clear winner (one treatment outside the other's confidence interval), you're done.

What you should see, given how the brand-voice judge weights "warm + helpful + concise":

- If the recommender's extra-helpful pitch outweighs the conciseness penalty, **Recommender wins**.
- If the brand voice's "keep answers short by default" dominates, **Born wins**.
- The metric tells you which is true. Reading the prompts alone wouldn't have.

# Promote the winner

1. With the winning treatment selected, click **Promote winner**.
<!-- VERIFY: confirm button label and where it lives in the results view. -->
2. The Targeting tab's Default rule should now serve the winning variation to all unmatched users.

Click **Check** when the experiment exists with at least one iteration started.
