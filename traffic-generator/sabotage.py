#!/usr/bin/env python3
"""Force a guarded-rollout rollback by emitting low judge scores.

For presenter-driven demos: when the rollout's organic data is too slow to
trigger an automatic rollback, run this to flood the otto-quality-score
metric with 1s for the Stiff variation's typical users. Within a minute or
two, the guarded rollout's regression detection should fire.

Usage:
    sabotage.py [N]

Where N is the number of bad scores to emit (default 60).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

APP_ENV = Path(__file__).resolve().parent.parent / "app" / ".env"
load_dotenv(dotenv_path=APP_ENV, override=True)

from ldclient import Context, LDClient  # noqa: E402
from ldclient.config import Config as LDConfig  # noqa: E402


def main() -> int:
    sdk_key = os.environ.get("LD_SDK_KEY")
    if not sdk_key:
        print("ERROR: LD_SDK_KEY not set", file=sys.stderr)
        return 1

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60

    ld_client = LDClient(LDConfig(sdk_key))
    if not ld_client.is_initialized():
        print("WARN: LD client did not initialize", file=sys.stderr)

    print(f"Emitting {n} sabotage events (otto-quality-score = 1.0)...")
    for i in range(n):
        ctx = Context.builder(f"sabotage-{uuid4().hex[:8]}").set("tier", "free").build()
        ld_client.track("otto-quality-score", ctx, None, 1.0)
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{n}")

    ld_client.flush()
    ld_client.close()
    print("Done. Watch the rollout for a regression detection event.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
