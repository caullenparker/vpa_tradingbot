import base64
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LIGHT_LOGO_PATH = PROJECT_ROOT / "assets" / "crescent_lake_logo_light.png"
DARK_LOGO_PATH = PROJECT_ROOT / "assets" / "crescent_lake_logo_dark.png"


def _image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def active_logo_uri() -> str:
    theme = st.session_state.get("theme_mode", "Light")
    path = DARK_LOGO_PATH if theme == "Dark" else LIGHT_LOGO_PATH
    return _image_data_uri(path)


def render_login_brand():
    st.markdown(
        f"""
        <div class="clc-logo-wrap">
            <img src="{active_logo_uri()}" class="clc-login-logo">
        </div>
        <div class="clc-title">VPA Trading Platform</div>
        <div class="clc-caption">A Crescent Lake Capital Platform</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand():
    st.markdown(
        f"""
        <div class="clc-logo-wrap">
            <img src="{active_logo_uri()}" class="clc-sidebar-logo">
        </div>
        <div style="text-align:center;font-weight:750;letter-spacing:.08rem;">
            VPA TRADING PLATFORM
        </div>
        <div style="text-align:center;font-size:.68rem;opacity:.65;letter-spacing:.12rem;">
            DISCIPLINE · PERSPECTIVE · COMPOUNDING
        </div>
        """,
        unsafe_allow_html=True,
    )
