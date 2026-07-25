import streamlit as st


def render():
    st.title("Trade Journal")
    st.caption("Review entries, exits, performance, setups, notes, and lessons learned.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Journaled Trades", "0")
    c2.metric("Winning Trades", "0")
    c3.metric("Losing Trades", "0")
    c4.metric("Average R", "-")

    st.info(
        "The first journal version will read your existing Excel trade log. "
        "A later version will automatically import IBKR fills."
    )

    st.subheader("Trade Log")
    st.dataframe(
        {
            "Date": [],
            "Symbol": [],
            "Side": [],
            "Entry": [],
            "Exit": [],
            "Quantity": [],
            "P/L": [],
            "Setup": [],
            "Notes": [],
        },
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Trade Review")
    left, right = st.columns(2)

    with left:
        st.text_area("Trade Thesis", disabled=True)
        st.text_area("What Went Well", disabled=True)

    with right:
        st.text_area("Mistakes", disabled=True)
        st.text_area("Lesson Learned", disabled=True)
