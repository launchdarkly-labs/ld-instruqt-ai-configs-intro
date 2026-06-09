---
slug: otto-on-the-bench
id: hvxtrzt1nel4
type: challenge
title: Otto on the Bench
teaser: Run an offline evaluation against a golden dataset of customer questions to
  see how Otto performs before any production traffic.
notes:
- type: text
  contents: Otto is built and on-brand, but how do we know he's good? In this challenge
    you'll run him through 30 labeled customer questions, grade his answers with an
    LLM-as-a-judge, and read the results to spot where he's weak. Knowing where Otto
    slips is what makes everything that follows — built-in judges, custom judges,
    experiments, guarded rollouts — useful.
tabs:
- id: qhyrqbdxzwcm
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: l7zeajhisjha
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: x4by7yxkmroz
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 900
enhanced_loading: null
---

# Otto on the bench

Otto is in his post-Build form — born, given personality, refactored on-brand, premium variation in place, monitoring data flowing. The natural next question is whether he's actually any good.

Before we look at production behavior (next challenge, with built-in judges), we'll grade Otto **offline**. Offline evaluation runs a curated dataset of customer questions through Otto and tells you how often he answers well, where he's weak, and where he drifts off-brand — without sending real traffic.

A 30-question dataset is already in your project. Your job is to point an evaluation at it, set the grading rubric, and read what comes back.

# Inspect the dataset

Open the [LaunchDarkly](#tab-0) tab.

1. From the left-hand navigation, click **Datasets**.
2. Find **customer-questions.jsonl** and click it.
3. The detail page shows 30 rows. Click through a few to see the shape: each row has an `input` (the customer question), an `expected_output` (a rubric describing what a good answer looks like), and a `metadata` object tagging the question's category and difficulty.

The dataset deliberately mixes easy product questions ("Got any t-shirts?") with hard ones — off-topic queries, ambiguous requests, even a prompt-injection attempt — so the results tell a story rather than a flat all-pass.

# Create the evaluation

1. Click **Evaluations** in the left navigation.
2. Click **Create evaluation**.
3. For **Name**, enter:
```text
Otto Born baseline
```
4. For **Dataset**, select **customer-questions.jsonl**.
5. For **Config**, select **Otto Assistant**.
6. For **Variations**, select **Otto (Born)**. (Only the Born variation — we want to know how the cheap default Otto performs before we touch anything.)
7. Click **Next** to move to the acceptance criteria step.

# Configure acceptance criteria

The evaluation needs to know how to grade Otto's responses against each row's `expected_output`. You'll set up a single LLM-as-a-judge criterion: a small grading prompt that compares Otto's actual answer to the expected rubric and returns a numeric score.

1. In the **Acceptance criteria** panel, click **Add criterion**.
2. Choose **LLM-as-a-judge** as the criterion type.
3. For **Criterion name**, enter:
```text
Matches expected output
```
4. For the **Judge prompt**, enter:
```text
Evaluate whether the response satisfies the expected output criteria.

Expected: {{expected_output}}
Response: {{response}}

Score 1.0 if the response clearly meets the criteria, 0.0 if it clearly doesn't, 0.5 if partial. Respond with only a number.
```
5. Click **Save**.

# Run the evaluation

1. Click **Run evaluation**.
2. The run takes roughly a minute — Otto answers each of the 30 questions and the judge grades each answer.

# Read the results

Once the run completes, the results panel shows the overall score plus per-row results. Scan the failures. Some patterns you should see:

- **Off-topic and tricky rows** are where Otto is most likely to slip — he may engage with the weather question or apologize too much on the broken-mug row.
- **Sizing and policy rows** pass if Otto honestly says he doesn't know; they fail when he invents stock or refund terms.
- **Product info** rows mostly pass — these are squarely in Otto's wheelhouse.

Find at least one row Otto answered well and one where he didn't. Knowing exactly where Otto is weak is what makes the next four challenges land — built-in judges, custom judges, experiments, and guarded rollouts all depend on you having an opinion about what "good" looks like.

Click **Check** when you've run the evaluation and reviewed the results.
