# PHASES.md

This file is the build sequence. Claude Code works one phase at a time, stops at each phase boundary for operator review, and only begins the next phase when explicitly told to proceed.

Each phase has:
- **Goal** — what this phase accomplishes
- **Deliverables** — files/artifacts produced
- **Verification steps** — checks Claude Code performs before declaring done
- **Done-when** — explicit conditions for operator sign-off

---

## Phase 1: Foundation

**Goal:** Establish the repository skeleton, Instruqt scaffolding, and answer open verification questions about tooling.

**Deliverables:**
- Repository directory structure per `CLAUDE.md`
- `instruqt/track.yml` and `instruqt/config.yml` populated with track metadata (slug, ID, title, teaser, description, time limit, secrets, virtual machine declaration)
- `instruqt/track_scripts/setup-workstation` and `cleanup-workstation` adapted from the reference track
- Empty `instruqt/00-welcome/` through `instruqt/08-wrap-up/` folders with placeholder `assignment.md` files (front-matter only, no body)
- `terraform/student-bootstrap/` Terraform module creating the LD project and any base resources (segments, environments, etc. needed by later challenges)
- `vm-image/README.md` documenting what the image must contain and how to build it (Dockerfile or Packer config — decide and document)
- A **Phase 1 verification note** appended to this file documenting:
  - Current `launchdarkly/launchdarkly` Terraform provider version and which AI Configs resources it supports
  - Current `ldai` Python package version
  - Current `launchdarkly-server-sdk` Python version
  - Whether Bedrock cross-region inference profiles work as expected for Sonnet in the chosen region
  - The chosen AWS region

**Verification steps Claude Code performs:**
- `track.yml` and `config.yml` parse as valid YAML
- Placeholder `assignment.md` files all have valid front-matter
- Web-search confirms current SDK and provider versions; record findings

**Done-when:**
- Operator reviews the skeleton and confirms structure
- Verification notes are recorded in this file
- Open questions surfaced for operator (e.g. AWS region, any provider gaps) are answered

---

## Phase 2: App scaffold (no AI yet)

**Goal:** Build the ToggleWear single-page site with Otto's chat UI working as a mock — the chat input/output flow works end-to-end, but Otto returns hardcoded canned responses. No Bedrock integration yet.

**Deliverables:**
- `app/server.py` — FastAPI app serving `static/index.html`, with a `/chat` POST endpoint returning canned responses
- `app/static/index.html` — ToggleWear page: header with logo and user-tier dropdown, product grid of 6-8 LaunchDarkly-branded apparel items, Otto chat widget
- `app/static/style.css` — modern, clean retail aesthetic. Not styled to look like Toggle Outfitters.
- `app/static/app.js` — vanilla JS: chat widget submit/receive, dropdown that updates an in-memory user-tier state and includes it on `/chat` requests
- `app/requirements.txt` — pinned versions
- `app/.env.example` — documented env vars
- Product list: 6-8 fictional items, each with name, price, image filename (placeholder images acceptable for now), and short description. See `NARRATIVE.md` for tone.

**Verification steps:**
- App starts via `uvicorn server:app --port 3000` without error
- Hitting `http://localhost:3000` returns the page
- Submitting a chat message returns a canned response
- Toggling the user-tier dropdown updates the value sent in the next `/chat` request (verify via browser devtools)

**Done-when:**
- Operator views the running app and signs off on the look, product list, and chat UX
- All env vars are documented in `.env.example`

---

## Phase 3: AI Configs wiring (locally working chat)

**Goal:** Replace the canned `/chat` response with a real LaunchDarkly AI Configs evaluation that calls Bedrock and returns a real model response. Done with a hardcoded local LD project for development — Instruqt provisioning comes later.

**Deliverables:**
- `app/server.py` updated:
  - Initialize the LaunchDarkly SDK using `LD_SDK_KEY` env var
  - Initialize the AI Configs SDK (`ldai`)
  - On `/chat`, build a context including user tier, evaluate the Otto AI Config, call Bedrock with the resulting model + prompt, return the response
  - Enforce the configurable turn cap; return graceful limit message when exceeded
  - Track `LD_CHAT_TURN_LIMIT` env var (default value documented)
- A development LaunchDarkly project (created manually by the operator or via a dev Terraform module) with Otto's AI Config defined for local testing
- Updated `app/requirements.txt` and `.env.example`
- Logging: each `/chat` call logs which variation was served, token counts, latency

**Verification steps:**
- With valid AWS + LD credentials in `.env`, the app returns real Bedrock responses
- Switching the user-tier dropdown changes which variation is evaluated (verify in logs)
- Turn cap triggers correctly after the configured number of turns
- Bedrock model errors (throttling, access denied) surface as user-friendly error messages, not raw stack traces

**Done-when:**
- Operator runs the app locally end-to-end, has a real conversation with Otto, sees the variation switch by user tier
- Default turn cap value is operator-approved

---

## Phase 4: Challenges 01-03 (create, iterate, snippets)

**Goal:** Author the first three substantive labs: create the first AI Config, iterate on the prompt, refactor into snippets.

**Deliverables (per challenge):**
- `instruqt/0N-<slug>/assignment.md` with full body content following `NARRATIVE.md` voice
- `instruqt/0N-<slug>/setup-workstation`
- `instruqt/0N-<slug>/check-workstation` with `fail-message` guidance for common mistakes
- `instruqt/0N-<slug>/solve-workstation`
- `terraform/challenge-0N/` Terraform module that materializes the end-state of the challenge
- Any required updates to `app/` (e.g. challenge 01 likely has the learner paste SDK-init code into `server.py` — the version pre-baked into the VM image must be the "before" state, and the Terraform/solve script must produce the "after" state)

**Specific notes per challenge:**

- **01 Otto is born:** Learner creates the AI Config in the LD UI, then pastes server-side SDK code into `server.py`. The pre-baked `server.py` should have a clearly-marked block to replace. The check script validates both the LD resource (config exists with a Haiku variation) and the code change (file content match).
- **02 Give Otto a personality:** No code changes. Learner edits the prompt in LD UI; the running app reflects the change. Check script validates the prompt content matches expected updated text (or a regex pattern, to allow some flexibility).
- **03 Otto on-brand at scale:** Learner creates two snippets (`brand_voice`, `safety_rules`) and refactors Otto's prompt to reference them. Check validates snippet creation and that Otto's prompt references them.

**Verification steps Claude Code performs:**
- For each challenge: run setup, then run solve, verify check passes against the solved state
- Web-search the current AI Configs docs to ground UI instructions; mark uncertain UI steps with `<!-- VERIFY: ... -->` comments per `CLAUDE.md`
- List expected screenshots in each challenge folder's `assets/` references

**Operator verification (after Claude Code declares phase done):**
- Operator walks through each lab manually with the draft `assignment.md` open, corrects UI instructions, removes verification markers, captures screenshots
- For each challenge: operator runs setup, completes the lab as a real learner, confirms check passes
- For each challenge: operator runs solve, confirms check still passes
- Operator confirms voice consistency with `NARRATIVE.md`

**Done-when:**
- Operator has completed the click-through verification pass on all three labs
- All verification markers resolved
- All check scripts produce helpful `fail-message` output when given known wrong states (operator tests at least one wrong path per challenge)

---

## Phase 5: Challenge 05 (variations + targeting)

**Goal:** Author the variations and targeting lab. (Challenge 04 is just a quiz — handled in Phase 8.)

**Deliverables:**
- `instruqt/05-otto-for-everyone/` full challenge: `assignment.md`, setup, check, solve
- `terraform/challenge-05/` module that adds the Sonnet "premium" variation to Otto's config and the targeting rule for premium-tier users

**Specific notes:**
- The user-tier dropdown in the app (built in Phase 2) is what the learner uses to test targeting. The lab should explicitly walk them through flipping the dropdown and observing Otto's behavior change.
- The check script validates the variation exists and the targeting rule is configured correctly.

**Verification steps Claude Code performs:**
- Run setup, then solve, verify check passes against the solved state
- Mark uncertain UI steps with `<!-- VERIFY: ... -->` comments

**Operator verification (after Claude Code declares phase done):**
- Operator walks through the lab manually with the draft `assignment.md` open, corrects UI instructions, removes verification markers, captures screenshots
- Operator completes the lab as a real learner; confirms check passes
- Operator runs solve, confirms check still passes
- Operator confirms the user-tier dropdown demo lands clearly

**Done-when:**
- Operator has completed the click-through verification pass
- All verification markers resolved
- Check script passes on completion and fails helpfully on wrong configurations

---

## Phase 6: Challenge 06 (monitoring + traffic generation)

**Goal:** Author the monitoring lab and build the traffic generator that populates monitoring data automatically in the setup script.

**Deliverables:**
- `traffic-generator/generate_traffic.py` — script that sends N chat sessions with random user contexts, random messages from a pool, and weighted thumbs-up/thumbs-down feedback events. Weights should produce visible differences between variations in the monitoring view.
- `instruqt/06-how-is-otto-doing/` full challenge
- `instruqt/06-how-is-otto-doing/setup-workstation` runs the traffic generator automatically and waits for it to complete before declaring setup successful
- `terraform/challenge-06/` — likely minimal; the previous challenge's state plus traffic is the setup

**Specific notes:**
- The traffic generator should complete in ~30 seconds. Tune the number of sessions to produce enough data for the monitoring view to look populated without taking too long.
- The generator must emit real feedback metric events using the LaunchDarkly SDK — these are what the monitoring view displays.
- Document the random message pool in `traffic-generator/messages.txt` or similar — keep messages short to control token usage.
- The assignment.md is more exploratory than directive: the learner navigates to the monitoring view, observes, and answers reflective questions in the assignment text.

**Verification steps Claude Code performs:**
- Run the traffic generator against a fresh project, confirm monitoring data is produced (verifiable via REST API)
- Mark uncertain UI navigation steps to the monitoring view with `<!-- VERIFY: ... -->` comments

**Operator verification (after Claude Code declares phase done):**
- Operator runs the lab with the draft open, corrects UI instructions for the monitoring view, captures screenshots
- Operator confirms monitoring view populates with meaningful, visibly-different data per variation
- Operator confirms the assignment.md walks the learner through the right observations

**Done-when:**
- Operator has completed the click-through verification pass
- All verification markers resolved
- Monitoring view shows clear variation differences with the default traffic generator settings

---

## Phase 7: Challenge 07 (judge + guarded rollout)

**Goal:** Author the guarded-rollout lab. This is the most complex setup work in the track because everything is pre-built.

**Deliverables:**
- `instruqt/07-trust-but-verify/` full challenge
- `terraform/challenge-07/` Terraform module that creates:
  - The Nova Pro variation on Otto's config, with a deliberately poor prompt (specific text in `NARRATIVE.md`)
  - The judge AI Config (separate config with its own prompt evaluating responses for brand-voice adherence)
  - A custom metric tied to the judge's score output
  - The guarded rollout configuration on Otto's main config, watching the metric
- `app/server.py` updates: after each Otto response, call the judge config, evaluate the response, and emit a metric event with the judge's score
- A sabotage script (e.g. `traffic-generator/sabotage.py`) that emits low scores directly to force the rollback for presenter-driven demos
- `instruqt/07-trust-but-verify/setup-workstation` runs the Terraform and starts a low-rate background traffic generator so the rollout has organic data to evaluate against

**Specific notes:**
- The bad Nova Pro prompt should produce responses that are detectably off-brand (wrong tone, off-topic, etc.) — bad enough to trigger the judge, not so bad that it's comical. See `NARRATIVE.md` for the specific prompt.
- The judge's prompt should be carefully written to produce reliable numeric scores. Test with several known-good and known-bad responses before declaring done.
- The sabotage script should be discoverable but not in the learner's main flow — they can use it if they want, presenters use it on demand.
- This challenge's check script likely just validates that the learner reached the guarded-rollout view and saw the rollback event, similar to challenge 06's "explore the monitoring view" pattern.

**Verification steps Claude Code performs:**
- Verify the judge configuration responds to test inputs with stable numeric scores (run several known-good and known-bad responses through it, check consistency)
- Verify the Terraform module applies cleanly and produces the expected resources
- Mark uncertain UI steps for the guarded rollout view with `<!-- VERIFY: ... -->` comments

**Operator verification (after Claude Code declares phase done):**
- Operator runs the full challenge end-to-end multiple times: with organic traffic alone, with the sabotage script, with neither
- Operator confirms the rollback fires when expected and doesn't fire when not expected
- Operator walks through the lab with the draft open, corrects UI instructions for the guarded rollout view, captures screenshots
- Operator confirms judge scoring is stable enough that demos don't roll back unintentionally during normal traffic

**Done-when:**
- Operator has completed the click-through verification pass
- All verification markers resolved
- Operator sees the rollback fire from organic traffic in a reasonable timeframe (or via sabotage on demand)
- The narrative arc lands — the learner finishes with a clear "guarded rollouts protect AI quality" takeaway

---

## Phase 8: Quizzes + welcome + wrap-up

**Goal:** Author the non-lab challenges (00, 04, 08).

**Deliverables:**
- `instruqt/00-welcome/assignment.md` — orient the learner, introduce ToggleWear and Otto. No task. May have a "click Next to continue" instruction.
- `instruqt/04-quiz-configs-and-snippets/assignment.md` — quiz, `type: quiz` in front-matter, 1-3 questions on challenges 01-03
- `instruqt/08-wrap-up/assignment.md` — final summary + 1-3 quiz questions covering the whole track, plus a "thanks for completing" close. May have suggested next steps (e.g. "explore the AI Configs docs" with a link).

**Specific notes:**
- Quiz front-matter format: see reference track's `08-test-your-knowledge` example. `answers` list, `solution` is a list of indices into `answers`.
- Welcome and wrap-up have no `setup`, `check`, or `solve` scripts (or trivial empty ones — check reference track for what's required).
- Voice and narrative wrap-up are owned by `NARRATIVE.md`.

**Done-when:**
- Quiz questions are challenging but answerable from track content alone
- Welcome sets the scene without spoiling the labs
- Wrap-up provides closure to Otto's arc

---

## Phase 9: Polish

**Goal:** Final pass for consistency, voice, and operator experience.

**Deliverables:**
- Pass through every `assignment.md` for narrative consistency against `NARRATIVE.md`
- Pass through every `check-workstation` for `fail-message` quality — every reasonable wrong path should produce specific guidance
- Pass through every `solve-workstation` to confirm it leaves the workstation in the right state
- Pass through every `setup-workstation` to confirm idempotency (running setup twice doesn't break things)
- Add or refine images in `instruqt/assets/` referenced from `assignment.md` files
- Update `vm-image/README.md` with the final list of everything the image must contain
- Final review of `track.yml` description and teaser
- Update `DECISIONS.md` with any decisions made during implementation that weren't captured during planning

**Verification steps:**
- Full track run-through in both 2hr presenter mode (with slides) and 1hr self-paced mode
- Time each challenge to confirm fit within budgets
- Capture screenshots of key moments for the wrap-up and any embedded images

**Done-when:**
- Operator runs both delivery modes end-to-end without intervention
- All polish items checked
- Track is ready for publishing via Instruqt CLI

---

## Phase 1 verification notes

Recorded by Claude Code on 2026-05-15.

- **Current `launchdarkly/launchdarkly` Terraform provider version**: `2.29.0` (released 2026-05-08). Pinned in `terraform/student-bootstrap/versions.tf` as `~> 2.29`.
- **AI Configs resources supported by Terraform provider**: `launchdarkly_ai_config` (modes: `completion`, `agent`, `judge`), `launchdarkly_ai_config_variation` (with inline `messages`, `model`, and `model_config_key`), `launchdarkly_ai_tool`, `launchdarkly_model_config`, `launchdarkly_metric`. AI Configs resources first shipped in provider v2.28.0 (2026-04-20).
  - **Gaps** that will need REST-API fallback via `null_resource` + `local-exec` `curl`: prompt snippets (Phase 4, challenge 03), AI Config targeting rules (Phase 5, challenge 05), guarded rollouts on AI Configs (Phase 7, challenge 07). The MCP tools `update-ai-config-targeting-rules`, `update-ai-config-rollout`, and `update-ai-config-individual-targets` confirm the REST endpoints exist.
- **Current `ldai` (launchdarkly-server-sdk-ai) Python version**: `0.20.1` (released 2026-05-14). Requires Python ≥3.10. Will be pinned in `app/requirements.txt` in Phase 3.
- **Current `launchdarkly-server-sdk` Python version**: `9.15.0` (released 2026-02-10). Requires Python 3.10+. Will be pinned in `app/requirements.txt` in Phase 3.
- **VM Python**: system `python3` from Ubuntu 24.04 noble — currently **3.12**. Both LD SDKs require ≥3.10. (Initial plan called for 3.11 via apt; noble doesn't ship 3.11, and 3.12 satisfies the constraint, so we use the system python.)
- **VM Terraform**: pinned to `1.15.2` (released 2026-05-06) and installed via direct binary download from `releases.hashicorp.com`. HashiCorp's apt repo's noble component is incomplete, so we bypass apt.
- **Chosen AWS region**: `us-east-1` (operator decision). Passed to the VM via the `AWS_REGION` Instruqt secret.
- **Bedrock cross-region inference profile availability (Sonnet, us-east-1)**: US geographic inference profile routes us-east-1 → us-east-1/us-west-2 for Claude Sonnet 4.5+. Global inference profile is supported on Claude Sonnet 4. Specific model and inference-profile IDs (Haiku, Sonnet, Nova Pro) will be locked in Phase 3 when wiring Bedrock — they live on each model's detail page in the Bedrock docs rather than in a single index, and the IDs change as new model versions ship.
- **VM image name**: `instruqt-launchdarkly/ai-configs-intro-1` (placeholder — operator may rename when registering the image).
- **VM `machine_type`**: bumped from reference's `n1-standard-1` to `n1-standard-2` to give headroom for the FastAPI app + traffic generator + Bedrock SDK. Open question flagged in `vm-image/README.md`.

### Open questions for operator (flagged during Phase 1)

1. **Repo HTTPS URL** to set at the top of `vm-image/build-image.sh` before the operator pastes it into the Instruqt console.
2. **`machine_type` confirmation**: is `n1-standard-2` acceptable, or should we stay on `n1-standard-1` to match the reference?
3. **VM image name versioning convention**: confirm `ai-configs-intro-N` with bumped suffix on re-bake.
4. **Source-of-truth at lab start**: keep the reference convention of *no* `git pull` at lab start (assignment/script edits require a re-bake), or add a pull (slower start, but live edits)?
5. **Two environments or one?** The reference uses only `test`. We could pre-create both `test` and `production` to give the challenge-05 targeting demo more dimensions, but it adds complexity. Current implementation: just `test`, matching the reference.
6. **Bedrock model ID specifics** for us-east-1: which Haiku version, which Sonnet inference profile (geo vs global), which Nova Pro ID? Deferred to Phase 3 since they aren't blocking for skeleton.
