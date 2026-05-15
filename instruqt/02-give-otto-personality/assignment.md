---
slug: give-otto-personality
id: skejfhwvjdtc
type: challenge
title: Give Otto a Personality
teaser: Otto sounds like a robot. Marketing has notes. Iterate on his prompt — no
  redeploy required.
notes:
- type: text
  contents: Otto works, but he's bland. The whole point of AI Configs is that you
    can iterate on the prompt at runtime, without touching code. In this challenge
    you'll do exactly that — change Otto's voice from the LaunchDarkly UI and watch
    the running app pick it up.
tabs:
- id: 8kiofegocbwj
  title: LaunchDarkly
  type: browser
  hostname: launchdarkly
- id: lcc1yzzdo5o4
  title: ToggleWear
  type: service
  hostname: workstation
  port: 3000
- id: uimvrfmfykfw
  title: Code Editor
  type: service
  hostname: workstation
  port: 8080
difficulty: basic
timelimit: 600
enhanced_loading: null
---

# Otto sounds like a robot

Marketing has notes. Try opening the [ToggleWear](#tab-1) tab right now and asking Otto something — anything. He answers, but he sounds like a service desk script. We're going to fix that without redeploying a thing.

This is the whole point of AI Configs: the prompt is configuration, not code. We change it in the LaunchDarkly UI and the running app picks it up automatically.

# Edit Otto's prompt

Open the [LaunchDarkly](#tab-0) tab.

1. From the left-hand navigation, click **AI Configs**.
2. Click **Otto Assistant** to open the config.
3. Click the **Otto v1 (Born)** variation to edit it. <!-- VERIFY: how variations are opened for edit -->
4. Find the **system** message and replace its content with:

```text
You are Otto, the shopping assistant at ToggleWear — an online shop for LaunchDarkly-branded apparel. You're warm, helpful, and a little playful. You know the products, you're honest when you don't know something, and you keep answers short unless someone asks for more. Help customers find the right item, answer questions about sizing and care, and point them in the right direction when they're not sure what they want.
```

5. Click **Save**. <!-- VERIFY: save button label and confirmation flow -->

# Try the new Otto

Open the [ToggleWear](#tab-1) tab. If you have a chat session open already, click the **X** to close it, then click **Chat with Otto** to start fresh — your last session's history would otherwise still carry the old prompt's tone.

Ask Otto something the marketing team would care about:

```text
What's the difference between the Rocket Tee and the Feature Branch Crewneck?
```

He should sound less like a help desk and more like someone who'd actually work at a small online shop. You didn't restart the server. You didn't redeploy. You changed configuration in LaunchDarkly and the app picked it up on the next call.

Click **Check** when you're satisfied.
