import os

import streamlit as st

from components.branding import render_login_brand
from components.theme import apply_theme, initialize_theme


APP_USERNAME = os.getenv("APP_USERNAME", "caullenellis")
APP_PASSWORD = os.getenv("APP_PASSWORD", "PrincessDani")


def require_login() -> bool:
    initialize_theme()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    apply_theme()

    if st.session_state.authenticated:
        return True

    left, center, right = st.columns([1, 1.05, 1])

    with center:
        st.markdown('<div class="clc-login-card">', unsafe_allow_html=True)
        render_login_brand()

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("SIGN IN", use_container_width=True)

        if submitted:
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            st.error("Invalid username or password.")

        st.markdown(
            '<div class="clc-footer">Educational only · Not financial advice</div></div>',
            unsafe_allow_html=True,
        )

    return False
