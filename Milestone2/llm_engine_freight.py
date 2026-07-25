"""
llm_engine_freight.py — LLM Copilot (Phase 3, Section 8).
Loads Qwen2.5-3B-Instruct in 4-bit (bitsandbytes) on the Colab T4 GPU,
answers freeform freight questions, and synthesizes Agent 1-3 outputs
into a structured JSON audit action + a 3-agent "Debate View".
"""

import json
import re

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

_tokenizer = None
_model = None
_llm_ready = False


def load_llm():
    """
    Loads Qwen2.5-3B-Instruct with 4-bit quantization (Section 3.1).
    Call this once at notebook startup, after confirming GPU with !nvidia-smi.
    Falls back gracefully (LLM_ACTIVE = False) if no GPU / bitsandbytes fails,
    per Section 8: "Otherwise you'll see a rule-based fallback — expected behavior."
    """
    global _tokenizer, _model, _llm_ready
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto",
        )
        _llm_ready = True
        print("✅ Qwen2.5-3B (4-bit) loaded on GPU.")
    except Exception as e:
        _llm_ready = False
        print(f"⚠️  LLM load failed, falling back to rule-based Copilot: {e}")

    return _llm_ready


def is_llm_active() -> bool:
    return _llm_ready


def _generate(prompt: str, max_new_tokens: int = 220) -> str:
    """Low-level generation call using the chat template."""
    messages = [
        {"role": "system", "content": "You are FreightQuote AI Copilot, an expert logistics analyst. "
                                       "Answer concisely and reference concrete numbers when given."},
        {"role": "user", "content": prompt},
    ]
    text = _tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = _tokenizer(text, return_tensors="pt").to(_model.device)
    output_ids = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    generated = output_ids[0][inputs["input_ids"].shape[-1]:]
    return _tokenizer.decode(generated, skip_special_tokens=True).strip()


# ------------------------------------------------------------------
# Rule-based fallback (used when GPU/model unavailable)
# ------------------------------------------------------------------
def _rule_based_answer(prompt: str, context: dict) -> str:
    p = prompt.lower()
    delay_risk = context.get("delay_risk_pct", 68)
    congestion = context.get("congestion_level", "high")
    carrier = context.get("carrier", "Maersk")
    punctuality = context.get("punctuality_rate", 94)

    if "delay" in p or "risk" in p:
        return (f"The delay risk for this route is {delay_risk}%, driven by {congestion} congestion "
                f"and potential canal queueing. {carrier} handles this route with a punctuality rate "
                f"of {punctuality}%, indicating generally reliable service despite the elevated risk.")
    if "cost" in p or "costly" in p or "price" in p:
        return (f"Shipping cost is elevated due to {congestion} port congestion, which raises delay "
                f"risk to {delay_risk}% and pushes carriers to price in schedule buffers. "
                f"{carrier}'s {punctuality}% punctuality rate partially offsets this risk.")
    return (f"Based on current agent outputs — delay risk {delay_risk}%, congestion {congestion}, "
            f"carrier {carrier} at {punctuality}% punctuality — plan for moderate schedule buffers.")


def ask_copilot(prompt: str, context: dict = None) -> str:
    """Section 8: main Copilot Q&A entrypoint."""
    context = context or {}
    if _llm_ready:
        grounded_prompt = (
            f"Context from our ML agents: {json.dumps(context)}\n\n"
            f"Question: {prompt}\n\n"
            f"Answer in 2-3 sentences using the context numbers where relevant."
        )
        try:
            return _generate(grounded_prompt)
        except Exception as e:
            print(f"[LLM generation error, falling back] {e}")
            return _rule_based_answer(prompt, context)
    return _rule_based_answer(prompt, context)


# ------------------------------------------------------------------
# Debate View — 3 agents give independent takes, LLM synthesizes
# ------------------------------------------------------------------
def debate_view(agent1_output: dict, agent2_output: dict, agent3_output: dict) -> dict:
    """
    agent1_output example: {"route": "Shanghai-Rotterdam", "cost": 4200, "driver": "high congestion"}
    agent2_output example: {"delay_risk_pct": 68, "congestion": "high", "canal_queue": True}
    agent3_output example: {"carrier": "Maersk", "punctuality_rate": 94, "compliance_risk": "moderate"}
    Returns a dict: {"agent1": str, "agent2": str, "agent3": str, "synthesis": str}
    """
    a1_text = (f"The high cost of shipping from {agent1_output.get('route', 'origin-destination')} "
               f"is due to {agent1_output.get('driver', 'elevated congestion levels')}.")
    a2_text = (f"The journey is experiencing "
               f"{'a canal queue, which increases the delay risk.' if agent2_output.get('canal_queue') else 'moderate congestion.'}")
    a3_text = (f"{agent3_output.get('carrier', 'The carrier')} has a "
               f"{agent3_output.get('punctuality_rate', 90)}% punctuality rate but faces "
               f"{agent3_output.get('compliance_risk', 'some')} compliance risk.")

    synthesis_prompt = (
        f"Agent 1 (pricing): {a1_text}\nAgent 2 (route/weather): {a2_text}\nAgent 3 (carrier audit): {a3_text}\n\n"
        f"Write a 2-3 sentence executive synthesis recommending an action."
    )

    if _llm_ready:
        try:
            synthesis = _generate(synthesis_prompt, max_new_tokens=150)
        except Exception:
            synthesis = _fallback_synthesis(agent1_output, agent2_output, agent3_output)
    else:
        synthesis = _fallback_synthesis(agent1_output, agent2_output, agent3_output)

    return {"agent1": a1_text, "agent2": a2_text, "agent3": a3_text, "synthesis": synthesis}


def _fallback_synthesis(a1, a2, a3):
    return (f"Given the {a2.get('congestion', 'high')} congestion and associated delays, it's "
            f"recommended to consider alternative routes or plan for extended dwell times at ports. "
            f"Additionally, since {a3.get('carrier', 'the carrier')} has a "
            f"{a3.get('punctuality_rate', 90)}% punctuality rate, retaining them remains reasonable "
            f"provided compliance risk is monitored.")


# ------------------------------------------------------------------
# Structured JSON audit action (Phase 3 requirement)
# ------------------------------------------------------------------
def build_json_audit_action(agent1_output: dict, agent2_output: dict, agent3_output: dict) -> dict:
    debate = debate_view(agent1_output, agent2_output, agent3_output)
    risk_level = "HIGH" if agent2_output.get("delay_risk_pct", 0) >= 60 else \
                 "MEDIUM" if agent2_output.get("delay_risk_pct", 0) >= 30 else "LOW"

    audit_action = {
        "route": agent1_output.get("route"),
        "predicted_cost": agent1_output.get("cost"),
        "delay_risk_pct": agent2_output.get("delay_risk_pct"),
        "risk_level": risk_level,
        "carrier": agent3_output.get("carrier"),
        "carrier_punctuality_rate": agent3_output.get("punctuality_rate"),
        "compliance_risk": agent3_output.get("compliance_risk"),
        "recommended_action": (
            "FLAG_FOR_REVIEW" if risk_level == "HIGH" else
            "MONITOR" if risk_level == "MEDIUM" else "APPROVE"
        ),
        "executive_summary": debate["synthesis"],
    }
    return audit_action


def audit_action_to_json_string(audit_action: dict) -> str:
    return json.dumps(audit_action, indent=2)
