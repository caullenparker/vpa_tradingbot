import streamlit as st


def render():
    st.title("Trade Journal")
    st.caption("A searchable record of entries, exits, P/L, setup notes, and lessons learned.")

    st.info(
        "Next build: searchable trade log, filters, trade-detail views, screenshots, "
        "setup tags, notes, and automatic IBKR fill imports."
    )

    st.subheader("Planned Trade Fields")
    st.markdown(
        """
        - Entry and exit date/time
        - Symbol and direction
        - Quantity, entry, exit, commissions, and P/L
        - Strategy/setup
        - Chart screenshot
        - Trade thesis and review notes
        - Mistakes and lessons learned
        """
    )
