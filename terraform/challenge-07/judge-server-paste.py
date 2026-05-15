    # ─── Challenge 07: judge evaluates Otto's response ─────────────────────
    # Score Otto's response 1-5 with the otto-response-judge AI Config, then
    # emit the score as an otto-quality-score metric event. Errors are
    # swallowed — a judge failure should not poison a user's chat.
    try:
        judge_ctx = Context.builder(req.session_id).set("tier", req.user_tier).build()
        judge_cfg = ai_client.judge_config(
            "otto-response-judge",
            judge_ctx,
            variables={"response": assistant_text},
        )
        if judge_cfg.enabled and judge_cfg.model is not None:
            judge_system: list[dict] = []
            judge_messages: list[dict] = []
            for m in (judge_cfg.messages or []):
                if m.role == "system":
                    judge_system.append({"text": m.content})
                else:
                    judge_messages.append(
                        {"role": m.role, "content": [{"text": m.content}]}
                    )
            judge_kwargs = {
                "modelId": resolve_bedrock_model(judge_cfg.model.name),
                "messages": judge_messages,
                "inferenceConfig": {"maxTokens": 4, "temperature": 0.0},
            }
            if judge_system:
                judge_kwargs["system"] = judge_system
            judge_resp = bedrock.converse(**judge_kwargs)
            judge_text = _extract_text(judge_resp).strip()
            score = next((int(c) for c in judge_text if c in "12345"), None)
            if score is not None:
                ld_client.track("otto-quality-score", judge_ctx, None, float(score))
                log.info(
                    "judge session=%s otto_model=%s score=%d",
                    req.session_id, model_id, score,
                )
    except Exception:  # noqa: BLE001
        log.exception("Judge eval failed (non-fatal)")
