import streamlit as st

def render():
    st.title("Bot Control Center")
    st.caption("Monitor scanner status, IBKR connection, order engine, logs, and automation controls.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Scanner", "Manual")
    col2.metric("Trade Engine", "Local")
    col3.metric("IBKR", "TWS Required")
    col4.metric("Mode", "Paper")

    st.warning("Automation controls are intentionally disabled until the signal-to-order workflow is fully tested.")
    st.subheader("Planned Controls")
    st.markdown(
        """
        - Run scanner now
        - Enable / disable paper trading
        - Max open positions
        - Dollar size per trade
        - Daily loss limit
        - Kill switch
        - View order logs
        """
    )

