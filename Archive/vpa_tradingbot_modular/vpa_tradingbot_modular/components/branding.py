from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = PROJECT_ROOT / "assets" / "crescent_lake_logo.png"


def render_login_brand():
    st.image(str(LOGO_PATH), width=300)
    st.markdown('<div class="clc-title">VPA TradingBot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="clc-caption">A Crescent Lake Capital Platform</div>',
        unsafe_allow_html=True,
    )


def render_sidebar_brand():
    st.image(str(LOGO_PATH), width=180)
    st.markdown(
        "<div style='text-align:center;font-weight:750;letter-spacing:.08rem;'>VPA TRADINGBOT</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align:center;font-size:.68rem;opacity:.65;letter-spacing:.12rem;'>"
        "DISCIPLINE · PERSPECTIVE · COMPOUNDING</div>",
        unsafe_allow_html=True,
    )
