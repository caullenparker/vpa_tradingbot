import streamlit as st


def render():
    st.title("Bot Control Center")
    st.caption("Monitor scanner status, broker connectivity, execution, logs, and risk controls.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Scanner", "Manual")
    c2.metric("Trade Engine", "Local")
    c3.metric("IBKR", "Paper TWS")
    c4.metric("Automation", "Disabled")

    st.warning(
        "Order automation remains disabled until the complete scanner-to-order workflow "
        "and all safety controls are validated in paper trading."
    )

    left, right = st.columns([1.15, 1])

    with left:
        st.subheader("Services")
        st.success("Render Website — Online")
        st.info("Scanner — Ready for manual runs")
        st.info("IBKR Engine — Runs locally")
        st.warning("Signal Processor — Not connected")
        st.warning("Automated Execution — Disabled")

    with right:
        st.subheader("Risk Configuration")
        st.number_input("Dollar Size per Trade", min_value=100, max_value=100000, value=1000, step=100, disabled=True)
        st.number_input("Maximum Open Positions", min_value=1, max_value=50, value=5, disabled=True)
        st.number_input("Daily Loss Limit", min_value=0, max_value=100000, value=500, step=100, disabled=True)
        st.toggle("Enable Paper Trading", value=False, disabled=True)
        st.toggle("Enable Live Trading", value=False, disabled=True)

    st.subheader("Planned Controls")
    st.markdown(
        """
        - Run scanner now
        - Enable or disable paper execution
        - Maximum open positions
        - One position per ticker
        - Daily loss limit
        - Market-hours validation
        - Emergency kill switch
        - Order and execution logs
        """
    )
