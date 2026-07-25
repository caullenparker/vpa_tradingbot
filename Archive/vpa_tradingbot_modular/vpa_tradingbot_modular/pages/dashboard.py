import pandas as pd
import streamlit as st

from pages.performance import load_performance_tracker, make_performance_line_chart

def display_home_dashboard():
    st.title("Good morning, Caullen! 👋")
    st.caption("Here’s what’s happening with your trading platform today.")

    data, error = load_performance_tracker()

    current_balance = None
    ytd_gains = None
    latest_win_rate = None
    total_trades = None
    latest_week = None

    if not error and data:
        df_perf = data["weekly"]
        actual_rows = df_perf[df_perf["Actual End Balance"].notna()].copy()

        if not actual_rows.empty:
            latest = actual_rows.iloc[-1]
            current_balance = latest["Actual End Balance"]
            latest_week = int(latest["Week"]) if pd.notna(latest["Week"]) else None
            ytd_gains = actual_rows["Actual Gains $"].sum(skipna=True)
            latest_win_rate = latest["Win Rate"]
            total_trades = actual_rows["Number of Trades"].sum(skipna=True)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    kpi1.metric(
        "Account Balance",
        f"${current_balance:,.2f}" if current_balance is not None and pd.notna(current_balance) else "Pending"
    )

    kpi2.metric(
        "YTD P/L",
        f"${ytd_gains:,.2f}" if ytd_gains is not None and pd.notna(ytd_gains) else "Pending"
    )

    kpi3.metric(
        "Win Rate",
        f"{latest_win_rate:.1%}" if latest_win_rate is not None and pd.notna(latest_win_rate) else "Pending"
    )

    kpi4.metric(
        "Total Trades",
        f"{int(total_trades):,}" if total_trades is not None and pd.notna(total_trades) else "Pending"
    )

    kpi5.metric(
        "Bot Status",
        "Manual Mode"
    )

    st.divider()

    left, right = st.columns([1.35, 1])

    with left:
        st.subheader("Account Equity Curve")

        if not error and data and not actual_rows.empty:
            st.plotly_chart(
                make_performance_line_chart(actual_rows),
                use_container_width=True,
                config={"scrollZoom": True, "displayModeBar": True}
            )
        else:
            st.info("Upload `Performance Tracker.xlsx` to populate the equity curve.")

    with right:
        st.subheader("Platform Status")

        st.success("Website: Online")
        st.info("IBKR: Local TWS Required")
        st.warning("Automation: Not Enabled Yet")
        st.caption("Next milestone: connect VPA signals to the local IBKR paper-trading engine.")

        st.subheader("Next Actions")
        st.markdown(
            """
            1. Verify Performance page.
            2. Build trade journal table.
            3. Add IBKR position monitor.
            4. Wire scanner signals into paper trades.
            """
        )

    st.subheader("Today’s Signals")
    st.info("Signal feed will appear here once we connect the scanner output to saved daily results.")

    st.subheader("Recent Trades")
    st.info("Trade journal will appear here once we add the trade log data source.")

