"""
llm_engine_freight.py
AI Copilot — Phase 3 of the Milestone 2 architecture.
Loads Qwen2.5-3B-Instruct in 4-bit (bitsandbytes) when a GPU is attached,
and synthesizes Agent 1-3 numeric outputs into an executive summary +
structured JSON audit action. Falls back to a rule-based responder when
no GPU/HF_TOKEN is available (expected behavior per Section 8, not a bug).
"""

import os
import json
import streamlit as st

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
HF_TOKEN = os.environ.get("HF_TOKEN")

_model = None
_tokenizer = None


def _try_load_model():
    """Lazily loads the 4-bit quantized model. Returns True on success."""
    global _model, _tokenizer
    if _model is not None:
        return True
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        if not torch.cuda.is_available():
            return False

        bnb_config = BitsAndBytesConfig(load_in_4bit=True)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, quantization_config=bnb_config, device_map="auto", token=HF_TOKEN
        )
        return True
    except Exception as e:
        print(f"[Copilot] Model load failed, using rule-based fallback: {e}")
        return False


def _rule_based_response(prompt: str) -> str:
    return (
        "Rule-based fallback (no GPU/model loaded): "
        f"Regarding '{prompt.strip()}' — congested ports increase dwell time and "
        "demurrage charges, which raises delivered cost and delay risk. "
        "Enable a GPU runtime and HF_TOKEN secret for a full Qwen2.5-3B response."
    )


def query_copilot(prompt: str, max_new_tokens: int = 200) -> str:
    if _try_load_model():
        import torch
        messages = [{"role": "user", "content": prompt}]
        inputs = _tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(_model.device)
        with torch.no_grad():
            output = _model.generate(inputs, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7)
        text = _tokenizer.decode(output[0][inputs.shape[-1]:], skip_special_tokens=True)
        return text.strip()
    return _rule_based_response(prompt)


def synthesize_audit_action(agent1_output: dict, agent2_output: dict, agent3_output: dict) -> dict:
    """Combines the 3 agents' numeric outputs into a structured JSON audit action (Section 8)."""
    prompt = (
        "Synthesize these freight agent outputs into an executive shipping strategy. "
        f"Pricing: {agent1_output}. Route delay risk: {agent2_output}. "
        f"Carrier compliance: {agent3_output}. "
        "Respond with a 2-3 sentence recommendation."
    )
    narrative = query_copilot(prompt)

    risk_level = "high" if agent2_output.get("delay_probability", 0) > 0.6 else "moderate" if agent2_output.get("delay_probability", 0) > 0.3 else "low"

    return {
        "audit_id": f"AUD-{abs(hash(str(agent1_output) + str(agent2_output))) % 100000}",
        "pricing_estimate": agent1_output,
        "route_risk_level": risk_level,
        "carrier_compliance": agent3_output,
        "executive_summary": narrative,
        "recommended_action": (
            "expedite_and_monitor" if risk_level == "high" else
            "standard_processing" if risk_level == "moderate" else
            "auto_approve"
        ),
    }


def render_copilot_page():
    st.subheader("🤖 AI Copilot")
    st.caption("Ask a logistics question, or synthesize the latest agent outputs into an audit action.")

    prompt = st.text_area(
        "Ask the Copilot",
        placeholder="Explain in 2 sentences why port congestion increases freight risk.",
    )
    if st.button("Ask Copilot"):
        if prompt.strip():
            with st.spinner("Thinking..."):
                response = query_copilot(prompt)
            st.markdown(f"**Copilot:** {response}")
        else:
            st.warning("Enter a prompt first.")

    st.markdown("---")
    st.subheader("Structured Audit Action")
    if st.button("Synthesize Agent 1-3 outputs"):
        # Placeholder sample outputs — wire these to the real agent predictions
        sample_audit = synthesize_audit_action(
            agent1_output={"predicted_cost": 4820.50, "distance_km": 1200, "weight_kg": 3400},
            agent2_output={"delay_probability": 0.42},
            agent3_output={"compliance_score": 0.88, "flagged_issues": []},
        )
        st.json(sample_audit)
