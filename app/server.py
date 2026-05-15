"""ToggleWear server.

Evaluates the otto-assistant AI Config for each chat turn and calls Bedrock
with the resulting model + prompt. Maintains per-session conversation history.
"""
import logging
import os
import threading
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from ldai import AICompletionConfigDefault, LDAIClient, LDMessage
from ldclient import Context, LDClient
from ldclient.config import Config as LDConfig
from pydantic import BaseModel

# override=True so .env wins over any stale AWS_* or LD_* values left in the
# shell from a previous session. load_dotenv only overrides keys it sets, so
# values absent from .env (e.g. AWS_SESSION_TOKEN when using long-lived IAM
# keys) still leak from the shell — clear them explicitly below.
_dotenv_keys = set(dotenv_values().keys())
load_dotenv(override=True)
if "AWS_SESSION_TOKEN" not in _dotenv_keys:
    os.environ.pop("AWS_SESSION_TOKEN", None)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("togglewear")

STATIC_DIR = Path(__file__).parent / "static"
OTTO_CONFIG_KEY = "otto-assistant"
TURN_LIMIT = int(os.getenv("LD_CHAT_TURN_LIMIT", "30"))
HISTORY_LIMIT = 20  # last N user/assistant messages per session
LD_SDK_KEY = os.environ["LD_SDK_KEY"]
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

ld_client = LDClient(LDConfig(LD_SDK_KEY))
ai_client = LDAIClient(ld_client)
# Explicit credentials — avoids the boto3 credential chain falling back to
# stale shared-credentials files, instance profiles, or SSO refresh attempts.
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
)

FALLBACK_CONFIG = AICompletionConfigDefault(enabled=False)

# LaunchDarkly's model config registry returns a vendor-neutral name (e.g.
# "claude-sonnet-4-5"); Bedrock needs the full model or inference-profile ID.
# When the workshop adds a new model, add a row here.
BEDROCK_MODEL_IDS = {
    "claude-sonnet-4-5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "claude-haiku-4-5":  "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "claude-haiku-3-5":  "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    "nova-pro":          "us.amazon.nova-pro-v1:0",
}


def resolve_bedrock_model(ld_model_name: str) -> str:
    """Map LD's vendor-neutral model name to a Bedrock model ID. Pass-through if unknown."""
    return BEDROCK_MODEL_IDS.get(ld_model_name, ld_model_name)

_turns: dict[str, int] = defaultdict(int)
_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))
_state_lock = threading.Lock()

app = FastAPI(title="ToggleWear")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str
    user_tier: str = "free"
    session_id: str


class ChatResponse(BaseModel):
    response: str
    turn: int
    turn_limit: int
    model: Optional[str] = None


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz():
    return {"ok": True, "otto_config": OTTO_CONFIG_KEY, "region": AWS_REGION}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    with _state_lock:
        _turns[req.session_id] += 1
        turn = _turns[req.session_id]

    if turn > TURN_LIMIT:
        return JSONResponse(
            status_code=429,
            content={
                "response": (
                    "You have reached the demo chat limit for this session. "
                    "Refresh the page to start a new session."
                ),
                "turn": turn,
                "turn_limit": TURN_LIMIT,
            },
        )

    context = Context.builder(req.session_id).set("tier", req.user_tier).build()
    cfg = ai_client.completion_config(OTTO_CONFIG_KEY, context, FALLBACK_CONFIG)

    if not cfg.enabled or cfg.model is None:
        log.warning(
            "AI Config %s returned disabled/no-model for tier=%s — is targeting on and a real variation served?",
            OTTO_CONFIG_KEY,
            req.user_tier,
        )
        return JSONResponse(
            status_code=503,
            content={
                "response": (
                    "Otto is currently unavailable. Verify the AI Config is enabled and "
                    "a non-disabled variation is being served in this environment."
                ),
                "turn": turn,
                "turn_limit": TURN_LIMIT,
            },
        )

    model_id = resolve_bedrock_model(cfg.model.name)

    system_blocks: list[dict] = []
    seed_messages: list[dict] = []
    for m in cfg.messages or []:
        if m.role == "system":
            system_blocks.append({"text": m.content})
        else:
            seed_messages.append({"role": m.role, "content": [{"text": m.content}]})

    with _state_lock:
        prior = list(_history[req.session_id])
    history_blocks = [{"role": m.role, "content": [{"text": m.content}]} for m in prior]
    new_user_block = {"role": "user", "content": [{"text": req.message}]}
    bedrock_messages = seed_messages + history_blocks + [new_user_block]

    inference_config: dict = {}
    temperature = cfg.model.get_parameter("temperature")
    max_tokens = cfg.model.get_parameter("maxTokens")
    if temperature is not None:
        inference_config["temperature"] = float(temperature)
    if max_tokens is not None:
        inference_config["maxTokens"] = int(max_tokens)

    tracker = cfg.create_tracker()

    converse_kwargs = {"modelId": model_id, "messages": bedrock_messages}
    if system_blocks:
        converse_kwargs["system"] = system_blocks
    if inference_config:
        converse_kwargs["inferenceConfig"] = inference_config

    try:
        response = tracker.track_bedrock_converse_metrics(bedrock.converse(**converse_kwargs))
    except ClientError as e:
        err = e.response.get("Error", {})
        code = err.get("Code")
        log.error("Bedrock ClientError code=%s message=%s", code, err.get("Message"))
        return JSONResponse(
            status_code=502,
            content={
                "response": _bedrock_user_message(code),
                "turn": turn,
                "turn_limit": TURN_LIMIT,
            },
        )
    except (BotoCoreError, RuntimeError) as e:
        # boto3 raises plain RuntimeError on credential refresh failures (e.g.
        # expired SSO/STS creds). Catch broadly so the user gets a clean JSON
        # response instead of a 500 with an empty body.
        log.exception("Bedrock SDK error")
        message = str(e) or "Bedrock SDK error"
        if "credentials" in message.lower() or "expired" in message.lower():
            user_msg = "Otto's AWS credentials look expired. Refresh them in .env and try again."
        else:
            user_msg = "Otto can't reach Bedrock right now. Please try again in a moment."
        return JSONResponse(
            status_code=502,
            content={"response": user_msg, "turn": turn, "turn_limit": TURN_LIMIT},
        )

    assistant_text = _extract_text(response)

    with _state_lock:
        _history[req.session_id].append(LDMessage(role="user", content=req.message))
        _history[req.session_id].append(LDMessage(role="assistant", content=assistant_text))

    usage = response.get("usage") or {}
    metrics = response.get("metrics") or {}
    log.info(
        "chat session=%s tier=%s turn=%d model=%s tokens_in=%s tokens_out=%s latency_ms=%s",
        req.session_id,
        req.user_tier,
        turn,
        model_id,
        usage.get("inputTokens"),
        usage.get("outputTokens"),
        metrics.get("latencyMs"),
    )

    return ChatResponse(
        response=assistant_text,
        turn=turn,
        turn_limit=TURN_LIMIT,
        model=model_id,
    )


def _bedrock_user_message(code: Optional[str]) -> str:
    if code in ("ThrottlingException", "ServiceQuotaExceededException"):
        return "Otto is a little overwhelmed right now. Please try again in a few seconds."
    if code == "AccessDeniedException":
        return "Otto can't reach his model — please check AWS credentials and Bedrock model access."
    if code == "ValidationException":
        return "Otto's AI Config has an invalid setting. Please verify the model ID and variation."
    return "Otto hit an unexpected error. Please try again."


def _extract_text(response: dict) -> str:
    try:
        return response["output"]["message"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return "Otto received a response in an unexpected format."


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
