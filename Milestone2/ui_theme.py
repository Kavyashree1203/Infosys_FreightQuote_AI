"""
ui_theme.py
Central CSS/theme module for FreightQuote AI.
Injects the dark-navy + cyan→purple gradient look used across
Login / Signup / Forgot Password / Home / Copilot / Admin pages
(carried over from Milestone 1, reused everywhere in Milestone 2).
"""

import streamlit as st

# ---- Brand palette (pulled from the Milestone 1 screens) ----
BG_DARK = "#0a0e1a"          # page background
CARD_BG = "#0f1420"          # card / container background
CARD_BORDER = "#2a3350"      # subtle card border
GRAD_START = "#38bdf8"       # cyan
GRAD_END = "#7c3aed"         # purple
TEXT_MAIN = "#f5f7fa"
TEXT_MUTED = "#9aa5c1"
INPUT_BG = "#ffffff"


def apply_theme():
    """Call once at the top of every Streamlit page/tab."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {BG_DARK};
            color: {TEXT_MAIN};
        }}

        /* ---------- Top nav "pill" buttons: Login / Signup / Forgot Password ---------- */
        div[data-testid="stHorizontalBlock"] .stButton > button {{
            background: linear-gradient(90deg, {GRAD_START}, {GRAD_END});
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.35);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        div[data-testid="stHorizontalBlock"] .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 0 18px rgba(124, 58, 237, 0.55);
        }}

        /* ---------- Title block ---------- */
        .app-title {{
            text-align: center;
            font-size: 2.6rem;
            font-weight: 800;
            color: white;
            text-shadow: 0 0 18px rgba(56, 189, 248, 0.45);
            margin-bottom: 0.2rem;
        }}
        .app-subtitle {{
            text-align: center;
            color: {TEXT_MUTED};
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }}
        .app-divider {{
            width: 90px;
            height: 3px;
            margin: 0.4rem auto 1.4rem auto;
            background: linear-gradient(90deg, {GRAD_START}, {GRAD_END});
            border-radius: 3px;
        }}

        /* ---------- Card container (login/signup/forgot forms) ---------- */
        .fq-card {{
            background-color: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 14px;
            padding: 1.8rem 2rem;
            margin-bottom: 1rem;
        }}
        .fq-card h3 {{
            color: white;
            font-weight: 700;
            border-bottom: 1px solid {CARD_BORDER};
            padding-bottom: 0.6rem;
            margin-bottom: 1rem;
        }}

        /* ---------- Inputs ---------- */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea textarea {{
            background-color: {INPUT_BG} !important;
            color: #111 !important;
            border-radius: 8px !important;
        }}
        label, .stMarkdown p {{
            color: {TEXT_MAIN} !important;
        }}

        /* ---------- Primary submit buttons (Login/Sign Up inside cards) ---------- */
        .fq-card .stButton > button, .stFormSubmitButton > button {{
            background-color: #111827;
            color: white;
            border: 1px solid {CARD_BORDER};
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1.4rem;
        }}
        .fq-card .stButton > button:hover, .stFormSubmitButton > button:hover {{
            border-color: {GRAD_START};
            color: {GRAD_START};
        }}

        /* ---------- Password strength badges ---------- */
        .pw-weak   {{ color: #ef4444; font-weight: 700; }}
        .pw-average{{ color: #f59e0b; font-weight: 700; }}
        .pw-good   {{ color: #22c55e; font-weight: 700; }}

        /* ---------- Lockout / cooldown banners ---------- */
        .fq-alert {{
            border-radius: 8px;
            padding: 0.7rem 1rem;
            margin-top: 0.6rem;
            font-weight: 600;
        }}
        .fq-alert-warn {{ background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid #f59e0b; }}
        .fq-alert-error{{ background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid #ef4444; }}
        .fq-alert-ok   {{ background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid #22c55e; }}

        footer, #MainMenu {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Top banner: title + subtitle + divider — identical on every page."""
    st.markdown('<div class="app-title">Infosys FreightQuote</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Smart Logistics Quotation &amp; Authentication Portal</div>',
        unsafe_allow_html=True,
    )


def render_nav(active: str):
    """
    Top pill-button nav: Login / Signup / Forgot Password.
    `active` is the current tab name; returns the tab the user clicked (or `active`).
    """
    tabs = ["Login", "Signup", "Forgot Password"]
    cols = st.columns(len(tabs))
    clicked = active
    for col, name in zip(cols, tabs):
        with col:
            if st.button(name, key=f"nav_{name}", use_container_width=True):
                clicked = name
    return clicked


def card_start(title: str):
    st.markdown(f'<div class="fq-card"><h3>{title}</h3>', unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def pw_strength_badge(password: str):
    """Returns (label, css_class, allowed:bool) per Section 6 of the spec."""
    n = len(password)
    if n < 5:
        return "🔴 Weak", "pw-weak", False
    elif n < 10:
        return "🟡 Average", "pw-average", True
    else:
        return "🟢 Good", "pw-good", True
