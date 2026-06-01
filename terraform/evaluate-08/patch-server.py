#!/usr/bin/env python3
"""Install Evaluate ch08's adaptive switching into the app.

Two steps:
  1. Copy adaptive.py into /opt/ld/ai-configs-intro/app/ so it's importable
     from server.py.
  2. Patch server.py:
     - Add `from adaptive import observe as adaptive_observe` to the imports.
     - Insert `adaptive_observe(score)` immediately after ch03's
       `ld_client.track("otto-brand-voice-score", ...)` line.

Idempotent: if `adaptive_observe(score)` already appears in server.py, skip.
"""
from __future__ import annotations

import pathlib
import shutil
import sys

REPO_ROOT = pathlib.Path("/opt/ld/ai-configs-intro")
SERVER_PY = REPO_ROOT / "app" / "server.py"
APP_ADAPTIVE = REPO_ROOT / "app" / "adaptive.py"
TF_ADAPTIVE = REPO_ROOT / "terraform" / "evaluate-08" / "adaptive.py"

IMPORT_LINE = "from adaptive import observe as adaptive_observe\n"
IMPORT_ANCHOR = "import boto3\n"

# Anchor inside ch03's brand-voice judge block — the ld_client.track call
# that emits the score. Insert the adaptive_observe call right after it.
ANCHOR = '                ld_client.track("otto-brand-voice-score", bv_ctx, None, score)\n'
INSERT = "                adaptive_observe(score)\n"

SIGNATURE = "adaptive_observe(score)"


def main() -> int:
    # 1. Copy adaptive.py alongside server.py.
    shutil.copy(TF_ADAPTIVE, APP_ADAPTIVE)
    print(f"Wrote {APP_ADAPTIVE}")

    # 2. Patch server.py.
    text = SERVER_PY.read_text()

    if SIGNATURE in text:
        print("server.py already wired to adaptive_observe — patch is a no-op.")
        return 0

    if IMPORT_ANCHOR not in text:
        print(f"ERROR: could not find import anchor `{IMPORT_ANCHOR.strip()}` in server.py", file=sys.stderr)
        return 1
    if ANCHOR not in text:
        print("ERROR: could not find the ch03 brand-voice ld_client.track line in server.py. "
              "Has Challenge 03 been completed?", file=sys.stderr)
        return 1

    # Insert the import after `import boto3` line.
    text = text.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + IMPORT_LINE, 1)

    # Insert the observe call immediately after the brand-voice track line.
    text = text.replace(ANCHOR, ANCHOR + INSERT, 1)

    SERVER_PY.write_text(text)
    print(f"Patched {SERVER_PY} with adaptive_observe wiring")
    return 0


if __name__ == "__main__":
    sys.exit(main())
