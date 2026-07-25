import streamlit as st

from components.auth import APP_USERNAME
from components.branding import render_sidebar_brand


PAGES = [
    "Dashboard",
    "Market Scanner",
    "Portfolio",
    "Performance",
    "Trade Journal",
    "Bot Control Center",
    "Settings",
]


def render_sidebar():
    with st.sidebar:
        render_sidebar_brand()
        st.divider()
        st.success(f"Logged in as {APP_USERNAME}")

        if st.button("Logout", use_container_width=True, key="logout_button"):
            st.session_state.authenticated = False
            st.rerun()

        st.divider()
        st.subheader("Navigation")
        return st.radio("Select Page", PAGES, label_visibility="collapsed")
