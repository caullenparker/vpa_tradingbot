import re
from io import StringIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots

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

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = read_html_tables_with_headers(url)
    df = tables[0]
    tickers = df["Symbol"].astype(str).str.replace(".", "-", regex=False).str.upper().tolist()
    tickers = [t for t in tickers if t and t != "NAN"]
    return sorted(list(set(tickers)))

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

