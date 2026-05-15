---
slug: otto-for-everyone
id: hadihgfs085x
type: challenge
title: Otto for Everyone
teaser: Free shoppers and premium shoppers want different things. Give them different
  Ottos with variations and targeting.
notes:
- type: text
  contents: Premium ToggleWear members get the white-glove treatment everywhere else
    on the site — Otto should be no exception. In this challenge you'll add a second
    variation backed by a more capable model, then target it to premium shoppers.
tabs:
- id: a2h2cnix35xw
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: 5qjvd5b0htc7
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: jfhxfxbweaqh
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 900
enhanced_loading: null
---

# Two audiences, two Ottos

Free shoppers and premium ToggleWear members get different treatment everywhere else on the site. Otto should be no exception. Premium customers get more time, more detail, and a more capable model behind the answers.

We're going to:

1. Add a second variation backed by **Claude Sonnet 4.5** with a richer premium-tier prompt.
2. Add a **targeting rule** that routes premium customers to that variation. Free shoppers keep getting the Haiku-backed Otto from the earlier challenges.
3. Test by flipping the user-tier dropdown on ToggleWear.

# Add the premium variation

Open the [LaunchDarkly](#tab-0) tab. Go to **AI Configs** → **Otto Assistant**.

1. Click **Add variation**. <!-- VERIFY: location of add-variation control -->
2. For **Name**, enter:
```text
Otto v2 (Premium)
```
3. For **Key**, confirm or enter:
```text
otto-premium
```
4. Under **Model**, pick **Anthropic Claude Sonnet 4.5**. <!-- VERIFY: model picker UX -->
5. Under **Messages**, add a **system** message with:

```text
{{ldsnippet.brand-voice}}

You work at ToggleWear and you're talking to a premium customer. Take a little more time with them. Offer thoughtful recommendations, mention complementary items when relevant, and share interesting product details (materials, care, the story behind a design). You can be a bit warmer and more conversational.

{{ldsnippet.safety-rules}}
```

<!-- VERIFY: snippet-reference syntax. Same caveat as Challenge 03 — adjust if the UI uses a different token. -->

6. Click **Save**.

Note what we just did: the premium prompt **reuses** the `brand-voice` and `safety-rules` snippets from Challenge 03. If marketing tweaks the brand voice tomorrow, both variations pick it up automatically.

# Route premium shoppers to the premium Otto

Click the **Targeting** tab. Make sure the environment selector reads **test**.

1. Under **Targeting rules**, click **Add rule**. <!-- VERIFY: rules section label -->
2. Build the clause: **User** **tier** **is one of** **premium**. <!-- VERIFY: clause builder UX (context kind, attribute, op, values) -->
3. For the **serve** dropdown, pick **Otto v2 (Premium)**.
4. Leave the **default rule** (fallthrough) as **Otto v1 (Born)** — free shoppers and anyone without a tier still get the Haiku Otto.
5. Click **Review and save**. <!-- VERIFY: save button label / confirmation flow -->

# See it work

Open the [ToggleWear](#tab-1) tab. The header has a **Logged in as** dropdown. It defaults to **Free user**.

1. With **Free user** selected, click **Chat with Otto** and ask a question:
```text
What's good for cold weather?
```
Otto should be brief and friendly — that's the Haiku-backed Born variation.

2. Close the chat. Change the dropdown to **Premium user**.

3. Re-open the chat (or refresh the page) and ask the same question. Otto should answer at more length, mention complementary items, and feel a bit warmer — that's the Sonnet-backed Premium variation, served because the LaunchDarkly context now has `tier: "premium"` and the rule you just added matches it.

The app's code didn't change. The variation you served changed because LaunchDarkly evaluated the targeting rule against the context.

Click **Check** when you're satisfied.
