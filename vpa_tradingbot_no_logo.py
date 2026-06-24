# VPA Dashboard Strategy Lab with Portfolio Backtest + Market Scanner
# Educational only. Not financial advice.

import os
import time
from io import StringIO
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(page_title="VPA TradingBot", layout="wide")


# -----------------------------
# Simple Login Gate
# -----------------------------

APP_USERNAME = os.getenv("APP_USERNAME", "caullenellis")
APP_PASSWORD = os.getenv("APP_PASSWORD", "PrincessDani")


def login_gate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        with st.sidebar:
            st.markdown(
                """
                <div style="text-align:center; padding: 0.65rem 0 1rem 0;">
                    <div style="font-size:1.25rem; font-weight:900; color:#f5f5f5;">
                        VPA TradingBot
                    </div>
                    <div style="font-size:0.72rem; color:rgba(255,255,255,0.48); letter-spacing:0.16rem;">
                        VOLUME · PRICE · ANALYSIS
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.success(f"Logged in as {APP_USERNAME}")

            if st.button("Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

        return True

    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at 50% 8%, rgba(247, 242, 171, 0.09), transparent 18%),
                    radial-gradient(circle at bottom left, rgba(247, 242, 171, 0.045), transparent 24%),
                    linear-gradient(135deg, #262933 0%, #181b23 48%, #11141b 100%);
            }

            header[data-testid="stHeader"] {
                background: transparent;
            }

            .block-container {
                padding-top: 3rem !important;
                max-width: 1120px !important;
            }

            .brand-title {
                text-align: center;
                font-size: 3.4rem;
                line-height: 1.05;
                font-weight: 950;
                letter-spacing: -0.08rem;
                color: #f5f5f5;
                margin-top: 1.5rem;
                margin-bottom: 0.35rem;
            }

            .brand-title .gold {
                color: #f7f2ab;
            }

            .brand-subtitle {
                text-align: center;
                color: rgba(255,255,255,0.55);
                letter-spacing: 0.35rem;
                text-transform: uppercase;
                font-size: 0.95rem;
                margin-bottom: 3rem;
            }

            .login-heading {
                text-align: center;
                color: #f7f2ab;
                font-size: 2rem;
                font-weight: 850;
                margin-bottom: 0.25rem;
            }

            .login-caption {
                text-align: center;
                color: rgba(255,255,255,0.65);
                font-size: 1rem;
                margin-bottom: 2rem;
            }

            div[data-testid="stForm"] {
                border: none;
                padding: 0;
                background: transparent;
            }

            div[data-testid="stTextInput"] label,
            div[data-testid="stCheckbox"] label {
                color: rgba(255,255,255,0.90) !important;
                font-weight: 650;
            }

            div[data-testid="stTextInput"] input {
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.16);
                background-color: rgba(255,255,255,0.055);
                min-height: 3rem;
                color: #f5f5f5;
            }

            div[data-testid="stTextInput"] input::placeholder {
                color: rgba(255,255,255,0.42);
            }

            button[kind="primaryFormSubmit"] {
                border-radius: 10px;
                min-height: 3rem;
                font-weight: 850;
                letter-spacing: 0.04rem;
                background: rgba(255,255,255,0.035);
                color: #f5f5f5;
                border: 1px solid rgba(255,255,255,0.22);
            }

            button[kind="primaryFormSubmit"]:hover {
                border-color: #f7f2ab;
                color: #f7f2ab;
                background: rgba(247,242,171,0.08);
            }

            .secure-note {
                text-align:center;
                color:rgba(255,255,255,0.50);
                margin-top: 2.1rem;
                font-size: 0.95rem;
            }

            .bottom-note {
                text-align:center;
                margin-top: 1.5rem;
                color: rgba(255, 255, 255, 0.30);
                font-size: 0.82rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="brand-title"><span class="gold">VPA</span> TradingBot</div>
        <div class="brand-subtitle">Volume · Price · Analysis</div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 2.25, 1])

    with center:
        st.markdown(
            """
            <div class="login-heading">Sign In</div>
            <div class="login-caption">Access your trading dashboard</div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            remember = st.checkbox("Remember me")
            submitted = st.form_submit_button("SIGN IN", use_container_width=True)

        if submitted:
            if username == APP_USERNAME and password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.markdown(
        """
        <div class="secure-note">🛡️ Secure access to your trading dashboard</div>
        <div class="bottom-note">© 2026 VPA TradingBot · Educational only · Not financial advice</div>
        """,
        unsafe_allow_html=True
    )

    return False


if not login_gate():
    st.stop()


# -----------------------------
# Data Helpers
# -----------------------------

@st.cache_data(ttl=60 * 60)
def get_data(ticker, period, interval):
    ticker = ticker.strip().upper()

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        raise ValueError(f"No data downloaded for {ticker}")

    df = df.dropna()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [str(c).lower() for c in df.columns]

    required_cols = {"open", "high", "low", "close", "volume"}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(f"{ticker} missing required columns: {missing_cols}")

    return df


def read_html_tables_with_headers(url):
    """
    Wikipedia sometimes blocks default Python/pandas requests with HTTP 403.
    This uses browser-like headers before passing the HTML into pandas.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    return pd.read_html(StringIO(response.text))


@st.cache_data(ttl=60 * 60 * 24)
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = read_html_tables_with_headers(url)
    df = tables[0]
    tickers = df["Symbol"].astype(str).str.replace(".", "-", regex=False).str.upper().tolist()
    tickers = [t for t in tickers if t and t != "NAN"]
    return sorted(list(set(tickers)))


@st.cache_data(ttl=60 * 60 * 24)
def get_nasdaq100_tickers():
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    tables = read_html_tables_with_headers(url)

    ticker_col = None
    ticker_df = None

    for table in tables:
        for col in table.columns:
            col_name = str(col).lower()
            if col_name in ["ticker", "symbol"] or "ticker" in col_name or "symbol" in col_name:
                ticker_col = col
                ticker_df = table
                break
        if ticker_col is not None:
            break

    if ticker_df is None:
        raise ValueError("Could not find Nasdaq-100 ticker table from Wikipedia.")

    tickers = ticker_df[ticker_col].astype(str).str.replace(".", "-", regex=False).str.upper().tolist()
    tickers = [t for t in tickers if t and t != "NAN"]

    return sorted(list(set(tickers)))


def parse_tickers(ticker_text):
    tickers = (
        ticker_text
        .replace("\n", ",")
        .replace(" ", ",")
        .split(",")
    )

    tickers = [t.strip().upper() for t in tickers if t.strip()]
    tickers = [t.replace(".", "-") for t in tickers]

    return sorted(list(dict.fromkeys(tickers)))


# -----------------------------
# Strategy Logic
# -----------------------------

def add_vpa_features(
    df,
    vol_window,
    trend_window,
    high_volume_threshold,
    low_volume_threshold,
    wide_spread_threshold,
    narrow_spread_threshold
):
    df = df.copy()

    df["spread"] = df["high"] - df["low"]
    df["body"] = abs(df["close"] - df["open"])
    df["range_pos"] = (df["close"] - df["low"]) / df["spread"].replace(0, np.nan)

    df["vol_ma"] = df["volume"].rolling(vol_window).mean()
    df["spread_ma"] = df["spread"].rolling(vol_window).mean()

    df["high_volume"] = df["volume"] > df["vol_ma"] * high_volume_threshold
    df["low_volume"] = df["volume"] < df["vol_ma"] * low_volume_threshold
    df["wide_spread"] = df["spread"] > df["spread_ma"] * wide_spread_threshold
    df["narrow_spread"] = df["spread"] < df["spread_ma"] * narrow_spread_threshold

    df["trend"] = df["close"].rolling(trend_window).mean()
    df["downtrend"] = df["close"] < df["trend"]
    df["uptrend"] = df["close"] > df["trend"]

    return df


def generate_signals(df, stopping_window):
    df = df.copy()

    df["stopping_volume"] = (
        df["downtrend"] &
        df["high_volume"] &
        df["wide_spread"] &
        (df["close"] < df["open"]) &
        (df["range_pos"] > 0.35)
    )

    df["bullish_test"] = (
        df["low_volume"] &
        df["narrow_spread"] &
        (df["range_pos"] > 0.40) &
        (df["stopping_volume"].rolling(stopping_window).sum().shift(1) > 0)
    )

    df["upthrust"] = (
        df["uptrend"] &
        df["high_volume"] &
        df["wide_spread"] &
        (df["close"] > df["open"]) &
        (df["range_pos"] < 0.65)
    )

    df["buy_signal"] = df["bullish_test"]
    df["sell_signal"] = df["upthrust"]

    return df


def backtest(df, initial_cash, stop_loss, take_profit):
    cash = float(initial_cash)
    position = 0.0
    entry_price = 0.0
    equity_curve = []
    trades = []

    for i in range(1, len(df)):
        price = float(df["close"].iloc[i])
        date = df.index[i]

        if position == 0:
            if bool(df["buy_signal"].iloc[i]):
                position = cash / price
                entry_price = price
                cash = 0.0

                trades.append({
                    "date": date,
                    "type": "BUY",
                    "price": price,
                    "pnl_pct": np.nan
                })

        else:
            pnl_pct = (price - entry_price) / entry_price

            exit_trade = (
                bool(df["sell_signal"].iloc[i]) or
                pnl_pct <= -stop_loss or
                pnl_pct >= take_profit
            )

            if exit_trade:
                cash = position * price
                position = 0.0

                trades.append({
                    "date": date,
                    "type": "SELL",
                    "price": price,
                    "pnl_pct": pnl_pct
                })

        equity = cash if position == 0 else position * price
        equity_curve.append(equity)

    trades_df = pd.DataFrame(trades)
    equity = pd.Series(equity_curve, index=df.index[1:])

    return trades_df, equity


def calculate_max_drawdown(equity):
    if equity.empty:
        return 0.0

    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    return float(drawdown.min() * 100)


def summarize_trades(trades):
    if trades.empty or "SELL" not in trades["type"].values:
        return 0.0

    sells = trades[trades["type"] == "SELL"].copy()

    if sells.empty or sells["pnl_pct"].dropna().empty:
        return 0.0

    win_rate = (sells["pnl_pct"] > 0).mean() * 100

    return float(win_rate)


def run_strategy_for_ticker(
    ticker,
    period,
    interval,
    initial_cash,
    stop_loss,
    take_profit,
    vol_window,
    trend_window,
    stopping_window,
    high_volume_threshold,
    low_volume_threshold,
    wide_spread_threshold,
    narrow_spread_threshold
):
    df = get_data(ticker, period, interval)

    df = add_vpa_features(
        df,
        vol_window,
        trend_window,
        high_volume_threshold,
        low_volume_threshold,
        wide_spread_threshold,
        narrow_spread_threshold
    )

    df = generate_signals(df, stopping_window)

    trades, equity = backtest(df, initial_cash, stop_loss, take_profit)

    final_equity = float(equity.iloc[-1]) if not equity.empty else float(initial_cash)
    total_return = (final_equity / initial_cash - 1) * 100 if initial_cash else 0.0
    max_drawdown = calculate_max_drawdown(equity)
    win_rate = summarize_trades(trades)

    summary = {
        "Ticker": ticker,
        "Initial Cash": initial_cash,
        "Final Equity": final_equity,
        "Total Return %": total_return,
        "Number of Trades": len(trades),
        "Buy Signals": int(df["buy_signal"].sum()),
        "Sell Signals": int(df["sell_signal"].sum()),
        "Win Rate %": win_rate,
        "Max Drawdown %": max_drawdown,
        "Last Close": float(df["close"].iloc[-1]),
        "Latest Buy Signal": bool(df["buy_signal"].iloc[-1]),
        "Latest Sell Signal": bool(df["sell_signal"].iloc[-1])
    }

    return df, trades, equity, summary


# -----------------------------
# Chart Helpers
# -----------------------------

def make_price_chart(df, trades, title="Price Chart with Buy/Sell Signals and Volume"):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25]
    )

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["trend"],
        mode="lines",
        name="Trend MA"
    ), row=1, col=1)

    if not trades.empty:
        buys = trades[trades["type"] == "BUY"]
        sells = trades[trades["type"] == "SELL"]

        fig.add_trace(go.Scatter(
            x=buys["date"],
            y=buys["price"],
            mode="markers",
            marker=dict(size=12, symbol="triangle-up", color="gold"),
            name="BUY"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=sells["date"],
            y=sells["price"],
            mode="markers",
            marker=dict(size=12, symbol="triangle-down", color="red"),
            name="SELL"
        ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.index,
        y=df["volume"],
        marker_color="blue",
        name="Volume",
        opacity=0.45
    ), row=2, col=1)

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        yaxis2_title="Volume",
        height=780,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        dragmode="zoom",
        hovermode="x unified"
    )

    fig.update_xaxes(
        rangeslider_visible=False,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor"
    )

    fig.update_yaxes(
        fixedrange=False,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor"
    )

    return fig


def make_equity_chart(equity, title="Equity Curve"):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=equity.index,
        y=equity.values,
        mode="lines",
        name="Equity Curve"
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Account Value",
        height=420,
        dragmode="zoom",
        hovermode="x unified"
    )

    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig


def display_trades_table(trades):
    if trades.empty:
        st.info("No trades were triggered with the current settings.")
        return

    display_trades = trades.copy()
    display_trades["date"] = pd.to_datetime(display_trades["date"]).dt.strftime("%Y-%m-%d")
    display_trades["pnl_pct"] = display_trades["pnl_pct"] * 100
    st.dataframe(display_trades, use_container_width=True)



# -----------------------------
# Performance Tracker Helpers
# -----------------------------

TRACKER_FILE = os.getenv("PERFORMANCE_TRACKER_FILE", "Performance Tracker.xlsx")


def _excel_serial_to_datetime(series):
    return pd.to_datetime(series, unit="D", origin="1899-12-30", errors="coerce")


def _numeric_clean(series):
    return pd.to_numeric(series.replace("-", np.nan), errors="coerce")


@st.cache_data(ttl=300)
def load_performance_tracker(file_path=TRACKER_FILE):
    """
    Loads the Performance Tracker workbook.

    Expected workbook:
    - Sheet: Options
    - Main weekly tracker starts with headers on row 3 and data on row 4.
    """
    try:
        raw = pd.read_excel(file_path, sheet_name="Options", header=None, engine="openpyxl")
    except FileNotFoundError:
        return None, f"Could not find '{file_path}'. Upload it to the same folder as this app."
    except Exception as e:
        return None, f"Could not read '{file_path}': {e}"

    rows = raw.iloc[3:].copy()

    df = pd.DataFrame({
        "Week": rows.iloc[:, 1],
        "Week Start": rows.iloc[:, 2],
        "Year": rows.iloc[:, 3],
        "Budget Start Balance": rows.iloc[:, 4],
        "Budget Gains $": rows.iloc[:, 5],
        "Budget Gains %": rows.iloc[:, 6],
        "Budget Deposits": rows.iloc[:, 7],
        "Budget End Balance": rows.iloc[:, 8],
        "Forecast Gains $": rows.iloc[:, 10],
        "Forecast Gains %": rows.iloc[:, 11],
        "Forecast Deposits": rows.iloc[:, 12],
        "Forecast End Balance": rows.iloc[:, 13],
        "Actual Start Balance": rows.iloc[:, 15],
        "Actual Gains $": rows.iloc[:, 16],
        "Actual Gains %": rows.iloc[:, 17],
        "Actual Deposits": rows.iloc[:, 18],
        "Actual End Balance": rows.iloc[:, 19],
        "Variance vs Budget": rows.iloc[:, 21],
        "Variance vs Forecast": rows.iloc[:, 22],
        "Trend": rows.iloc[:, 23],
        "Win Rate": rows.iloc[:, 24],
        "Position % of Balance": rows.iloc[:, 26],
        "Position % of Position": rows.iloc[:, 27],
        "Total Costs": rows.iloc[:, 28],
        "Number of Trades": rows.iloc[:, 29],
        "Position Cost % of Balance": rows.iloc[:, 30],
        "Aggressive Max": rows.iloc[:, 31],
        "Aggressive %": rows.iloc[:, 32],
        "Fees": rows.iloc[:, 33],
        "Comments": rows.iloc[:, 34],
    })

    df = df[pd.to_numeric(df["Week"], errors="coerce").notna()].copy()

    numeric_cols = [
        "Week", "Year", "Budget Start Balance", "Budget Gains $", "Budget Gains %",
        "Budget Deposits", "Budget End Balance", "Forecast Gains $", "Forecast Gains %",
        "Forecast Deposits", "Forecast End Balance", "Actual Start Balance",
        "Actual Gains $", "Actual Gains %", "Actual Deposits", "Actual End Balance",
        "Variance vs Budget", "Variance vs Forecast", "Trend", "Win Rate",
        "Position % of Balance", "Position % of Position", "Total Costs",
        "Number of Trades", "Position Cost % of Balance", "Aggressive Max",
        "Aggressive %", "Fees"
    ]

    for col in numeric_cols:
        df[col] = _numeric_clean(df[col])

    df["Week Start"] = _excel_serial_to_datetime(df["Week Start"])
    df = df.sort_values("Week Start").reset_index(drop=True)

    ltd = raw.iloc[3:10, 37:39].copy()
    ltd.columns = ["Label", "Amount"]
    ltd = ltd.dropna(how="all")
    ltd["Amount"] = pd.to_numeric(ltd["Amount"], errors="coerce")

    return {"weekly": df, "ltd": ltd}, None


def make_performance_line_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Week Start"],
        y=df["Actual End Balance"],
        mode="lines+markers",
        name="Actual End Balance"
    ))

    fig.add_trace(go.Scatter(
        x=df["Week Start"],
        y=df["Budget End Balance"],
        mode="lines",
        name="Budget End Balance"
    ))

    fig.add_trace(go.Scatter(
        x=df["Week Start"],
        y=df["Forecast End Balance"],
        mode="lines",
        name="Forecast End Balance"
    ))

    fig.update_layout(
        title="Ending Balance: Actual vs Budget vs Forecast",
        xaxis_title="Week",
        yaxis_title="Ending Balance",
        height=430,
        hovermode="x unified",
        dragmode="zoom",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )

    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig


def make_weekly_gains_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["Week Start"],
        y=df["Actual Gains $"],
        name="Actual Gains $"
    ))

    fig.update_layout(
        title="Weekly Actual Gains / Losses",
        xaxis_title="Week",
        yaxis_title="Actual Gains $",
        height=360,
        hovermode="x unified",
        dragmode="zoom"
    )

    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig


def display_performance_tracker_page():
    st.title("Performance Tracker")
    st.caption("Weekly trading account performance, budget, forecast, actuals, variance, and position sizing.")

    data, error = load_performance_tracker()

    if error:
        st.error(error)
        st.info("For deployment, upload `Performance Tracker.xlsx` to your GitHub repo beside the Streamlit `.py` file.")
        return

    df = data["weekly"]
    ltd = data["ltd"]

    actual_rows = df[df["Actual End Balance"].notna()].copy()

    if actual_rows.empty:
        st.warning("No actual performance rows found yet.")
        st.dataframe(df, use_container_width=True)
        return

    latest = actual_rows.iloc[-1]

    current_balance = latest["Actual End Balance"]
    latest_week = int(latest["Week"])
    ytd_gains = actual_rows["Actual Gains $"].sum(skipna=True)
    ytd_deposits = actual_rows["Actual Deposits"].sum(skipna=True)
    total_trades = actual_rows["Number of Trades"].sum(skipna=True)
    latest_win_rate = latest["Win Rate"]
    variance_vs_budget = latest["Variance vs Budget"]
    variance_vs_forecast = latest["Variance vs Forecast"]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Current Balance", f"${current_balance:,.2f}" if pd.notna(current_balance) else "-")
    kpi2.metric("YTD Actual Gains", f"${ytd_gains:,.2f}" if pd.notna(ytd_gains) else "-")
    kpi3.metric("YTD Deposits", f"${ytd_deposits:,.2f}" if pd.notna(ytd_deposits) else "-")
    kpi4.metric("Latest Week", f"Week {latest_week}")

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    kpi5.metric("Latest Win Rate", f"{latest_win_rate:.1%}" if pd.notna(latest_win_rate) else "-")
    kpi6.metric("Total Trades", f"{int(total_trades):,}" if pd.notna(total_trades) else "-")
    kpi7.metric("Variance vs Budget", f"${variance_vs_budget:,.2f}" if pd.notna(variance_vs_budget) else "-")
    kpi8.metric("Variance vs Forecast", f"${variance_vs_forecast:,.2f}" if pd.notna(variance_vs_forecast) else "-")

    st.divider()

    chart_col1, chart_col2 = st.columns([1.35, 1])

    with chart_col1:
        st.plotly_chart(
            make_performance_line_chart(actual_rows),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

    with chart_col2:
        st.plotly_chart(
            make_weekly_gains_chart(actual_rows),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

    st.subheader("Weekly Performance Table")

    display_cols = [
        "Week", "Week Start", "Budget End Balance", "Forecast End Balance",
        "Actual End Balance", "Actual Gains $", "Actual Gains %", "Actual Deposits",
        "Variance vs Budget", "Variance vs Forecast", "Win Rate",
        "Position % of Balance", "Total Costs", "Number of Trades", "Fees", "Comments"
    ]

    display_df = df[display_cols].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Week Start": st.column_config.DateColumn("Week Start", format="YYYY-MM-DD"),
            "Budget End Balance": st.column_config.NumberColumn("Budget End Balance", format="$%.2f"),
            "Forecast End Balance": st.column_config.NumberColumn("Forecast End Balance", format="$%.2f"),
            "Actual End Balance": st.column_config.NumberColumn("Actual End Balance", format="$%.2f"),
            "Actual Gains $": st.column_config.NumberColumn("Actual Gains $", format="$%.2f"),
            "Actual Gains %": st.column_config.NumberColumn("Actual Gains %", format="percent"),
            "Actual Deposits": st.column_config.NumberColumn("Actual Deposits", format="$%.2f"),
            "Variance vs Budget": st.column_config.NumberColumn("Variance vs Budget", format="$%.2f"),
            "Variance vs Forecast": st.column_config.NumberColumn("Variance vs Forecast", format="$%.2f"),
            "Win Rate": st.column_config.NumberColumn("Win Rate", format="percent"),
            "Position % of Balance": st.column_config.NumberColumn("Position % of Balance", format="percent"),
            "Total Costs": st.column_config.NumberColumn("Total Costs", format="$%.2f"),
            "Fees": st.column_config.NumberColumn("Fees", format="$%.2f"),
        }
    )

    if ltd is not None and not ltd.empty:
        st.subheader("LTD Losses / Net Gains-Losses")
        st.dataframe(
            ltd,
            use_container_width=True,
            hide_index=True,
            column_config={"Amount": st.column_config.NumberColumn("Amount", format="$%.2f")}
        )


# -----------------------------
# Sidebar Inputs
# -----------------------------

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Portfolio Backtest", "Market Scanner", "Performance Tracker"],
    index=0
)

st.sidebar.divider()

if page in ["Portfolio Backtest", "Market Scanner"]:
    st.sidebar.header("Strategy Inputs")

    if page == "Portfolio Backtest":
        ticker_text = st.sidebar.text_area(
            "Tickers",
            value="SPY",
            help="Enter one or more tickers separated by commas, spaces, or new lines."
        )

    elif page == "Market Scanner":
        universe_choice = st.sidebar.selectbox(
            "Scanner Universe",
            ["S&P 500", "Nasdaq 100", "Both", "Custom List"],
            index=0
        )

        custom_scanner_tickers = ""
        if universe_choice == "Custom List":
            custom_scanner_tickers = st.sidebar.text_area(
                "Custom Scanner Tickers",
                value="SPY, QQQ, TLT, AAPL, MSFT, NVDA, AMZN, META, GOOGL",
                help="Enter tickers separated by commas, spaces, or new lines."
            )

        max_tickers = st.sidebar.number_input(
            "Max Tickers to Scan",
            min_value=10,
            max_value=700,
            value=100,
            step=10,
            help="Use a smaller number first for speed. Increase once you know it works."
        )

    period = st.sidebar.selectbox(
        "Historical Period",
        ["6mo", "1y", "2y", "3y", "5y", "10y"],
        index=3
    )

    interval = st.sidebar.selectbox(
        "Interval",
        ["1d", "1h", "30m", "15m"],
        index=0,
        help="Intraday intervals may be limited by Yahoo Finance history availability."
    )

    st.sidebar.subheader("VPA Settings")

    vol_window = st.sidebar.slider("Volume Lookback Window", 5, 100, 20)
    trend_window = st.sidebar.slider("Trend Window", 5, 200, 20)
    stopping_window = st.sidebar.slider("Stopping Volume Window", 2, 30, 10)

    high_volume_threshold = st.sidebar.slider("High Volume Threshold", 1.00, 3.00, 1.05, 0.05)
    low_volume_threshold = st.sidebar.slider("Low Volume Threshold", 0.20, 1.50, 1.00, 0.05)
    wide_spread_threshold = st.sidebar.slider("Wide Spread Threshold", 1.00, 3.00, 1.05, 0.05)
    narrow_spread_threshold = st.sidebar.slider("Narrow Spread Threshold", 0.20, 1.50, 0.95, 0.05)

    st.sidebar.subheader("Backtest Settings")

    initial_cash = st.sidebar.number_input("Initial Cash", value=10000, step=1000)
    stop_loss = st.sidebar.slider("Stop Loss %", 1, 50, 4) / 100
    take_profit = st.sidebar.slider("Take Profit %", 1, 100, 8) / 100

elif page == "Performance Tracker":
    st.sidebar.header("Performance Tracker")
    st.sidebar.caption("Reads `Performance Tracker.xlsx` from the app folder.")
    st.sidebar.info("Upload the workbook to GitHub beside the app file before deploying.")


# -----------------------------
# Page 1: Portfolio Backtest
# -----------------------------

if page == "Portfolio Backtest":
    st.title("VPA TradingBot")
    st.caption("Volume Price Analysis trading research dashboard. Educational only. Not financial advice.")

    run_button = st.button("Run Portfolio Backtest", type="primary")

    if run_button:
        tickers = parse_tickers(ticker_text)

        if not tickers:
            st.error("Please enter at least one ticker.")
            st.stop()

        cash_per_ticker = initial_cash / len(tickers)

        summaries = []
        equity_curves = {}
        data_by_ticker = {}
        trades_by_ticker = {}
        errors = []

        progress = st.progress(0)
        status = st.empty()

        for idx, ticker in enumerate(tickers):
            status.write(f"Running backtest for {ticker}...")

            try:
                df, trades, equity, summary = run_strategy_for_ticker(
                    ticker=ticker,
                    period=period,
                    interval=interval,
                    initial_cash=cash_per_ticker,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    vol_window=vol_window,
                    trend_window=trend_window,
                    stopping_window=stopping_window,
                    high_volume_threshold=high_volume_threshold,
                    low_volume_threshold=low_volume_threshold,
                    wide_spread_threshold=wide_spread_threshold,
                    narrow_spread_threshold=narrow_spread_threshold
                )

                summaries.append(summary)
                equity_curves[ticker] = equity
                data_by_ticker[ticker] = df
                trades_by_ticker[ticker] = trades

            except Exception as e:
                errors.append({"Ticker": ticker, "Error": str(e)})

            progress.progress((idx + 1) / len(tickers))

        status.empty()

        if not summaries:
            st.error("No tickers successfully completed.")
            if errors:
                st.dataframe(pd.DataFrame(errors), use_container_width=True)
            st.stop()

        summary_df = pd.DataFrame(summaries).sort_values("Total Return %", ascending=False)

        combined_equity = pd.concat(equity_curves.values(), axis=1)
        combined_equity.columns = list(equity_curves.keys())
        portfolio_equity = combined_equity.ffill().sum(axis=1)

        final_portfolio_equity = float(portfolio_equity.iloc[-1]) if not portfolio_equity.empty else float(initial_cash)
        portfolio_total_return = (final_portfolio_equity / initial_cash - 1) * 100
        total_trades = int(summary_df["Number of Trades"].sum())

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Final Portfolio Equity", f"${final_portfolio_equity:,.2f}")
        col2.metric("Portfolio Total Return", f"{portfolio_total_return:.2f}%")
        col3.metric("Number of Trades", total_trades)
        col4.metric("Tickers Tested", len(summary_df))

        st.subheader("Portfolio Equity Curve")
        st.plotly_chart(
            make_equity_chart(portfolio_equity, title="Portfolio Equity Curve"),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

        st.subheader("Ticker Results")
        st.dataframe(
            summary_df.style.format({
                "Initial Cash": "${:,.2f}",
                "Final Equity": "${:,.2f}",
                "Total Return %": "{:.2f}%",
                "Win Rate %": "{:.2f}%",
                "Max Drawdown %": "{:.2f}%",
                "Last Close": "${:,.2f}"
            }),
            use_container_width=True
        )

        selected_ticker = st.selectbox(
            "Select ticker to inspect",
            list(summary_df["Ticker"]),
            index=0
        )

        st.subheader(f"{selected_ticker} Price Chart")
        st.plotly_chart(
            make_price_chart(
                data_by_ticker[selected_ticker],
                trades_by_ticker[selected_ticker],
                title=f"{selected_ticker} Price Chart with Buy/Sell Signals and Volume"
            ),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

        st.subheader(f"{selected_ticker} Equity Curve")
        st.plotly_chart(
            make_equity_chart(
                equity_curves[selected_ticker],
                title=f"{selected_ticker} Equity Curve"
            ),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

        st.subheader(f"{selected_ticker} Trades")
        display_trades_table(trades_by_ticker[selected_ticker])

        if errors:
            with st.expander("Tickers with errors"):
                st.dataframe(pd.DataFrame(errors), use_container_width=True)

    else:
        st.info("Adjust the inputs on the left, then click Run Portfolio Backtest.")


# -----------------------------
# Page 2: Market Scanner
# -----------------------------

else:
    st.title("VPA Market Scanner")
    st.caption("Scans S&P 500 and/or Nasdaq 100 tickers using the same strategy settings, then ranks by Total Return %. Educational only. Not financial advice.")

    st.warning(
        "The scanner can take a while because it downloads and backtests many tickers. "
        "Start with 50–100 tickers first, then increase the limit."
    )

    run_scanner = st.button("Run Market Scanner", type="primary")

    if run_scanner:
        try:
            if universe_choice == "S&P 500":
                tickers = get_sp500_tickers()
            elif universe_choice == "Nasdaq 100":
                tickers = get_nasdaq100_tickers()
            elif universe_choice == "Both":
                tickers = sorted(list(set(get_sp500_tickers() + get_nasdaq100_tickers())))
            else:
                tickers = parse_tickers(custom_scanner_tickers)

            tickers = tickers[:int(max_tickers)]

        except Exception as e:
            st.error(f"Could not load ticker universe: {e}")
            st.stop()

        st.write(f"Scanning **{len(tickers)}** tickers from **{universe_choice}**...")

        scanner_initial_cash = 10000

        results = []
        data_by_ticker = {}
        trades_by_ticker = {}
        equity_by_ticker = {}
        errors = []

        progress = st.progress(0)
        status = st.empty()

        start_time = time.time()

        for idx, ticker in enumerate(tickers):
            status.write(f"Scanning {idx + 1} of {len(tickers)}: {ticker}")

            try:
                df, trades, equity, summary = run_strategy_for_ticker(
                    ticker=ticker,
                    period=period,
                    interval=interval,
                    initial_cash=scanner_initial_cash,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    vol_window=vol_window,
                    trend_window=trend_window,
                    stopping_window=stopping_window,
                    high_volume_threshold=high_volume_threshold,
                    low_volume_threshold=low_volume_threshold,
                    wide_spread_threshold=wide_spread_threshold,
                    narrow_spread_threshold=narrow_spread_threshold
                )

                results.append(summary)
                data_by_ticker[ticker] = df
                trades_by_ticker[ticker] = trades
                equity_by_ticker[ticker] = equity

            except Exception as e:
                errors.append({"Ticker": ticker, "Error": str(e)})

            progress.progress((idx + 1) / len(tickers))

        status.empty()

        elapsed = time.time() - start_time

        if not results:
            st.error("No tickers successfully completed.")
            if errors:
                st.dataframe(pd.DataFrame(errors), use_container_width=True)
            st.stop()

        results_df = pd.DataFrame(results).sort_values("Total Return %", ascending=False)
        results_df.insert(0, "Rank", range(1, len(results_df) + 1))

        st.success(f"Scanner complete in {elapsed:.1f} seconds.")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tickers Scanned", len(results_df))
        col2.metric("Best Ticker", results_df.iloc[0]["Ticker"])
        col3.metric("Best Total Return", f"{results_df.iloc[0]['Total Return %']:.2f}%")
        col4.metric("Avg Total Return", f"{results_df['Total Return %'].mean():.2f}%")

        st.subheader("Highest Performing Tickers Ranked by Total Return")

        st.dataframe(
            results_df.style.format({
                "Initial Cash": "${:,.2f}",
                "Final Equity": "${:,.2f}",
                "Total Return %": "{:.2f}%",
                "Win Rate %": "{:.2f}%",
                "Max Drawdown %": "{:.2f}%",
                "Last Close": "${:,.2f}"
            }),
            use_container_width=True
        )

        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Scanner Results as CSV",
            data=csv,
            file_name="vpa_market_scanner_results.csv",
            mime="text/csv"
        )

        top_tickers = results_df["Ticker"].head(25).tolist()

        selected_ticker = st.selectbox(
            "Inspect a top ticker",
            top_tickers,
            index=0
        )

        st.subheader(f"{selected_ticker} Price Chart")
        st.plotly_chart(
            make_price_chart(
                data_by_ticker[selected_ticker],
                trades_by_ticker[selected_ticker],
                title=f"{selected_ticker} Price Chart with Buy/Sell Signals and Volume"
            ),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

        st.subheader(f"{selected_ticker} Equity Curve")
        st.plotly_chart(
            make_equity_chart(
                equity_by_ticker[selected_ticker],
                title=f"{selected_ticker} Equity Curve"
            ),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

        st.subheader(f"{selected_ticker} Trades")
        display_trades_table(trades_by_ticker[selected_ticker])

        if errors:
            with st.expander("Tickers with errors"):
                st.dataframe(pd.DataFrame(errors), use_container_width=True)

    else:
        st.info("Choose your scanner universe and settings on the left, then click Run Market Scanner.")


# Page 3: Performance Tracker
if page == "Performance Tracker":
    display_performance_tracker_page()
