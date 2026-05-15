#!/usr/bin/env python3
"""Inject Challenge 07's judge integration into server.py.

Looks for the marker comment left at the end of Challenge 01's paste block
and inserts the judge code immediately after it. Idempotent: if the file
already contains a judge_config call, this is a no-op.
"""
import pathlib
import sys

REPO_ROOT = pathlib.Path("/opt/ld/ai-configs-intro")
SERVER_PY = REPO_ROOT / "app" / "server.py"
PASTE_FILE = REPO_ROOT / "terraform" / "challenge-07" / "judge-server-paste.py"
MARKER = "    # ─── Challenge 07 judge injects below this marker ──────────────────────"


def main() -> int:
    text = SERVER_PY.read_text()
    paste = PASTE_FILE.read_text()

    if 'ai_client.judge_config("otto-response-judge"' in text:
        print("server.py already has judge integration — no patch needed.")
        return 0

    if MARKER not in text:
        print(
            "ERROR: Challenge 07 marker not found in server.py. "
            "Has Challenge 01's paste been applied?",
            file=sys.stderr,
        )
        return 1

    end_of_marker = text.find(MARKER) + len(MARKER)
    end_of_line = text.find("\n", end_of_marker)
    new_text = text[: end_of_line + 1] + paste + text[end_of_line + 1 :]
    SERVER_PY.write_text(new_text)
    print(f"Patched {SERVER_PY} with judge integration")
    return 0


if __name__ == "__main__":
    sys.exit(main())
