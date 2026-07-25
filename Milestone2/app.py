"""
app.py — FreightQuote AI main Streamlit entrypoint (Milestone 2).
Run from the Colab launch cell, e.g.:
    !streamlit run app.py --server.port 8501 &
    (then open the ngrok public URL)
"""

import streamlit as st
import joblib
import os

import db
import auth
import ui_theme
import admin_dash
import llm_engine_freight as llm

st.set_page_config(page_title="FreightQuote AI", page_icon="⚡", layout="wide")
ui_theme.inject_css()
db.init_db()

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# ------------------------------------------------------------------
# Session state defaults
# ------------------------------------------------------------------
for key, default in [
    ("logged_in", False),
    ("username", None),
    ("role", None),
    ("token", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ------------------------------------------------------------------
# AUTH SCREENS (Phase 1) — Login / Register / Forgot Password
# ------------------------------------------------------------------
def render_auth_screens():
    ui_theme.render_brand_header()

    tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Forgot Password"])

    # ---------------- Login ----------------
    with tab1:
        ui_theme.card_start("User Login")
        st.markdown('<div class="fq-inner-box">', unsafe_allow_html=True)
        login_id = st.text_input("Username / Email *", key="login_id")
        col_pw, col_eye = st.columns([5, 1])
        show_pw = st.session_state.get("show_login_pw", False)
        password = st.text_input(
            "Password *", type="default" if show_pw else "password", key="login_pw"
        )
        st.checkbox("👁 Show password", key="show_login_pw")
        remember = st.checkbox("Remember Me", key="login_remember")

        if st.button("Login", key="login_btn"):
            ok, msg, token = auth.login_user(login_id, password)
            if ok:
                conn = db.get_conn()
                user = conn.execute(
                    "SELECT * FROM users WHERE email = ? OR username = ?", (login_id, login_id)
                ).fetchone()
                conn.close()
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.session_state.token = token
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)
        ui_theme.card_end()

    # ---------------- Signup ----------------
    with tab2:
        ui_theme.card_start("Create Account")
        st.markdown('<div class="fq-inner-box">', unsafe_allow_html=True)
        u = st.text_input("Username *", key="reg_username")
        e = st.text_input("Email *", key="reg_email")
        show_reg_pw = st.session_state.get("show_reg_pw", False)
        p = st.text_input("Password *", type="default" if show_reg_pw else "password", key="reg_pw")
        confirm_p = st.text_input(
            "Confirm Password *", type="default" if show_reg_pw else "password", key="reg_confirm_pw"
        )
        st.checkbox("👁 Show password", key="show_reg_pw")
        if p:
            allowed, badge, msg = auth.check_password_strength(p)
            st.markdown(f"Strength: {badge} — {msg}")

        sec_question = st.selectbox("Security Question *", auth.SECURITY_QUESTIONS, key="reg_sec_q")
        sec_answer = st.text_input("Security Answer *", key="reg_sec_a")

        if st.button("Sign Up", key="signup_btn"):
            if p != confirm_p:
                st.error("Passwords do not match.")
            elif not sec_answer:
                st.error("Security answer is required.")
            else:
                ok, msg = auth.register_user(
                    u, e, p, security_question=sec_question, security_answer=sec_answer
                )
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)
        ui_theme.card_end()

    # ---------------- Forgot Password ----------------
    with tab3:
        ui_theme.card_start("Forgot Password")
        st.markdown("Choose a recovery method:")
        method = st.radio(
            "recovery_method", ["Security Question", "Email OTP"],
            key="fp_method", label_visibility="collapsed", horizontal=True,
        )
        st.markdown('<div class="fq-inner-box">', unsafe_allow_html=True)

        if method == "Security Question":
            fp_username = st.text_input("Username *", key="fp_username")
            if st.button("Get Security Question", key="fp_get_q"):
                question, err = auth.get_security_question(fp_username)
                if err:
                    st.error(err)
                else:
                    st.session_state["fp_question"] = question
                    st.session_state["fp_question_user"] = fp_username

            if st.session_state.get("fp_question"):
                st.markdown(f"**{st.session_state['fp_question']}**")
                answer = st.text_input("Your Answer *", key="fp_answer")
                new_pw = st.text_input("New Password *", type="password", key="fp_new_pw_sq")
                if new_pw:
                    allowed, badge, msg = auth.check_password_strength(new_pw)
                    st.markdown(f"Strength: {badge} — {msg}")
                if st.button("Reset Password", key="fp_reset_sq"):
                    ok, msg = auth.verify_security_answer(st.session_state["fp_question_user"], answer)
                    if not ok:
                        st.error(msg)
                    else:
                        ok2, msg2 = auth.reset_password_by_username(
                            st.session_state["fp_question_user"], new_pw
                        )
                        st.success(msg2) if ok2 else st.error(msg2)

        else:  # Email OTP
            fp_email = st.text_input("Registered email *", key="fp_email")
            if st.button("Send OTP", key="fp_send_otp"):
                ok, msg = auth.request_otp(fp_email, purpose="reset")
                st.info(msg) if ok else st.warning(msg)

            otp_code = st.text_input("Enter OTP *", key="fp_otp")
            new_pw = st.text_input("New Password *", type="password", key="fp_new_pw_otp")
            if new_pw:
                allowed, badge, msg = auth.check_password_strength(new_pw)
                st.markdown(f"Strength: {badge} — {msg}")
            if st.button("Reset Password", key="fp_reset_otp"):
                ok_otp, msg_otp = auth.verify_otp(fp_email, otp_code, purpose="reset")
                if not ok_otp:
                    st.error(msg_otp)
                else:
                    ok_reset, msg_reset = auth.reset_password(fp_email, new_pw)
                    st.success(msg_reset) if ok_reset else st.error(msg_reset)

        st.markdown("</div>", unsafe_allow_html=True)
        ui_theme.card_end()

    ui_theme.render_footer()


# ------------------------------------------------------------------
# Agent pages
# ------------------------------------------------------------------
def render_agent1_pricing():
    st.subheader("💰 Agent 1: Dynamic Pricing")
    path = os.path.join(MODELS_DIR, "agent1_pricing_champion.joblib")
    if not os.path.exists(path):
        st.warning("Model not trained yet. Run train_ml_freight.train_agent1_pricing() in the notebook.")
        return
    bundle = joblib.load(path)
    model, scaler, features = bundle["model"], bundle["scaler"], bundle["features"]

    distance_km = st.number_input("Distance (km)", 50.0, 15000.0, 5000.0)
    weight_kg = st.number_input("Weight (kg)", 10.0, 25000.0, 1000.0)
    congestion_level = st.slider("Congestion level (0-1)", 0.0, 1.0, 0.5)
    fuel_index = st.slider("Fuel index", 0.8, 1.6, 1.1)

    if st.button("Predict Freight Cost"):
        import pandas as pd
        X = pd.DataFrame([[distance_km, weight_kg, congestion_level, fuel_index]], columns=features)
        try:
            X_in = scaler.transform(X)
            pred = model.predict(X_in)[0]
        except Exception:
            pred = model.predict(X)[0]
        st.success(f"💵 Predicted Freight Cost: **${pred:,.2f}**")
        st.session_state["agent1_output"] = {
            "route": "Custom Route", "cost": round(float(pred), 2),
            "driver": "high congestion" if congestion_level > 0.6 else "normal conditions",
        }


def render_agent2_route():
    st.subheader("🧭 Agent 2: Route Delay / Weather")
    path = os.path.join(MODELS_DIR, "agent2_route_delay_champion.joblib")
    if not os.path.exists(path):
        st.warning("Model not trained yet. Run train_ml_freight.train_agent2_route_delay() in the notebook.")
        return
    bundle = joblib.load(path)
    model, scaler, features = bundle["model"], bundle["scaler"], bundle["features"]

    congestion = st.slider("Congestion", 0.0, 1.0, 0.6)
    weather_risk = st.slider("Weather risk", 0.0, 1.0, 0.4)
    canal_queue = st.checkbox("Canal queue present?")
    distance_km = st.number_input("Distance (km)", 50.0, 15000.0, 6000.0)

    if st.button("Assess Delay Risk"):
        import pandas as pd
        X = pd.DataFrame([[congestion, weather_risk, int(canal_queue), distance_km]], columns=features)
        try:
            proba = model.predict_proba(scaler.transform(X))[0][1]
        except Exception:
            proba = model.predict_proba(X)[0][1]
        risk_pct = round(proba * 100, 1)
        st.success(f"⚠️ Delay Risk: **{risk_pct}%**")
        st.session_state["agent2_output"] = {
            "delay_risk_pct": risk_pct,
            "congestion": "high" if congestion > 0.6 else "moderate",
            "canal_queue": canal_queue,
        }


def render_agent3_carrier():
    st.subheader("✅ Agent 3: Carrier Audit")
    path = os.path.join(MODELS_DIR, "agent3_carrier_audit_champion.joblib")
    if not os.path.exists(path):
        st.warning("Model not trained yet. Run train_ml_freight.train_agent3_carrier_audit() in the notebook.")
        return
    bundle = joblib.load(path)
    model, scaler, features = bundle["model"], bundle["scaler"], bundle["features"]

    carrier_name = st.text_input("Carrier name", "Maersk")
    punctuality_rate = st.slider("Punctuality rate", 0.5, 1.0, 0.94)
    docs_compliance = st.slider("Docs compliance", 0.0, 1.0, 0.8)
    safety_incidents = st.number_input("Safety incidents (last year)", 0, 10, 1)
    years_active = st.number_input("Years active", 1.0, 25.0, 10.0)

    if st.button("Run Compliance Audit"):
        import pandas as pd
        X = pd.DataFrame([[punctuality_rate, docs_compliance, safety_incidents, years_active]], columns=features)
        try:
            proba = model.predict_proba(scaler.transform(X))[0][1]
        except Exception:
            proba = model.predict_proba(X)[0][1]
        risk = "moderate" if proba > 0.3 else "low"
        st.success(f"🛡️ Compliance risk: **{risk}** (non-compliance probability {proba:.2f})")
        st.session_state["agent3_output"] = {
            "carrier": carrier_name,
            "punctuality_rate": round(punctuality_rate * 100, 1),
            "compliance_risk": risk,
        }


def render_ai_copilot():
    st.subheader(f"💬 AI Copilot — Powered by Qwen-2.5-3B")
    if llm.is_llm_active():
        st.success("⚡ LLM Active on GPU")
    else:
        st.info("ℹ️ Rule-based fallback active (no GPU / model not loaded)")

    context = {
        **st.session_state.get("agent1_output", {}),
        **st.session_state.get("agent2_output", {}),
        **st.session_state.get("agent3_output", {}),
    }

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for turn in st.session_state.chat_history:
        st.markdown(f"🙋 **You:** {turn['q']}")
        st.markdown(f"⚡ **Copilot:** {turn['a']}")

    prompt = st.text_input("Ask the Copilot", placeholder="e.g. Why is port congestion increasing freight risk?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ask") and prompt:
            answer = llm.ask_copilot(prompt, context)
            st.session_state.chat_history.append({"q": prompt, "a": answer})
            db.log_copilot_query(st.session_state.username, prompt, answer)
            st.rerun()

    with col2:
        if st.button("Debate View"):
            debate = llm.debate_view(
                st.session_state.get("agent1_output", {}),
                st.session_state.get("agent2_output", {}),
                st.session_state.get("agent3_output", {}),
            )
            st.json(debate)

            audit = llm.build_json_audit_action(
                st.session_state.get("agent1_output", {}),
                st.session_state.get("agent2_output", {}),
                st.session_state.get("agent3_output", {}),
            )
            st.markdown("**Structured JSON Audit Action:**")
            st.code(llm.audit_action_to_json_string(audit), language="json")


# ------------------------------------------------------------------
# Main router
# ------------------------------------------------------------------
def main():
    if not st.session_state.logged_in:
        render_auth_screens()
        return

    is_admin = st.session_state.role.lower() == "admin"

    st.sidebar.markdown("### ⚡ FreightQuote AI")
    st.sidebar.markdown(f"User: **{st.session_state.username}**  \n[{st.session_state.role}]")
    pages = ["💬 AI Copilot", "$ Agent 1: Pricing", "🧭 Agent 2: Route/Weather", "✅ Agent 3: Carrier Audit"]
    if is_admin:
        pages.append("🛡️ Admin Dashboard")
    pages.append("🚪 Sign Out")

    choice = st.sidebar.radio("Navigate", pages, label_visibility="collapsed")

    if choice == "💬 AI Copilot":
        render_ai_copilot()
    elif choice == "$ Agent 1: Pricing":
        render_agent1_pricing()
    elif choice == "🧭 Agent 2: Route/Weather":
        render_agent2_route()
    elif choice == "✅ Agent 3: Carrier Audit":
        render_agent3_carrier()
    elif choice == "🛡️ Admin Dashboard" and is_admin:
        admin_dash.render_admin_dashboard(st.session_state.username)
    elif choice == "🚪 Sign Out":
        for key in ["logged_in", "username", "role", "token", "chat_history"]:
            st.session_state[key] = False if key == "logged_in" else None
        st.rerun()


if __name__ == "__main__":
    main()
