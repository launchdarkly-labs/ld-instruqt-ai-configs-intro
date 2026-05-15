"""ToggleWear server.

Phase 2: serves the static frontend and answers /chat with canned responses.
Phase 3 replaces the canned block with an AI Configs + Bedrock evaluation.
"""
import os
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

STATIC_DIR = Path(__file__).parent / "static"
TURN_LIMIT = int(os.getenv("LD_CHAT_TURN_LIMIT", "30"))

app = FastAPI(title="ToggleWear")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Per-session turn counter. In-memory and per-process — fine for a single-VM
# Instruqt workstation; if we ever scale beyond one process this needs a real
# store.
_turns: dict[str, int] = defaultdict(int)


class ChatRequest(BaseModel):
    message: str
    user_tier: str = "free"
    session_id: str


class ChatResponse(BaseModel):
    response: str
    turn: int
    turn_limit: int


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
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

    # --- PHASE 3 REPLACES THIS BLOCK ---------------------------------------
    # In Phase 3, the canned dispatch below is replaced by:
    #   1. Build an LDContext including user_tier.
    #   2. Evaluate the "otto-assistant" AI Config.
    #   3. Call Bedrock with the evaluated model + messages.
    #   4. Track tokens / latency / variation.
    response_text = _canned_response(req.message, req.user_tier)
    # -----------------------------------------------------------------------

    return ChatResponse(response=response_text, turn=turn, turn_limit=TURN_LIMIT)


def _canned_response(message: str, user_tier: str) -> str:
    """Bland, robotic Otto. The pre-personality 'born' state from NARRATIVE.md.

    Once Phase 3 wires Bedrock, this function goes away.
    """
    m = message.lower().strip()

    if any(g in m for g in ("hi", "hello", "hey", "greetings")):
        return "Hello. I am the ToggleWear shopping assistant. How may I help you."

    if any(s in m for s in ("size", "fit", "sizing", "small", "medium", "large")):
        return "Please consult the product page for sizing information."

    if any(p in m for p in ("price", "cost", "how much")):
        return "Please refer to the product grid for current pricing."

    if any(s in m for s in ("ship", "delivery", "return", "refund", "policy")):
        return "Please consult the ToggleWear policies page for shipping and return information."

    if any(p in m for p in ("recommend", "suggest", "best", "favorite")):
        return "ToggleWear offers a selection of LaunchDarkly-branded apparel. Please see the product grid."

    tier_note = " (Premium support enabled.)" if user_tier == "premium" else ""
    return f"I am unable to assist with that request. Please try a different question.{tier_note}"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
