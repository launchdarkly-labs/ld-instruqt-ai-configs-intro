#!/usr/bin/env python3
"""Create and start the Evaluate ch06 prompt experiment.

Discovers the variationIds for otto-born and otto-recommender, fetches
the otto-assistant config version, then POSTs to /experiments and starts
the first iteration. Idempotent: if an experiment with the target key
already exists, exit cleanly without touching it.

VERIFY: the experiment's `flags` map references a `ruleId` value. For
fallthrough-targeted experiments the canonical value isn't documented;
this script tries "fallthrough" first and falls back to discovering the
ID from the targeting response. Operator may need to adjust during
click-through.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://app.launchdarkly.com/api/v2"
EXPERIMENT_KEY = "otto-prompt-experiment"
EXPERIMENT_NAME = "Otto Prompt Experiment"
METRIC_KEY = "otto-brand-voice-score"
CONFIG_KEY = "otto-assistant"
ENV_KEY = "test"
CONTROL_VARIATION = "otto-born"
CONTENDER_VARIATION = "otto-recommender"


def request(method: str, path: str, body: dict | None = None, headers_extra: dict | None = None) -> dict:
    token = os.environ["LAUNCHDARKLY_ACCESS_TOKEN"]
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "LD-API-Version": "beta",
    }
    if headers_extra:
        headers.update(headers_extra)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode()
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        text = e.read().decode() if e.fp else ""
        raise SystemExit(f"{method} {path} -> HTTP {e.code}: {text}")


def variation_ids(project_key: str) -> tuple[str, str]:
    """Look up the variation _ids for the two participating variations."""
    targeting = request("GET", f"/projects/{project_key}/ai-configs/{CONFIG_KEY}/targeting")
    by_key = {v["key"]: v["_id"] for v in targeting.get("variations", [])}
    if CONTROL_VARIATION not in by_key:
        raise SystemExit(f"Could not find control variation {CONTROL_VARIATION}")
    if CONTENDER_VARIATION not in by_key:
        raise SystemExit(f"Could not find contender variation {CONTENDER_VARIATION}")
    return by_key[CONTROL_VARIATION], by_key[CONTENDER_VARIATION]


def config_version(project_key: str) -> int:
    """Best-effort fetch of the Config's current version number."""
    cfg = request("GET", f"/projects/{project_key}/ai-configs/{CONFIG_KEY}")
    # Try several plausible keys; the LD API has used different shapes over time.
    for key in ("version", "_version", "configVersion"):
        if key in cfg:
            return int(cfg[key])
    # Fallback: 1. Operator confirms during click-through.
    return 1


def fallthrough_rule_id(project_key: str) -> str:
    """Try to find the rule ID for the fallthrough rule."""
    targeting = request("GET", f"/projects/{project_key}/ai-configs/{CONFIG_KEY}/targeting")
    env = targeting.get("environments", {}).get(ENV_KEY, {})
    fallthrough = env.get("fallthrough", {})
    # Some LD APIs expose the rule id directly here:
    for key in ("ruleId", "_id", "id"):
        if key in fallthrough:
            return str(fallthrough[key])
    # Convention fallback. Operator verifies.
    return "fallthrough"


def experiment_exists(project_key: str) -> bool:
    try:
        request("GET", f"/projects/{project_key}/environments/{ENV_KEY}/experiments/{EXPERIMENT_KEY}")
        return True
    except SystemExit as e:
        if "404" in str(e):
            return False
        raise


def create_experiment(project_key: str, control_id: str, contender_id: str, rule_id: str, version: int) -> None:
    payload = {
        "key": EXPERIMENT_KEY,
        "name": EXPERIMENT_NAME,
        "description": "Otto (Born) vs Otto (Recommender), graded on the brand-voice judge.",
        "iteration": {
            "hypothesis": "Adding a one-sentence prompt to suggest a complementary item improves brand-voice score without going off-brand.",
            "metrics": [{"key": METRIC_KEY}],
            "treatments": [
                {
                    "name": "Control (Born)",
                    "baseline": True,
                    "allocationPercent": 50,
                    "parameters": [{"flagKey": CONFIG_KEY, "variationId": control_id}],
                },
                {
                    "name": "Contender (Recommender)",
                    "baseline": False,
                    "allocationPercent": 50,
                    "parameters": [{"flagKey": CONFIG_KEY, "variationId": contender_id}],
                },
            ],
            "flags": {
                CONFIG_KEY: {
                    "ruleId": rule_id,
                    "flagConfigVersion": version,
                    "notInExperimentVariationId": control_id,
                },
            },
            "primarySingleMetricKey": METRIC_KEY,
            "randomizationUnit": "user",
        },
    }
    request("POST", f"/projects/{project_key}/environments/{ENV_KEY}/experiments", body=payload)
    print(f"Created experiment {EXPERIMENT_KEY}")


def start_iteration(project_key: str) -> None:
    request(
        "POST",
        f"/projects/{project_key}/environments/{ENV_KEY}/experiments/{EXPERIMENT_KEY}/iterations",
    )
    print(f"Started iteration on {EXPERIMENT_KEY}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    args = p.parse_args()

    if experiment_exists(args.project):
        print(f"Experiment {EXPERIMENT_KEY} already exists — no-op.")
        return 0

    control_id, contender_id = variation_ids(args.project)
    version = config_version(args.project)
    rule_id = fallthrough_rule_id(args.project)

    create_experiment(args.project, control_id, contender_id, rule_id, version)
    start_iteration(args.project)
    return 0


if __name__ == "__main__":
    sys.exit(main())
