import streamlit as st


def render():
    st.title("Settings")
    st.caption("Platform configuration, appearance, risk limits, and broker setup.")

    st.subheader("Appearance")
    st.write("Use the Light / Dark selector in the sidebar. Your selection persists during the session.")

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
