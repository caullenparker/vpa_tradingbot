import streamlit as st

from components.theme import set_theme


def render():
    st.title("Settings")
    st.caption("Platform appearance, account configuration, risk limits, and broker setup.")

    st.subheader("Appearance")
    selected_theme = st.radio(
        "Theme",
        options=["Light", "Dark"],
        horizontal=True,
        index=0 if st.session_state.get("theme_mode", "Light") == "Light" else 1,
        help="The selected theme is retained through the session and URL."
    )

    if selected_theme != st.session_state.get("theme_mode"):
        set_theme(selected_theme)
        st.rerun()

    st.caption(
        "The login page automatically uses your most recently selected theme."
    )

    st.divider()

    st.subheader("Login")
    st.write("Username and password are read from Render Environment Variables.")

    st.subheader("Risk Defaults")
    st.write("Current planned paper-trading size: **$1,000 per trade**.")

    st.subheader("IBKR Setup")
    st.markdown(
        """
        Local IBKR paper trading requires:
        - TWS Paper Trading open
        - API enabled
        - Socket port `7497`
        - Read-Only API unchecked
        - Local Python trade engine running on your PC
        """
    )

    st.warning(
        "The Render website cannot connect directly to TWS running on your home computer. "
        "Execution remains local until the broker engine is moved to an always-on machine or VPS."
    )
