import time

import pandas as pd
import streamlit as st

from core.strategy import (
    display_trades_table,
    get_nasdaq100_tickers,
    get_sp500_tickers,
    make_equity_chart,
    make_price_chart,
    parse_tickers,
    run_strategy_for_ticker,
)


def render():
    st.title("VPA Market Scanner")
    st.caption(
        "Scans S&P 500 and/or Nasdaq 100 tickers, backtests the VPA strategy, "
        "and ranks results by Total Return %. Educational only. Not financial advice."
    )

    with st.sidebar:
        st.header("Strategy Inputs")
        universe_choice = st.selectbox(
            "Scanner Universe", ["S&P 500", "Nasdaq 100", "Both", "Custom List"], index=0
        )

        custom_tickers = ""
        if universe_choice == "Custom List":
            custom_tickers = st.text_area(
                "Custom Scanner Tickers",
                value="SPY, QQQ, TLT, AAPL, MSFT, NVDA, AMZN, META, GOOGL",
            )

        max_tickers = st.number_input(
            "Max Tickers to Scan", min_value=10, max_value=700, value=100, step=10
        )
        period = st.selectbox("Historical Period", ["6mo", "1y", "2y", "3y", "5y", "10y"], index=0)
        interval = st.selectbox("Interval", ["1d"], index=0)

        st.subheader("VPA Settings")
        vol_window = st.slider("Volume Lookback Window", 5, 100, 20)
        trend_window = st.slider("Trend Window", 5, 200, 20)
        stopping_window = st.slider("Stopping Volume Window", 2, 30, 10)
        high_volume_threshold = st.slider("High Volume Threshold", 1.00, 3.00, 1.05, 0.05)
        low_volume_threshold = st.slider("Low Volume Threshold", 0.20, 1.50, 1.00, 0.05)
        wide_spread_threshold = st.slider("Wide Spread Threshold", 1.00, 3.00, 1.05, 0.05)
        narrow_spread_threshold = st.slider("Narrow Spread Threshold", 0.20, 1.50, 0.95, 0.05)

        st.subheader("Backtest Settings")
        stop_loss = st.slider("Stop Loss %", 1, 50, 4) / 100
        take_profit = st.slider("Take Profit %", 1, 100, 8) / 100

    st.warning(
        "The scanner downloads and backtests many tickers. Start with 50–100 tickers, "
        "then increase the limit."
    )

    if not st.button("Run Market Scanner", type="primary"):
        st.info("Choose your scanner universe and settings on the left, then run the scanner.")
        return

    try:
        if universe_choice == "S&P 500":
            tickers = get_sp500_tickers()
        elif universe_choice == "Nasdaq 100":
            tickers = get_nasdaq100_tickers()
        elif universe_choice == "Both":
            tickers = sorted(set(get_sp500_tickers() + get_nasdaq100_tickers()))
        else:
            tickers = parse_tickers(custom_tickers)
        tickers = tickers[: int(max_tickers)]
    except Exception as exc:
        st.error(f"Could not load ticker universe: {exc}")
        return

    st.write(f"Scanning **{len(tickers)}** tickers from **{universe_choice}**...")

    results, data_by_ticker, trades_by_ticker, equity_by_ticker, errors = [], {}, {}, {}, []
    progress = st.progress(0)
    status = st.empty()
    started = time.time()

    for idx, ticker in enumerate(tickers):
        status.write(f"Scanning {idx + 1} of {len(tickers)}: {ticker}")
        try:
            df, trades, equity, summary = run_strategy_for_ticker(
                ticker=ticker,
                period=period,
                interval=interval,
                initial_cash=10000,
                stop_loss=stop_loss,
                take_profit=take_profit,
                vol_window=vol_window,
                trend_window=trend_window,
                stopping_window=stopping_window,
                high_volume_threshold=high_volume_threshold,
                low_volume_threshold=low_volume_threshold,
                wide_spread_threshold=wide_spread_threshold,
                narrow_spread_threshold=narrow_spread_threshold,
            )
            results.append(summary)
            data_by_ticker[ticker] = df
            trades_by_ticker[ticker] = trades
            equity_by_ticker[ticker] = equity
        except Exception as exc:
            errors.append({"Ticker": ticker, "Error": str(exc)})
        progress.progress((idx + 1) / len(tickers))

    status.empty()

    if not results:
        st.error("No tickers successfully completed.")
        if errors:
            st.dataframe(pd.DataFrame(errors), use_container_width=True)
        return

    results_df = pd.DataFrame(results).sort_values("Total Return %", ascending=False)
    results_df.insert(0, "Rank", range(1, len(results_df) + 1))

    st.success(f"Scanner complete in {time.time() - started:.1f} seconds.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tickers Scanned", len(results_df))
    c2.metric("Best Ticker", results_df.iloc[0]["Ticker"])
    c3.metric("Best Total Return", f"{results_df.iloc[0]['Total Return %']:.2f}%")
    c4.metric("Avg Total Return", f"{results_df['Total Return %'].mean():.2f}%")

    st.subheader("Highest Performing Tickers")
    st.dataframe(
        results_df.style.format(
            {
                "Initial Cash": "${:,.2f}",
                "Final Equity": "${:,.2f}",
                "Total Return %": "{:.2f}%",
                "Win Rate %": "{:.2f}%",
                "Max Drawdown %": "{:.2f}%",
                "Last Close": "${:,.2f}",
            }
        ),
        use_container_width=True,
    )

    st.download_button(
        "Download Scanner Results as CSV",
        results_df.to_csv(index=False).encode("utf-8"),
        "vpa_market_scanner_results.csv",
        "text/csv",
    )

    selected = st.selectbox("Inspect a top ticker", results_df["Ticker"].head(25).tolist())
    st.subheader(f"{selected} Price Chart")
    st.plotly_chart(
        make_price_chart(
            data_by_ticker[selected],
            trades_by_ticker[selected],
            title=f"{selected} Price Chart with Buy/Sell Signals and Volume",
        ),
        use_container_width=True,
        config={"scrollZoom": True, "displayModeBar": True},
    )

    st.subheader(f"{selected} Equity Curve")
    st.plotly_chart(
        make_equity_chart(equity_by_ticker[selected], title=f"{selected} Equity Curve"),
        use_container_width=True,
        config={"scrollZoom": True, "displayModeBar": True},
    )
    st.subheader(f"{selected} Trades")
    display_trades_table(trades_by_ticker[selected])

    if errors:
        with st.expander("Tickers with errors"):
            st.dataframe(pd.DataFrame(errors), use_container_width=True)
