# Iterating safely (without touching the live track)

This doc is the repeatable workflow for changing the track or app, testing the
change in a real Instruqt sandbox, and **never overwriting the published track
or anyone else's work.**

## The one thing that can hurt the live track

The published, customer-facing track is:

| Field | Value |
|---|---|
| slug | `ld-agentcontrol-intro` |
| id | `xl0egbmxaqtv` |
| owner | `launchdarkly` |
| developers | `kcochran@launchdarkly.com`, `sattensil@launchdarkly.com` |
| VM image | `launchdarkly/workshop-ai-configs` |

`instruqt track push` updates the track identified by the **`owner` + `slug`**
in the `track.yml` of the directory you run it from. **This repo's
`instruqt/track.yml` carries the live slug/id.** So:

> ⛔ **Never run `instruqt track push` from inside this repo's `instruqt/`
> folder.** That overwrites the live track. All testing happens in a *separate
> copy* with a *different slug* (below).

Likewise: **never re-save the `launchdarkly/workshop-ai-configs` image** — bake
test changes under a new image name and repoint a copy track at it.

## One-time setup

```sh
brew install instruqt/tap/instruqt   # macOS; see https://docs.instruqt.com/getting-started/set-up-instruqt for other OS
instruqt version
instruqt auth login                  # browser login; token lasts 1 hour, re-run when it expires
```

## The loop

### 1. Make your change on a branch
```sh
git checkout -b fix/my-change
# edit app/, instruqt/, terraform/, vm-image/build-image.sh, etc.
git push -u origin fix/my-change
```

### 2. Bake a NEW image (only if you changed anything baked into the VM)
Baked-in = `app/`, `requirements.txt`, the systemd units in
`vm-image/build-image.sh`, `terraform/**`, `instruqt/**` scripts — because
track-level `setup-workstation` does **not** `git pull` at lab start.
(Pure `assignment.md` prose changes still need a rebake for the same reason.)

In the Instruqt console: **Settings → Host images → Create image**.
- **Name:** a *new, distinct* name — bump the suffix, e.g. `workshop-ai-configs-3`.
  Never reuse `workshop-ai-configs` (the live image).
- **Base image:** an Ubuntu LTS **preset** (22.04 or 24.04).
- On the **Customize** step, in the Terminal, paste (swap in your branch + the
  raw URL's commit SHA — find the SHA with `git rev-parse --short HEAD`):
  ```sh
  curl -fsSL https://raw.githubusercontent.com/launchdarkly-labs/ld-instruqt-ai-configs-intro/<COMMIT_SHA>/vm-image/build-image.sh \
    | sed 's|^REPO_REF=.*|REPO_REF="fix/my-change"|' \
    | bash
  ```
- Wait for `==> Done. Save this VM...`. Verify, then **Save**:
  ```sh
  systemctl is-enabled togglewear code-server   # both: enabled
  grep ExecStart /etc/systemd/system/togglewear.service
  ```

If your change is *track-only* and needs no rebake, you can point the copy
track at the existing image instead.

### 3. Create a throwaway COPY of the live track (safe — new slug + id)
Run this **outside this repo** so nothing lands on the live track:
```sh
mkdir -p ~/instruqt-test && cd ~/instruqt-test
instruqt track create --from launchdarkly/ld-agentcontrol-intro --title "AI Configs Intro - <what youre testing>"
```
This makes a server-side copy with an auto-generated slug (e.g.
`ai-configs-intro-reload-test`). It does **not** modify the original. The new
track lands in `~/instruqt-test/<new-slug>/`.

### 4. Point the copy at your new image
Edit `~/instruqt-test/<new-slug>/config.yml`:
```yaml
  image: launchdarkly/workshop-ai-configs-3   # your new image from step 2
```

### 5. Confirm you're about to push the COPY, then push
```sh
cd ~/instruqt-test/<new-slug>
grep -E '^(slug|owner):' track.yml   # slug must NOT be ld-agentcontrol-intro
instruqt track push
```

### 6. Set secrets on the copy + start it
The copy declares the secret *names* but does **not** inherit the live track's
secret *values*. In the console, open the new track → **Secrets**, and set:
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`,
`LAUNCHDARKLY_ACCESS_TOKEN` (copy from the live track's secrets if you have
access). Then **Start** the track (or `instruqt track open`) and test.

> ⚠️ Secrets are one shared set, used by every run: a shared AWS IAM user
> (shared Bedrock cost + rate limits) and a shared LaunchDarkly token. Per-run
> isolation only applies to the LD *project* (`ai-configs-intro-<sandbox_id>`),
> not the account or AWS.

### 7. Clean up when done
```sh
instruqt track delete launchdarkly/<new-slug>   # remove the throwaway track
```
And delete the throwaway image in Settings → Host images if you won't reuse it.

## Promoting a verified change to production (deliberate, separate step)

Testing never touches production. To actually ship a fix to learners:
1. Merge your branch to `main` (PR + review).
2. Rebake the change into a new image and update the **live** `config.yml`'s
   `image:` to that new name (still a fresh suffix — don't clobber the old one
   until you've cut over).
3. From this repo's `instruqt/` dir (the one with the live slug/id),
   `instruqt track push` to update `ld-agentcontrol-intro` — coordinate with
   `kcochran@` first, since this is the customer-facing track.
