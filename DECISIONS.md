# DECISIONS.md

This file records every meaningful decision made during planning, with the reasoning behind it. When Claude Code (or any contributor) is tempted to reopen a decision, they should read the rationale here first.

Format: one decision per section, dated, with options considered and reason for the chosen path. Add new decisions to the bottom as they arise.

---

## Track scope and audience

**Decision:** Six substantive hands-on labs (plus welcome, two quizzes, wrap-up = nine challenges total) covering: AI Config creation, prompt iteration, prompt snippets, variations & targeting, monitoring, and guarded rollout.

**Audience:** Developers — both LaunchDarkly evaluators and existing LD customers expanding into AI use cases. Assumes LD fundamentals are known.

**Rationale:** This is a 100-level introduction to AI Configs. The six concepts above are the product's core surface area minus agents (deferred). Targeting developers rather than mixed audiences lets us assume technical literacy and skip foundational LD content.

**Options considered:**
- *Comprehensive intro covering everything including agents.* Rejected: too much for 2 hours; agent configs deserve their own 200-level track.
- *Narrow focus on a single concept (e.g. "swap models without redeploying").* Rejected: doesn't give a complete enough picture for evaluators to understand the product.

---

## Track length and cadence

**Decision:** 2-hour presenter-led format with slide-based lecture interleaved between labs; same content runs ~1 hour self-paced. 6 labs + 2 quizzes + welcome + wrap-up = 9 total Instruqt challenges.

**Rationale:** Matches the reference track's pattern and the requested delivery profile. Quizzes serve as natural break points for presenters and as mental consolidation for self-paced learners.

---

## App architecture: single Python process serving frontend + API

**Decision:** One FastAPI process serves both the HTML/JS frontend (as static files) and the `/chat` API endpoint on port 3000. AI Config evaluation and Bedrock calls happen server-side in Python; the JS frontend only handles UI.

**Rationale:**
- The reference track's app is a single process on port 3000; matching this means learners' muscle memory carries over.
- AI Configs evaluation belongs server-side regardless — prompts and SDK keys shouldn't be in the browser.
- Single repo, single language to edit per challenge (server-side Python for AI Configs concepts; the JS exists but learners barely touch it).
- One process = simpler VM image, fewer ports, fewer ways to break.

**Options considered:**
- *Separate Python API + static JS frontend on different ports.* Rejected: more moving parts for no learning gain.
- *Node/Next.js stack matching the reference track exactly.* Rejected: the operator chose Python for server-side, and that's the more idiomatic stack for AI Configs SDK usage anyway.

---

## Tech stack: Python (FastAPI) + vanilla JavaScript

**Decision:** Server is FastAPI. Client is vanilla JS — no framework, no build step.

**Rationale:** The operator specified Python and "plain JavaScript" for simplicity, given learners will copy/paste code in some challenges. Vanilla JS is easier to read and modify in a code editor without tooling. FastAPI was chosen over Flask because of native async support (Bedrock calls benefit) and cleaner type-hint ergonomics.

---

## LLM provider: AWS Bedrock

**Decision:** AWS Bedrock is the sole LLM provider. Models used: Claude Haiku (default Otto), Claude Sonnet (premium Otto), Amazon Nova Pro (cross-vendor variation in the guarded-rollout challenge).

**Rationale:**
- Single AWS account with IAM-controlled access means easier credential management for Instruqt's secrets system.
- Bedrock's catalog lets us tell the "swap models without redeploying" story credibly with three distinct options.
- Mixing Anthropic Claude (Haiku, Sonnet) with Amazon Nova in challenge 7 gives the cross-family demo real teeth — the judge catches a regression from a genuinely different model family, not just a different size.

**Options considered:**
- *Direct Anthropic API.* Rejected: only one model family available, weaker variation story.
- *Cross-family from the start (e.g. Haiku vs Nova in challenge 5).* Rejected: in challenge 5 we want to show "premium variation with better model"; same-family-different-size (Haiku → Sonnet) tells that story more clearly. Save the family swap for challenge 7 where it serves the judge/guarded-rollout narrative.

---

## Retail-shop fiction: ToggleWear, single page, no commerce

**Decision:** The site is "ToggleWear," a fictional retailer selling LaunchDarkly-branded apparel. Single page: header (logo + user-tier dropdown), product grid of 6-8 items, Otto the shopping-assistant chat widget. No cart, checkout, auth, or commerce.

**Rationale:**
- A retail shop is instantly legible — every learner understands the use cases (recommendations, support, brand voice).
- LaunchDarkly-branded apparel keeps the demo "in-family" — the brand reference is amusing without being distracting.
- Single page minimizes UI surface area; the app exists to host Otto, not to be a real store.
- No commerce functionality avoids scope creep into payment forms, user accounts, etc.
- ToggleWear is deliberately *not* a fork of the legacy Toggle Outfitters app — fresh codebase, no library-rot inheritance.

---

## Otto: a shopping assistant chatbot

**Decision:** The AI surface is a chat widget named "Otto" embedded on the ToggleWear page. Otto can answer questions about products, ToggleWear policies, sizing, etc.

**Rationale:** Naming the AI gives the narrative a character. Each lab is a beat in Otto's development — born, given voice, branded, personalized, measured, governed. This carries the learner through the track with a story rather than a checklist.

---

## User-tier dropdown in the header

**Decision:** A header dropdown ("Logged in as: Free user / Premium user") that updates the LD context client-side and triggers re-evaluation server-side.

**Rationale:**
- Targeting in challenge 5 needs a way for the learner to flip user contexts.
- A dropdown looks polished on a presenter's screen and tells the targeting story visibly.
- Hardcoded URL params would work but feel hacky for a demo meant to impress.

**Options considered:**
- *Query parameter (`?user=premium`).* Rejected as too unpolished for presenter demos.
- *A full mock login flow.* Rejected: adds scope for no learning value.

---

## Cost protection: configurable turn cap per session

**Decision:** Python server enforces a turn cap per chat session, configurable via env var. Default to a value generous enough to complete the track comfortably. When exceeded, Otto returns a graceful "demo limit reached" message instead of calling Bedrock.

**Rationale:** Bedrock costs scale linearly with usage; an unattended Instruqt track being run by many learners in parallel could rack up bills via runaway loops, accidental retries, or curious learners spamming the chat. Per-session cap with env-var control gives operators a knob without redeployment.

**Open knob:** The specific default value should be set during implementation based on a realistic walkthrough of the track. Err high initially; tune down with real data.

---

## Cost protection at the model level

**Decision:** Use the cheapest viable model (Haiku) as the default; reserve Sonnet for premium-tier targeting; Nova Pro appears only in challenge 7's pre-built scenario. Traffic generator (challenge 6) sends short messages to keep token counts low.

**Rationale:** Stacking architectural choices for cost control: cheap default model + tight turn cap + short generated traffic. Cumulative protection against bill surprises.

---

## Challenge 7: judge + guarded rollout, all pre-built

**Decision:** Challenge 7's setup script creates *everything*: the Nova Pro variation with a deliberately-poor prompt, a second AI Config that acts as a "judge" scoring responses for brand-voice adherence, a metric wired to the judge's output, and the guarded rollout configuration. The learner observes the rollout proceed and watches the auto-rollback fire. A sabotage script is included for presenters to trigger the rollback dramatically on demand.

**Rationale:**
- Teaching the judge pattern from scratch would consume the entire 2-hour budget on its own. Pre-building keeps the learner focused on the *outcome* (guarded rollouts protect AI quality) not the mechanics.
- The bad prompt regression is *organic* — the judge legitimately catches a quality problem, not a contrived flag flip. This makes the demo feel real.
- A sabotage trigger lets presenters force the rollback within a class timeframe instead of waiting for organic traffic to accumulate.

**Options considered:**
- *Learner builds the judge.* Rejected: too much for one lab.
- *Skip guarded rollouts entirely, end on monitoring.* Rejected: guarded rollouts are the strongest "wow" moment for AI use cases specifically, and they're the natural narrative ending — "now you can trust the system to protect itself."
- *Simulate the regression rather than serve a real bad prompt.* Rejected: serving real bad responses through the live model is more impressive and only marginally more complex to set up.

---

## Challenge 6: traffic generator runs automatically in setup

**Decision:** Challenge 6's `setup-workstation` runs the traffic generator script automatically. The learner arrives at a populated monitoring view, no manual step required.

**Rationale:** The lesson is "use monitoring to understand AI behavior," not "run a script." Surfacing populated data immediately lets the learner spend their lab time on observation and interpretation.

---

## Lecture content: out of scope for the track

**Decision:** The track contains no lecture content. Presenters deliver conceptual framing via slides between labs. The `notes` field in each challenge's front-matter contains only a one-paragraph orientation, mirroring the reference track.

**Rationale:** The operator delivers the lecture content via PowerPoint. Embedding lectures in the track would duplicate effort, force the self-paced flow to read material a presenter would deliver verbally, and make the track harder to update.

---

## Lecture-lab split delivers the same content at 2hr or 1hr

**Decision:** Labs stand alone — they're written so a self-paced learner can complete them without the lecture preamble. The 2hr format adds slide-based lecture between labs; the 1hr format skips lecture and runs labs back-to-back.

**Rationale:** Two delivery modes, one source of truth. The constraint this places on labs: `assignment.md` prose must carry enough conceptual context that an unsupervised learner can follow it without a presenter setting up each lab.

---

## File pairing convention: `.remote` files are not authored

**Decision:** Claude Code creates only the non-`.remote` versions of each file. The Instruqt CLI generates `.remote` mirrors on publish.

**Rationale:** Extracted from inspection of the reference track — all `.remote` files were byte-identical to their counterparts, indicating CLI-generated mirrors. Authoring both creates merge conflicts on publish.

---

## VM image inputs in repo, image build done by humans

**Decision:** Claude Code produces the *inputs* for VM image building (app source, Dockerfile or Packer config, install scripts, systemd unit files) in `vm-image/`. The actual image build is performed by a human operator and registered with Instruqt.

**Rationale:** Image builds require AWS/GCP credentials and Instruqt registry access that Claude Code doesn't have. Separating "what goes in the image" (Claude Code's job) from "build and register the image" (human's job) makes the handoff explicit.

---

## Terraform provider vs. REST API for AI Configs resources

**Decision:** Prefer the `launchdarkly/launchdarkly` Terraform provider for AI Configs resources where supported. Where the provider lacks AI Configs support, fall back to REST API calls via `null_resource` + `local-exec curl`.

**Rationale:** AI Configs is a relatively new product. The Terraform provider may not yet cover every resource type. Provider-native is preferred (cleaner code, drift detection), but the REST fallback is unblocked while waiting for provider updates.

**Verification step:** During Phase 1, check the current Terraform provider documentation for AI Configs resource support and record findings in `PHASES.md` Phase 1 notes.

---

## SDK version pinning

**Decision:** Pin specific versions of `launchdarkly-server-sdk`, `launchdarkly-server-sdk-ai` (`ldai`), `boto3`, `fastapi`, and `uvicorn` in `requirements.txt`. Verify latest stable versions at implementation time via web search; do not guess from training data.

**Rationale:** AI Configs SDK is evolving rapidly. Unpinned versions cause non-reproducible failures when learners run the track months after authoring.

---

## Narrative consistency owned by NARRATIVE.md

**Decision:** A separate `NARRATIVE.md` file holds Otto's story arc, voice guide, ToggleWear brand details, and product list. All `assignment.md` files should be consistent with it.

**Rationale:** Across 9 challenges authored over multiple sessions, voice drift is a real risk. A single source of truth for narrative concerns prevents it.

---

## Phase-by-phase build with operator review gates

**Decision:** Claude Code works one phase at a time per `PHASES.md`. After each phase, work pauses for operator review before the next phase begins.

**Rationale:** Catching architecture or convention drift early is much cheaper than catching it after 9 challenges are written. Phase gates also let the operator validate against real Instruqt deployment between phases if desired.

---

## UI instructions in assignment.md: drafts subject to operator verification

**Decision:** Claude Code drafts click-by-click LaunchDarkly UI instructions in `assignment.md` files based on reading the public AI Configs docs. The operator then walks through each flow with the draft open, corrects UI specifics (button labels, menu paths, step ordering), captures screenshots, and removes `<!-- VERIFY: ... -->` markers. Phase done-when conditions require this operator verification pass before sign-off.

**Rationale:** Claude Code cannot drive a browser in this environment — it can't click through the LaunchDarkly UI to verify flows itself. Options considered:

- *Operator screen-records each flow first, Claude Code transcribes.* Higher first-draft accuracy, but expensive operator time upfront and dependent on flow being known before authoring.
- *Operator gives Claude Code an LD account.* Doesn't help in this environment — Claude Code still can't drive a browser from a chat session. Would only help with a separate browser-agent product (e.g. Claude in Chrome), which is a workflow change.
- *Claude Code hedges in prose ("navigate to roughly the configs area").* Rejected — produces unusable instructions. Learners need specifics.
- *Hybrid: confident drafts from docs + operator click-through pass.* Chosen. Lowest total operator time, highest first-draft quality given the tooling constraint.

This decision is enforced in `CLAUDE.md` ("UI instructions in assignment.md are drafts pending operator verification") and in every UI-touching phase's done-when in `PHASES.md`.

---

## LD model name → Bedrock model ID lives in the app, not the AI Config

**Decision:** LaunchDarkly's model config registry stores vendor-neutral model names like `claude-haiku-4-5`, `nova-pro`. The app's `server.py` maintains a `BEDROCK_MODEL_IDS` dict that maps each to the corresponding Bedrock model or inference-profile ID (e.g. `us.anthropic.claude-haiku-4-5-20251001-v1:0`). Adding a new model means a row in that dict — no AI Config changes needed.

**Rationale:** Discovered the hard way during Phase 3: the `modelName` passed when creating a variation is a hint, but what `cfg.model.name` returns from the SDK is the model config's vendor-neutral `modelId`. Bedrock needs the full model/profile ID. The cleanest place for that translation is the boundary where we leave LD-land and enter AWS-land — in the app's Bedrock client wrapper.

**Side benefit:** The LD AI Config stays vendor-agnostic. If we ever swap Bedrock for OpenAI direct, only `BEDROCK_MODEL_IDS` (or its OpenAI equivalent) changes — the AI Configs and variations don't.

---

## Per-challenge Terraform modules are independent and hybrid

**Decision:** Each challenge has its own `terraform/challenge-NN/` module with its own state. Modules use:

- `launchdarkly_*` resources for NEW resources introduced by that challenge (e.g. challenge-01 creates the Haiku model_config, the AI Config, and the first variation; challenge-05 creates the Sonnet variation; challenge-07 creates Nova Pro model_config, the Stiff variation, the judge config, and the metric).
- `null_resource` + `local-exec curl` for: updates to resources owned by earlier challenges' modules (which Terraform can't touch from a different module without `terraform import`), and for resources the provider doesn't yet expose (snippets, AI Config targeting rules, guarded rollouts, AI Config `evaluationMetricKey`).

**Rationale:** Each challenge's solve must produce the END STATE of that challenge regardless of whether prior challenges were completed in code or skipped. Terraform's per-module state model doesn't share resources across modules, so updates to "already-managed" resources need to go through either `terraform import` (operationally heavy) or REST API (lightweight). REST via `null_resource` won.

**Side effect:** Some idempotency is on us — for example, challenge-03's snippet POST has `|| echo "(may already exist)"` because the second apply would 409. Worth the trade-off for state simplicity.

---

## server.py BEFORE state + marker-based paste pattern

**Decision:** `server.py` ships from the VM image in a BEFORE state: imports/init/helpers/turn-cap pre-wired, but `/chat`'s body is a clearly-marked stub block returning a canned "not wired yet" response. Challenge 01 has the learner replace the stub with ~30 lines of AI Config + Bedrock eval logic. The solve script applies the same paste programmatically using a Python script that finds the markers and substitutes the block.

A second marker (`# ─── Challenge 07 judge injects below this marker ──────`) sits at the bottom of the post-Challenge-01 code. Challenge 07's setup script finds it and injects the judge integration block.

**Rationale:** Two-step staged code injection keeps each challenge's setup self-contained while making it possible for later challenges to extend the same file. Pure Python `find/replace` on stable comment markers is more robust than line-number-based patching and survives the learner doing the paste manually vs. via solve.

**Trade-off:** The marker comments persist in the final server.py code. Acceptable — they're inert single-line comments with clear purpose.

---

## AI Config snippet-reference syntax: deferred to operator verification

**Decision:** Phase 4 / Challenge 03 introduces prompt snippets via REST (the Terraform provider doesn't expose them yet). The reference syntax for embedding a snippet in a variation message — i.e. what token the UI/SDK expects — isn't documented anywhere I could find at authoring time. The placeholder `{{ldsnippet.<key>}}` is used throughout, with `<!-- VERIFY -->` markers in the assignment and Terraform calling it out. Operator confirms or fixes during click-through.

**Rationale:** Spent significant time searching docs, OpenAPI, and SDK source — no canonical reference. Authoring against a placeholder is faster than blocking the whole phase on this single detail; the marker pattern (already a documented project convention) handles the verification gap.

**Where this lives:** `instruqt/03-otto-on-brand/assignment.md`, `instruqt/05-otto-for-everyone/assignment.md`, `terraform/challenge-03/main.tf`, `terraform/challenge-05/main.tf`. Update all four locations together when the real syntax is confirmed.

---

## Guarded rollout configured by the learner, not pre-built

**Decision:** Phase 7's setup pre-builds everything *except* the guarded rollout itself: the Nova Pro Stiff variation, the judge AI Config + metric, the server-side judge integration, and a low-rate background traffic generator. The learner configures the guarded rollout in the LD UI as the lab's actionable centerpiece.

**Rationale:** Two reasons. First, LaunchDarkly's REST API for starting a guarded rollout isn't publicly documented at authoring time — the OpenAPI spec includes the `GuardedReleaseConfig` schema and `ReleaseGuardianConfiguration` but no path uses them in the spec. Reverse-engineering the UI's API calls was deferred. Second, configuring the rollout in the UI *is* the most important learning moment of the track — making the learner do it themselves reinforces the workshop's main lesson.

**Side script:** `traffic-generator/sabotage.py` exists as a presenter escape hatch — emits low judge scores directly via `ld_client.track()` to force a regression detection when organic background traffic is too slow.

**Side benefit:** Makes the lab demonstrably "real" — the learner can see the rollback fire from their own configuration, not from a pre-built one that magically works.

---

## Judge invocation: SDK eval + manual Bedrock call

**Decision:** The judge integration in `server.py` (added by Challenge 07's setup patch) calls `ai_client.judge_config(...)` to evaluate the `otto-response-judge` AI Config (which interpolates the `{{response}}` template variable with Otto's answer), then calls `bedrock.converse()` manually with the resulting model and messages. The 1-5 score is parsed from the response text and emitted via raw `ld_client.track("otto-quality-score", ...)` rather than `tracker.track_judge_result(...)`.

**Rationale:** The `ldai` SDK supports a higher-level judge flow via `create_judge()` + `judge.evaluate()`, but it relies on an AI Provider plugin system (langchain, openai). There's no `ldai_bedrock` provider as of authoring. Writing a custom provider was scoped out. Manual Bedrock invocation works fine and stays transparent to the workshop's audience — the code reads exactly like the regular Otto eval.

---

## Traffic generator skips Bedrock entirely

**Decision:** `traffic-generator/generate_traffic.py` and `background_traffic.py` evaluate the AI Config to get a real tracker, then emit synthetic `track_duration`, `track_tokens`, `track_success`, and `track_feedback` events with values weighted per model. They do NOT call Bedrock.

**Rationale:** Real Bedrock calls would make 120 sessions take ~10 minutes and cost real money per learner. The monitoring view only consumes the LD-side metric events, so skipping Bedrock costs nothing in terms of what the lab shows. Weights are tuned so Sonnet looks visibly better than Haiku in the dashboard, and Nova Pro Stiff looks worse — the comparison is what matters, not the absolute numbers.

**Side benefit:** Same generator works as a sabotage tool — see `sabotage.py`, which is just the metric-emission path without the eval boilerplate.
