"""
ui_theme.py — "Infosys FreightQuote" dark theme.
Matches the reference design: near-black navy background, cyan->purple
gradient nav buttons, bordered dark cards, white input fields, and a
centered title/subtitle header.
"""

import streamlit as st

BG_DARK = "#0b0f1f"
CARD_BG = "#11162b"
CARD_BORDER = "#2b3358"
GRADIENT = "linear-gradient(90deg, #22d3ee 0%, #7c5cff 100%)"
TEXT_LIGHT = "#e8ecff"
TEXT_MUTED = "#9aa3c7"
INPUT_BG = "#ffffff"
BTN_DARK_BG = "#141a33"

CUSTOM_CSS = f"""
<style>
    /* ---- page background ---- */
    .stApp {{
        background-color: {BG_DARK};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {CARD_BG};
        border-right: 1px solid {CARD_BORDER};
    }}

    /* ---- headings / text ---- */
    h1, h2, h3, h4, h5, label, p, span, div {{
        color: {TEXT_LIGHT};
    }}
    .fq-title {{
        text-align: center;
        font-weight: 800;
        font-size: 2.6rem;
        color: {TEXT_LIGHT};
        text-shadow: 0 0 18px rgba(124,92,255,0.35);
        margin-bottom: 0.2rem;
    }}
    .fq-underline {{
        width: 90px;
        height: 3px;
        margin: 10px auto 14px auto;
        background: {GRADIENT};
        border-radius: 3px;
    }}
    .fq-subtitle {{
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 1.05rem;
        margin-bottom: 28px;
    }}
    .fq-footer {{
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 0.8rem;
        margin-top: 40px;
        opacity: 0.7;
    }}

    /* ---- card container (login / signup / forgot password) ---- */
    .fq-card {{
        background-color: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 14px;
        padding: 28px 30px;
        margin-bottom: 20px;
    }}
    .fq-card h3 {{
        font-size: 1.4rem;
        font-weight: 700;
        border-bottom: 1px solid {CARD_BORDER};
        padding-bottom: 14px;
        margin-bottom: 20px;
    }}
    .fq-inner-box {{
        border: 1px solid {CARD_BORDER};
        border-radius: 10px;
        padding: 22px;
        background-color: rgba(255,255,255,0.02);
    }}

    /* ---- inputs: white pill fields like the mockups ---- */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div {{
        background-color: {INPUT_BG} !important;
        color: #111 !important;
        border-radius: 8px !important;
        border: none !important;
    }}

    /* ---- primary action buttons: gradient pill with lift + glow ---- */
    div.stButton > button,
    div.stFormSubmitButton > button,
    button[kind="primary"],
    button[kind="secondary"] {{
        background: {GRADIENT};
        background-size: 160% 160%;
        color: #ffffff !important;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        letter-spacing: 0.02em;
        padding: 11px 26px;
        box-shadow: 0 4px 14px rgba(124, 92, 255, 0.35);
        transition: transform 0.15s ease, box-shadow 0.15s ease, background-position 0.4s ease;
    }}
    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 22px rgba(34, 211, 238, 0.45);
        background-position: 100% 0%;
        color: #ffffff !important;
    }}
    div.stButton > button:active,
    div.stFormSubmitButton > button:active {{
        transform: translateY(0) scale(0.98);
        box-shadow: 0 3px 10px rgba(124, 92, 255, 0.3);
    }}
    div.stButton > button:focus,
    div.stFormSubmitButton > button:focus {{
        outline: none;
        box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.35), 0 4px 14px rgba(124, 92, 255, 0.35);
    }}

    /* ---- top nav tabs styled as gradient pill buttons ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 14px;
        justify-content: center;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: {GRADIENT};
        border-radius: 10px;
        padding: 10px 26px;
        color: white !important;
        font-weight: 700;
        border: none;
    }}
    .stTabs [aria-selected="true"] {{
        box-shadow: 0 0 14px rgba(124,92,255,0.6);
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: transparent;
    }}

    /* ---- metric cards used on dashboards ---- */
    .metric-card {{
        border: 1px solid {CARD_BORDER};
        background-color: {CARD_BG};
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }}

    /* ---- fq-header used on internal dashboards (admin, agent pages) --- */
    .fq-header {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        padding: 20px 30px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }}
    .fq-badge {{
        background: {GRADIENT};
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
    }}
</style>
"""


def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_brand_header():
    """Centered 'Infosys FreightQuote' title block shown above the auth tabs."""
    st.markdown('<div class="fq-title">⚡ Infosys FreightQuote</div>', unsafe_allow_html=True)
    st.markdown('<div class="fq-underline"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fq-subtitle">Smart Logistics Quotation &amp; Authentication Portal</div>',
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        '<div class="fq-footer">Developed for Infosys Springboard Internship 7.0 · Batch 1 · Milestone 2</div>',
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str, right_label: str = None):
    """Header used on internal pages (Admin dashboard, Agent pages)."""
    right_html = f'<div class="fq-badge">👤 {right_label}</div>' if right_label else ""
    st.markdown(
        f"""
        <div class="fq-header">
            <div>
                <h2 style="margin:0">⚡ {title}</h2>
                <div style="opacity:0.75">{subtitle}</div>
            </div>
            {right_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, icon: str = "📦"):
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:28px">{icon}</div>
            <div style="font-size:26px; font-weight:700">{value}</div>
            <div style="color:#9aa3c7">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_start(title: str = None):
    html = '<div class="fq-card">'
    if title:
        html += f"<h3>{title}</h3>"
    st.markdown(html, unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)
