import pandas as pd
import streamlit as st

from pages.performance import load_performance_tracker, make_performance_line_chart


def render():
    st.title("Good morning, Caullen! 👋")
    st.caption("Here’s what’s happening across the Crescent Lake Capital trading platform.")

    data, error = load_performance_tracker()

    current_balance = None
    ytd_gains = None
    latest_win_rate = None
    total_trades = None
    actual_rows = pd.DataFrame()

    if not error and data:
        weekly = data["weekly"]
        actual_rows = weekly[weekly["Actual End Balance"].notna()].copy()

        if not actual_rows.empty:
            latest = actual_rows.iloc[-1]
            current_balance = latest["Actual End Balance"]
            ytd_gains = actual_rows["Actual Gains $"].sum(skipna=True)
            latest_win_rate = latest["Win Rate"]
            total_trades = actual_rows["Number of Trades"].sum(skipna=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Account Balance", f"${current_balance:,.2f}" if pd.notna(current_balance) else "Pending")
    k2.metric("YTD P/L", f"${ytd_gains:,.2f}" if pd.notna(ytd_gains) else "Pending")
    k3.metric("Open Positions", "0")
    k4.metric("Win Rate", f"{latest_win_rate:.1%}" if pd.notna(latest_win_rate) else "Pending")
    k5.metric("Total Trades", f"{int(total_trades):,}" if pd.notna(total_trades) else "Pending")
    k6.metric("Risk Level", "LOW")

    st.divider()

    left, right = st.columns([1.35, 1])

    with left:
        st.subheader("Account Equity Curve")
        if not actual_rows.empty:
            st.plotly_chart(
                make_performance_line_chart(actual_rows),
                use_container_width=True,
                config={"scrollZoom": True, "displayModeBar": True},
            )
        else:
            st.info("Upload or update the Performance Tracker workbook to populate the equity curve.")

    with right:
        st.subheader("System Status")
        st.success("Website: Online")
        st.info("Market Scanner: Manual")
        st.info("IBKR Broker Bridge: Local")
        st.warning("Automated Trading: Disabled")

        st.subheader("Risk Controls")
        st.write("**Trade Size:** $1,000")
        st.write("**Mode:** Paper Trading")
        st.write("**Duplicate Positions:** Blocked")
        st.write("**Live Trading:** Disabled")

    lower_left, lower_right = st.columns([1.2, 1])

    with lower_left:
        st.subheader("Today’s Signals")
        st.info("Daily signal results will appear here after scanner persistence is added.")

    with lower_right:
        st.subheader("Recent Activity")
        st.info("IBKR fills, scanner runs, and bot events will appear here.")

    st.subheader("Recent Trades")
    st.info("The Trade Journal will populate from Excel initially, then from IBKR fills automatically.")
