"""
app.py
Entry point for FreightQuote AI — Milestone 2.
Recreates the Milestone 1 Login / Signup / Forgot-Password screens exactly
(same nav pills, title, card layout) and, once authenticated, unlocks:
  Home -> Agent 1/2/3 -> AI Copilot -> Admin Dashboard (role='Admin' only)
"""

import streamlit as st

import db
import auth
import ui_theme
from ui_theme import apply_theme, render_header, render_nav, card_start, card_end, pw_strength_badge

st.set_page_config(page_title="Infosys FreightQuote", layout="centered")
db.init_db()
apply_theme()

SECURITY_QUESTIONS = [
    "What is your favourite pet's name?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
]

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Login"
if "otp_stage" not in st.session_state:
    st.session_state.otp_stage = None  # holds pending OTP + user id during forgot-password flow


# ---------------------------------------------------------------------------
# Gate: if logged in, hand off to the main app (Home / Agents / Copilot / Admin)
# ---------------------------------------------------------------------------

def render_authenticated_shell(claims):
    render_header()
    st.sidebar.success(f"Logged in as {claims['username']} ({claims['role']})")
    if st.sidebar.button("Logout"):
        st.session_state.auth_token = None
        st.rerun()

    pages = ["Home", "Agent 1: Pricing", "Agent 2: Route Delay", "Agent 3: Carrier Compliance", "AI Copilot"]
    if claims["role"].lower() == "admin":
        pages.append("Admin Dashboard")

    page = st.sidebar.radio("Navigate", pages)

    if page == "Home":
        card_start("Home — KPI Overview")
        st.write("Welcome to FreightQuote AI. Select an agent from the sidebar to get started.")
        card_end()
    elif page == "Admin Dashboard":
        import admin_dash
        admin_dash.render()
    elif page == "AI Copilot":
        import llm_engine_freight
        llm_engine_freight.render_copilot_page()
    else:
        st.info(f"{page} module lives in train_ml_freight.py — wire up the trained model UI here.")


token = st.session_state.auth_token
claims = auth.verify_token(token) if token else None

if claims:
    render_authenticated_shell(claims)
    st.stop()


# ---------------------------------------------------------------------------
# Unauthenticated: Login / Signup / Forgot Password nav (matches screenshots)
# ---------------------------------------------------------------------------

render_header()
clicked = render_nav(st.session_state.active_tab)
st.session_state.active_tab = clicked

# =========================== LOGIN ===========================
if st.session_state.active_tab == "Login":
    card_start("User Login")
    identifier = st.text_input("Username / Email *", key="login_id")
    password = st.text_input("Password *", type="password", key="login_pw")
    st.checkbox("Remember Me", key="login_remember")

    if st.button("Login", key="login_submit"):
        if not identifier or not password:
            st.warning("Please fill in both fields.")
        else:
            success, message, token = auth.attempt_login(identifier, password)
            if success:
                st.session_state.auth_token = token
                st.success(message)
                st.rerun()
            else:
                st.markdown(f'<div class="fq-alert fq-alert-error">{message}</div>', unsafe_allow_html=True)
    card_end()

# =========================== SIGNUP ===========================
elif st.session_state.active_tab == "Signup":
    card_start("Create Account")
    username = st.text_input("Username *", key="su_username")
    email = st.text_input("Email *", key="su_email")
    password = st.text_input("Password *", type="password", key="su_pw")
    confirm_password = st.text_input("Confirm Password *", type="password", key="su_confirm")

    if password:
        label, css_class, _allowed = pw_strength_badge(password)
        st.markdown(f'<span class="{css_class}">{label}</span>', unsafe_allow_html=True)

    security_question = st.selectbox("Security Question *", SECURITY_QUESTIONS, key="su_question")
    security_answer = st.text_input("Security Answer *", key="su_answer")

    if st.button("Sign Up", key="signup_submit"):
        if not all([username, email, password, confirm_password, security_answer]):
            st.warning("Please fill in all required fields.")
        else:
            success, message = auth.signup_user(
                username, email, password, confirm_password, security_question, security_answer
            )
            if success:
                st.markdown(f'<div class="fq-alert fq-alert-ok">{message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="fq-alert fq-alert-error">{message}</div>', unsafe_allow_html=True)
    card_end()

# =========================== FORGOT PASSWORD ===========================
elif st.session_state.active_tab == "Forgot Password":
    card_start("Forgot Password")
    st.write("Choose a recovery method:")
    method = st.radio("recovery_method", ["Security Question", "Email OTP"], label_visibility="collapsed")
    st.markdown("---")

    if method == "Security Question":
        username = st.text_input("Username *", key="fp_sq_username")
        if st.button("Get Security Question", key="fp_get_question"):
            user = db.get_user_by_identifier(username)
            if not user:
                st.markdown('<div class="fq-alert fq-alert-error">❌ No account found.</div>', unsafe_allow_html=True)
            else:
                st.session_state.otp_stage = {"mode": "sq", "user_id": user["id"], "question": user["security_question"]}

        stage = st.session_state.otp_stage
        if stage and stage.get("mode") == "sq":
            st.info(stage["question"])
            answer = st.text_input("Your Answer *", key="fp_sq_answer")
            new_pw = st.text_input("New Password *", type="password", key="fp_sq_newpw")
            if new_pw:
                label, css_class, _ = pw_strength_badge(new_pw)
                st.markdown(f'<span class="{css_class}">{label}</span>', unsafe_allow_html=True)
            if st.button("Reset Password", key="fp_sq_reset"):
                allowed, msg = auth.check_password_strength(new_pw)
                if not allowed:
                    st.markdown(f'<div class="fq-alert fq-alert-error">{msg}</div>', unsafe_allow_html=True)
                else:
                    conn = db.get_conn()
                    row = conn.execute(
                        "SELECT security_answer_hash FROM users WHERE id = ?", (stage["user_id"],)
                    ).fetchone()
                    conn.close()
                    import bcrypt
                    if bcrypt.checkpw(answer.strip().lower().encode(), row["security_answer_hash"].encode()):
                        db.reset_password(stage["user_id"], new_pw)
                        st.markdown('<div class="fq-alert fq-alert-ok">✅ Password reset successful.</div>', unsafe_allow_html=True)
                        st.session_state.otp_stage = None
                    else:
                        st.markdown('<div class="fq-alert fq-alert-error">❌ Incorrect answer.</div>', unsafe_allow_html=True)

    else:  # Email OTP
        username = st.text_input("Username / Email *", key="fp_otp_username")
        if st.button("Send OTP", key="fp_send_otp"):
            user = db.get_user_by_identifier(username)
            if not user:
                st.markdown('<div class="fq-alert fq-alert-error">❌ No account found.</div>', unsafe_allow_html=True)
            else:
                allowed, msg = auth.can_resend_otp(user)
                if not allowed:
                    st.markdown(f'<div class="fq-alert fq-alert-warn">{msg}</div>', unsafe_allow_html=True)
                else:
                    otp = auth.generate_otp()
                    auth.send_otp_email(user["email"], otp)
                    auth.register_otp_resend(user["id"])
                    st.session_state.otp_stage = {"mode": "otp", "user_id": user["id"], "otp": otp}
                    st.markdown('<div class="fq-alert fq-alert-ok">✅ OTP sent (check console/email).</div>', unsafe_allow_html=True)

        stage = st.session_state.otp_stage
        if stage and stage.get("mode") == "otp":
            entered = st.text_input("Enter OTP *", key="fp_otp_entered")
            new_pw = st.text_input("New Password *", type="password", key="fp_otp_newpw")
            if new_pw:
                label, css_class, _ = pw_strength_badge(new_pw)
                st.markdown(f'<span class="{css_class}">{label}</span>', unsafe_allow_html=True)

            colA, colB = st.columns(2)
            with colA:
                if st.button("Verify & Reset", key="fp_otp_verify"):
                    if entered == stage["otp"]:
                        allowed, msg = auth.check_password_strength(new_pw)
                        if not allowed:
                            st.markdown(f'<div class="fq-alert fq-alert-error">{msg}</div>', unsafe_allow_html=True)
                        else:
                            db.reset_password(stage["user_id"], new_pw)
                            auth.reset_otp_counter(stage["user_id"])
                            st.markdown('<div class="fq-alert fq-alert-ok">✅ Password reset successful.</div>', unsafe_allow_html=True)
                            st.session_state.otp_stage = None
                    else:
                        st.markdown('<div class="fq-alert fq-alert-error">❌ Incorrect OTP.</div>', unsafe_allow_html=True)
            with colB:
                if st.button("Resend OTP", key="fp_otp_resend"):
                    user = db.get_all_users()  # cheap re-lookup by id
                    user_row = next((u for u in user if u["id"] == stage["user_id"]), None)
                    allowed, msg = auth.can_resend_otp(user_row)
                    if not allowed:
                        st.markdown(f'<div class="fq-alert fq-alert-warn">{msg}</div>', unsafe_allow_html=True)
                    else:
                        new_otp = auth.generate_otp()
                        auth.send_otp_email(user_row["email"], new_otp)
                        auth.register_otp_resend(stage["user_id"])
                        stage["otp"] = new_otp
                        st.session_state.otp_stage = stage
                        st.markdown('<div class="fq-alert fq-alert-ok">✅ New OTP sent.</div>', unsafe_allow_html=True)

    card_end()

st.markdown(
    '<p style="text-align:center;color:#5a6482;margin-top:2rem;">'
    'Developed for Infosys Springboard Internship 7.0 · Batch 1 · Milestone 2</p>',
    unsafe_allow_html=True,
)
