import streamlit as st


THEMES = {
    "Dark": {
        "bg": "#0d131c",
        "sidebar": "#111a25",
        "card": "#172231",
        "text": "#edf2f7",
        "muted": "#9aa8b8",
        "border": "#2b3a4c",
        "input": "#1a2634",
        "accent": "#274f6d",
        "accent_hover": "#356b92",
    },
    "Light": {
        "bg": "#f5f7fa",
        "sidebar": "#edf1f5",
        "card": "#ffffff",
        "text": "#142438",
        "muted": "#627386",
        "border": "#d5dde6",
        "input": "#ffffff",
        "accent": "#183b56",
        "accent_hover": "#265978",
    },
}


def initialize_theme():
    if "theme_mode" in st.session_state:
        return

    query_theme = st.query_params.get("theme")
    if query_theme in THEMES:
        st.session_state.theme_mode = query_theme
    else:
        st.session_state.theme_mode = "Light"


def set_theme(theme_name: str):
    if theme_name not in THEMES:
        return

    st.session_state.theme_mode = theme_name
    st.query_params["theme"] = theme_name


def apply_theme():
    initialize_theme()
    t = THEMES[st.session_state.theme_mode]

    st.markdown(
        f"""
        <style>
            :root {{
                --bg: {t["bg"]};
                --sidebar: {t["sidebar"]};
                --card: {t["card"]};
                --text: {t["text"]};
                --muted: {t["muted"]};
                --border: {t["border"]};
                --input: {t["input"]};
                --accent: {t["accent"]};
                --accent-hover: {t["accent_hover"]};
            }}

            .stApp {{
                background: var(--bg);
                color: var(--text);
            }}

            header[data-testid="stHeader"] {{
                background: transparent;
            }}

            section[data-testid="stSidebar"] {{
                background: var(--sidebar);
                border-right: 1px solid var(--border);
            }}

            .block-container {{
                max-width: 1500px;
                padding-top: 2rem;
                padding-bottom: 3rem;
            }}

            h1, h2, h3, h4, h5, h6, p, label {{
                color: var(--text);
            }}

            div[data-testid="stMetric"] {{
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 1rem;
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.07);
            }}

            div[data-testid="stMetricLabel"] *,
            div[data-testid="stMetricDelta"] * {{
                color: var(--muted) !important;
            }}

            div[data-testid="stTextInput"] input,
            div[data-testid="stNumberInput"] input,
            div[data-baseweb="select"] > div {{
                background: var(--input) !important;
                color: var(--text) !important;
                border-color: var(--border) !important;
            }}

            div[data-testid="stForm"] {{
                border: none;
                padding: 0;
                background: transparent;
            }}

            button {{
                border-radius: 10px !important;
            }}

            hr {{
                border-color: var(--border);
            }}

            .clc-login-card {{
                max-width: 500px;
                margin: 5vh auto 0 auto;
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 2rem 2.1rem 1.65rem;
                box-shadow: 0 28px 80px rgba(0, 0, 0, 0.14);
            }}

            .clc-logo-wrap {{
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto 0.65rem auto;
            }}

            .clc-login-logo {{
                display: block;
                width: 300px;
                max-width: 92%;
                height: auto;
                margin: 0 auto;
            }}

            .clc-sidebar-logo {{
                display: block;
                width: 185px;
                max-width: 92%;
                height: auto;
                margin: 0 auto 0.35rem auto;
            }}

            .clc-title {{
                text-align: center;
                font-size: 1.9rem;
                font-weight: 800;
                color: var(--text);
                margin-top: 0.35rem;
            }}

            .clc-caption {{
                text-align: center;
                color: var(--muted);
                margin-bottom: 1.35rem;
            }}

            .clc-footer {{
                text-align: center;
                color: var(--muted);
                margin-top: 1.2rem;
                font-size: 0.78rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
