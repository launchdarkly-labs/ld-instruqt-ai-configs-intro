#!/usr/bin/env python3
"""Populate the AI Configs monitoring view with synthetic chat traffic.

This script does NOT call Bedrock. It evaluates the otto-assistant AI Config
once per simulated session to obtain a real LDAI tracker, then emits the
metric events the monitoring view consumes (tokens, duration, success,
thumbs-up/thumbs-down) using random-but-realistic values weighted per model.

Skipping the real model call keeps the run cheap and lets us land ~120
sessions in roughly 30 seconds, which is enough data for the monitoring
view to show clear differences between the Haiku and Sonnet variations.
"""
from __future__ import annotations

import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

# Load the app's .env so the generator sees the same LD_SDK_KEY as the server.
APP_ENV = Path(__file__).resolve().parent.parent / "app" / ".env"
load_dotenv(dotenv_path=APP_ENV, override=True)

from ldai import AICompletionConfigDefault, LDAIClient  # noqa: E402
from ldai.tracker import FeedbackKind, TokenUsage  # noqa: E402
from ldclient import Context, LDClient  # noqa: E402
from ldclient.config import Config as LDConfig  # noqa: E402

OTTO_CONFIG_KEY = "otto-assistant"
N_SESSIONS = int(os.getenv("TRAFFIC_SESSIONS", "120"))
PREMIUM_RATIO = float(os.getenv("TRAFFIC_PREMIUM_RATIO", "0.30"))
MAX_WORKERS = int(os.getenv("TRAFFIC_MAX_WORKERS", "8"))

# Per-model positive-feedback rate. Sonnet beats Haiku by enough to make the
# monitoring view visibly different between the two variations.
POSITIVE_RATE = {
    "claude-sonnet-4-5": 0.92,
    "claude-haiku-4-5":  0.78,
}
DEFAULT_POSITIVE_RATE = 0.75


def load_messages() -> list[str]:
    path = Path(__file__).resolve().parent / "messages.txt"
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def run_session(ai_client: LDAIClient, messages: list[str], idx: int) -> str:
    session_id = f"sim-{uuid4().hex[:8]}"
    tier = "premium" if random.random() < PREMIUM_RATIO else "free"
    msg = random.choice(messages)

    ctx = Context.builder(session_id).set("tier", tier).build()
    cfg = ai_client.completion_config(
        OTTO_CONFIG_KEY, ctx, AICompletionConfigDefault(enabled=False)
    )

    if not cfg.enabled or cfg.model is None:
        return f"[{idx}] tier={tier} skipped (config disabled)"

    tracker = cfg.create_tracker()

    # Simulate Bedrock-style metrics. Token counts vary with model since Sonnet
    # tends to produce longer outputs.
    is_sonnet = cfg.model.name == "claude-sonnet-4-5"
    latency_ms = random.randint(2200, 5800) if is_sonnet else random.randint(700, 2400)
    in_tokens = random.randint(50, 180) + len(msg) // 4
    out_tokens = random.randint(120, 360) if is_sonnet else random.randint(40, 180)

    tracker.track_duration(latency_ms)
    tracker.track_tokens(
        TokenUsage(total=in_tokens + out_tokens, input=in_tokens, output=out_tokens)
    )
    tracker.track_success()

    pos_rate = POSITIVE_RATE.get(cfg.model.name, DEFAULT_POSITIVE_RATE)
    kind = FeedbackKind.Positive if random.random() < pos_rate else FeedbackKind.Negative
    tracker.track_feedback({"kind": kind})

    return (
        f"[{idx}] tier={tier} model={cfg.model.name} "
        f"latency={latency_ms}ms in={in_tokens} out={out_tokens} "
        f"feedback={kind.value}"
    )


def main() -> int:
    sdk_key = os.environ.get("LD_SDK_KEY")
    if not sdk_key:
        print("ERROR: LD_SDK_KEY not set", file=sys.stderr)
        return 1

    print(f"Initializing LD client...")
    ld_client = LDClient(LDConfig(sdk_key))
    if not ld_client.is_initialized():
        print("WARN: LD client did not initialize in time", file=sys.stderr)
    ai_client = LDAIClient(ld_client)

    messages = load_messages()
    if not messages:
        print("ERROR: messages.txt is empty", file=sys.stderr)
        return 1

    print(
        f"Generating {N_SESSIONS} sessions "
        f"(~{int(PREMIUM_RATIO * 100)}% premium, {MAX_WORKERS} workers)..."
    )
    start = time.time()
    successes = 0
    skipped = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [
            pool.submit(run_session, ai_client, messages, i) for i in range(N_SESSIONS)
        ]
        for fut in as_completed(futures):
            result = fut.result()
            if "skipped" in result:
                skipped += 1
            else:
                successes += 1

    ld_client.flush()
    ld_client.close()
    elapsed = time.time() - start
    print(f"Done. {successes} ok, {skipped} skipped in {elapsed:.1f}s.")
    return 0 if successes else 1


if __name__ == "__main__":
    sys.exit(main())
