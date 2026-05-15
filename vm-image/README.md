# VM image — `ai-configs-intro`

This directory contains the inputs for the Instruqt VM image referenced by `instruqt/config.yml`. Images are built **manually through the Instruqt web console**, not by an external image pipeline. The `build-image.sh` script in this directory is the artifact you paste into a fresh Ubuntu base to produce the image.

## How to build

1. **Spin up a base VM in the Instruqt console.** Pick an Ubuntu LTS image (22.04 or 24.04 — the script uses whatever `python3` ships with the base, which must be ≥3.10).
2. **Open the terminal on that VM and become root** (`sudo -i`, or run `sudo bash` before pasting the script).
3. **Edit the top of `build-image.sh`** to point `REPO_URL` and `REPO_REF` at the desired commit of this repo. The defaults are placeholders.
4. **Paste the entire script** into the terminal. It echoes progress at each step and `set -e`s on the first failure.
5. **Verify** the script's last line — `Done. Save this VM as your image from the Instruqt console.` — appears and `systemctl is-enabled togglewear code-server` reports both as `enabled`.
6. **Save the running VM as a new image** from the Instruqt console, named to match the `image:` field in `instruqt/config.yml` (currently `instruqt-launchdarkly/ai-configs-intro-1`). Bump the trailing `-N` when re-baking so labs in flight don't get pulled out from under their learners.

The script is idempotent enough to re-run on the same VM (it `rm -rf`s the clone and re-clones), but the intended flow is: fresh base → paste → save.

## What the script installs

| Component | Path | Notes |
|---|---|---|
| System tools | `apt` | `jq`, `git`, `curl`, `wget`, `vim`, `unzip`, `gnupg`, `ca-certificates`, `build-essential`, `lsb-release`, `software-properties-common` |
| System Python 3 + venv | `/usr/bin/python3` | apt (`python3`, `python3-venv`, `python3-dev`). Ubuntu 24.04 noble's system python is 3.12; both `ldai` and `launchdarkly-server-sdk` require ≥3.10, so the system python is fine. |
| Terraform | `/usr/local/bin/terraform` | Direct binary download from `releases.hashicorp.com`. Pinned in `TERRAFORM_VERSION` at the top of `build-image.sh`. HashiCorp's apt repo's noble component is incomplete, so we bypass it. |
| App source | `/opt/ld/ai-configs-intro/` | `git clone --depth 1 --branch ${REPO_REF} ${REPO_URL}`. Subtrees the per-challenge scripts depend on: `app/`, `terraform/student-bootstrap/`, `terraform/challenge-{01..07}/`, `traffic-generator/`, `instruqt/`. |
| Python venv | `/opt/ld/ai-configs-intro/app/.venv/` | `pip install -r app/requirements.txt`. Used by both the FastAPI server and the traffic generators (no second venv). |
| Seeded `.env` | `/opt/ld/ai-configs-intro/app/.env` | Copied from `.env.example`; track-level `setup-workstation` `sed`s real values in at lab start. |
| Bootstrap TF init | `/opt/ld/ai-configs-intro/terraform/student-bootstrap/` | `terraform init` runs at bake time so lab start is fast. |
| `togglewear.service` | `/etc/systemd/system/togglewear.service` | Enabled at boot; runs `uvicorn server:app --host 0.0.0.0 --port 3000`. |
| `code-server.service` | `/etc/systemd/system/code-server.service` | Enabled at boot; serves on port 8080 with `--auth none`. |

## When to re-bake

Re-bake any time:
- `app/requirements.txt` changes (the venv inside the image needs to be rebuilt).
- A systemd unit changes (the unit is written at bake time, not lab start).
- A new tool is needed in `apt`.

**Source-of-truth note:** the current track-level `setup-workstation` does *not* `git pull` at lab start, so any change to scripts or assignment files inside `instruqt/` or `terraform/challenge-NN/` *also* requires a re-bake. This matches the reference track's convention. If you want hot-edit-without-re-bake, add a `git pull` to the top of `setup-workstation` — flagged as an open question in `PHASES.md`.

## What the image does **not** include

- AWS credentials, LD access tokens, LD SDK/client/project keys — those arrive via Instruqt secrets and `setup-workstation` at lab start.
- The student's LD project — created at lab start by `terraform/student-bootstrap/`.
- AI Config resources themselves — those are created by the learner during the labs (or by per-challenge `solve-workstation` Terraform if the learner clicks Skip).

## Things the per-challenge scripts assume are on the image

Reading the per-challenge `setup-workstation` / `solve-workstation` scripts, these paths must exist post-bake:

- `/opt/ld/ai-configs-intro/app/server.py` and `/opt/ld/ai-configs-intro/app/.venv/bin/python` — used by every challenge that restarts the service or invokes the traffic generators.
- `/opt/ld/ai-configs-intro/terraform/challenge-{01,02,03,05,06,07}/*.tf` — each challenge's `setup-workstation` does `terraform init` + `terraform apply` in its own folder.
- `/opt/ld/ai-configs-intro/terraform/challenge-01/{patch-server.py,server-paste.py}` — Challenge 01's solve uses these to patch `server.py` to the AFTER state.
- `/opt/ld/ai-configs-intro/terraform/challenge-07/{patch-server.py,judge-server-paste.py}` — Challenge 07's setup uses these to inject the judge integration.
- `/opt/ld/ai-configs-intro/traffic-generator/{generate_traffic.py,background_traffic.py,sabotage.py,messages.txt}` — Challenge 06 setup runs `generate_traffic.py` once; Challenge 07 setup launches `background_traffic.py` via `nohup` and leaves it running for the duration of the lab.
- `/var/log/togglewear-bg-traffic.log` — Challenge 07's background traffic generator writes here. Path must be writable by the user running setup (root in the Instruqt model).

The git clone covers all of these. If you switch to a different on-VM layout, update both `build-image.sh` and the hard-coded paths in the per-challenge scripts.
