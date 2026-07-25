import streamlit as st

from components.auth import APP_USERNAME
from components.branding import render_sidebar_brand
from components.theme import theme_selector


PAGES = [
    "Dashboard",
    "Market Scanner",
    "Performance",
    "Trade Journal",
    "Bot Control Center",
    "Settings",
]


def render_sidebar():
    with st.sidebar:
        render_sidebar_brand()
        st.divider()
        theme_selector("sidebar_theme_selector")
        st.success(f"Logged in as {APP_USERNAME}")

        if st.button("Logout", use_container_width=True, key="logout_button"):
            st.session_state.authenticated = False
            st.rerun()

        st.divider()
        st.subheader("Navigation")
        page = st.radio("Select Page", PAGES, label_visibility="collapsed")
        return page
