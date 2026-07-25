import streamlit as st

from components.auth import require_login
from components.sidebar import render_sidebar
from components.theme import apply_theme
from views import bot_control, dashboard, portfolio, scanner, settings, trade_journal
from views.performance import display_performance_tracker_page


st.set_page_config(
    page_title="Crescent Lake Capital | VPA Trading Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not require_login():
    st.stop()

apply_theme()
page = render_sidebar()

if page == "Dashboard":
    dashboard.render()
elif page == "Market Scanner":
    scanner.render()
elif page == "Portfolio":
    portfolio.render()
elif page == "Performance":
    display_performance_tracker_page()
elif page == "Trade Journal":
    trade_journal.render()
elif page == "Bot Control Center":
    bot_control.render()
elif page == "Settings":
    settings.render()
