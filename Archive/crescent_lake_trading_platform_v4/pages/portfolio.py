import streamlit as st


def render():
    st.title("Portfolio")
    st.caption("Current positions, account allocation, exposure, and unrealized performance.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Positions", "0")
    c2.metric("Invested Capital", "$0.00")
    c3.metric("Unrealized P/L", "$0.00")
    c4.metric("Portfolio Exposure", "0.0%")

    st.info(
        "Portfolio data will populate automatically after the local IBKR bridge "
        "is connected to the website data layer."
    )

    left, right = st.columns([1.35, 1])

    with left:
        st.subheader("Open Positions")
        st.dataframe(
            {
                "Symbol": [],
                "Quantity": [],
                "Average Cost": [],
                "Last Price": [],
                "Market Value": [],
                "Unrealized P/L": [],
                "P/L %": [],
            },
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.subheader("Allocation")
        st.caption("Allocation chart will appear once positions are available.")

    st.subheader("Risk & Exposure")
    r1, r2, r3 = st.columns(3)
    r1.metric("Largest Position", "-")
    r2.metric("Cash Allocation", "100.0%")
    r3.metric("Sector Concentration", "-")
