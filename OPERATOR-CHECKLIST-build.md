# OPERATOR-CHECKLIST-build.md

Per-challenge verification items for **Track 1 / Build** (`instruqt-build/`). These are tasks that can only be completed by an operator with browser access to a live LaunchDarkly project — Claude Code can draft from docs but cannot drive the UI itself (see the "UI instructions in assignment.md are drafts pending operator verification" entry in `DECISIONS.md`).

Author-side cleanup of stale `<!-- VERIFY -->` markers and recent bug-fix commits ([snippet syntax, federation cleanup, setup-workstation path]) is complete as of 2026-06-01. What remains below is verification work that requires the LD UI.

---

## Cross-cutting items

- [ ] **Live-fire end-to-end smoke test** of the entire Build track against a fresh sandbox: bootstrap → click through every challenge → solve every challenge → confirm every check passes.
- [ ] **VM image re-bake** after the recent hotfixes land on `main`. `vm-image/build-image.sh`'s `REPO_REF` should bump to the new commit. Bump the image's `-N` suffix in `instruqt-build/config.yml` so in-flight labs don't pick up the new image mid-session.
- [ ] **Track-level `setup-workstation` timing**: measure end-to-end startup time. The script bootstraps the project and exits — single Terraform apply. Should be well under 60s.

---

## Per-challenge verification

For each challenge: confirm UI labels in `assignment.md` against the live LD UI; capture screenshots into `instruqt-build/assets/`; add `![alt](../assets/<file>)` image references to the assignment at the appropriate beats; complete the lab as a real learner; click Check (expect pass); run solve from a fresh state and click Check again (expect pass); deliberately fail one assertion (e.g. wrong variation) and confirm `fail-message` output is helpful.

### 00 Welcome

- [ ] No tasks; just confirm copy reads cleanly with no leftover "AI Configs" terminology where "AgentControl" or "Config" is now preferred. (See [[project-track-branding]] — learner-facing prose in `00-welcome` still says "AI Config(s)" pending a separate rename pass.)

### 01 Otto is born

- [ ] Verify UI labels for: **Configs** left-nav item, **Create config** button, **Name**/**Key**/**Mode** fields, **Create** button, the variation creation page, model picker path (**Anthropic → claude-haiku-4-5-20251001**), the system-prompt **System** selector, **Review and save** / **Save changes** buttons, the **Targeting** tab, **Default rule** → **Edit** flow.
- [ ] Screenshot already exists: `assets/ch01-create-config.png`. Capture additional shots if any beat needs visual disambiguation.
- [ ] Test that pasting the Challenge 01 paste block into `server.py` and saving triggers a reload that wires Otto correctly. The marker block must match what the patch-server.py script expects.

### 02 Give Otto a personality

- [ ] Verify UI for editing an existing variation's system prompt: clear text + save flow + naming of any unsaved-changes indicators.
- [ ] Confirm the **Review and save** confirmation step's exact label.
- [ ] Screenshots: capture the variation-edit page and the Review-and-save confirmation.
- [ ] Add `![...]` image references at the appropriate beats in `instruqt-build/02-give-otto-personality/assignment.md`.

### 03 Otto on-brand at scale

- [ ] Verify UI for **Snippets** under AI Configs: where it lives in the left nav; **Create snippet** dialog fields (**Name**, **Key**, **Text**); save flow.
- [ ] Verify the **Load snippet** button location inside the variation prompt editor and confirm the markup it inserts. Recent finding via docs (`https://launchdarkly.com/docs/home/agentcontrol/snippets`) says the canonical reference is `{{snippet.<key>#<version>}}` — confirm the UI inserts this form, with the version (probably `#1` for a fresh-created snippet).
- [ ] Capture screenshots of: snippet creation, snippet listing, the Load-snippet UI inside the prompt editor.

### 04 Quiz: configs and snippets

- [ ] Read through quiz questions and confirm exactly one correct answer per question.
- [ ] Confirm Instruqt's quiz UI renders the answers list correctly (no markdown artifacts).

### 05 Otto for everyone

- [ ] Verify UI for **Add variation** flow.
- [ ] Confirm model picker shows `claude-sonnet-4-6` under Anthropic (currently in the assignment.md). If the displayed model name differs, update assignment.md.
- [ ] Verify UI for adding a targeting rule on the Targeting tab: **+** menu, **Build a custom rule** option, context-kind picker, attribute picker, operator picker, value entry.
- [ ] Confirm Otto on the [ToggleWear](#tab-1) tab actually changes behavior when the **Logged in as** dropdown is switched from Free to Premium (relies on the SDK picking up the targeting rule).
- [ ] Capture screenshots of the rule-builder flow.

### 06 How is Otto doing

- [ ] Verify UI for the **Monitoring** view: navigation to it, the metric dropdown, the variation breakdown.
- [ ] Confirm the traffic generator's output produces visibly differentiated bars/lines between Otto v1 (Born) and Otto v2 (Premium) within ~30s of setup completion. If too fast/slow, tune `traffic-generator/generate_traffic.py`'s session count.
- [ ] The assignment is exploratory; confirm the reflective questions still make sense given the monitoring view's current shape.

### 07 Wrap-up

- [ ] Confirm copy reads cleanly with no leftover "AI Configs" terminology where "AgentControl" or "Config" is now preferred.
- [ ] Read through any final quiz questions; confirm answers list.

---

## Known stale-context items recently resolved (no operator action needed)

These are recorded for context — recent commits already addressed them.

- `{{ldsnippet.<key>}}` → `{{snippet.<key>#<version>}}` in ch03 and ch05 Terraform + assignment.md (commit `446a543`).
- `instruqt-build/track_scripts/setup-workstation` `cd` path corrected to match `vm-image/build-image.sh` (commit `5931319`).
- Dead `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` secrets dropped from `instruqt-build/config.yml` (commit `5931319`).
- Stale "API not publicly documented" comments around the guarded-rollout REST surface cleaned in commit `5629fbc`. `start-guarded-rollout` is now a published MCP tool.
- The `07-trust-but-verify` challenge **lifted to Evaluate** during Phase 6 of `PHASES-evaluate.md` and no longer lives in Build. Build now ends at the monitoring challenge (ch06), with `07-wrap-up` closing the arc and teeing up Evaluate as the next track. The old `terraform/challenge-07/` directory was removed in the same lift.

---

## How to mark progress

Tick items as `[x]` when verified. Capture per-item gotchas inline as plain prose under the bullet (e.g. button label differs from what's in the docs; alternative wording the operator chose). When all per-challenge items are ticked and the cross-cutting smoke test passes, Build is genuinely ship-ready.
