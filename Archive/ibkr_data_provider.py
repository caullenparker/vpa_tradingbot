# ibkr_data_provider.py
# IBKR historical data provider for VPA TradingBot.
# Requires TWS or IB Gateway to be open and logged into Paper Trading.
# Educational only. Not financial advice.

from ib_insync import IB, Stock, util
import pandas as pd


IBKR_HOST = "127.0.0.1"
IBKR_PORT = 7497          # Paper TWS default
IBKR_CLIENT_ID = 10


PERIOD_TO_DURATION = {
    "1mo": "1 M",
    "3mo": "3 M",
    "6mo": "6 M",
    "1y": "1 Y",
    "2y": "2 Y",
    "3y": "3 Y",
    "5y": "5 Y",
    "10y": "10 Y",
}

INTERVAL_TO_BAR_SIZE = {
    "1d": "1 day",
    "1h": "1 hour",
    "30m": "30 mins",
    "15m": "15 mins",
    "5m": "5 mins",
}


def normalize_ibkr_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts IBKR historical bars into the same OHLCV format your VPA scanner expects:
    index = datetime
    columns = open, high, low, close, volume
    """
    if df.empty:
        return df

    df = df.copy()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

    required = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"IBKR data missing required columns: {missing}")

    df = df[required]
    df = df.dropna()

    return df


def get_ibkr_data(
    ticker: str,
    period: str = "3y",
    interval: str = "1d",
    host: str = IBKR_HOST,
    port: int = IBKR_PORT,
    client_id: int = IBKR_CLIENT_ID,
    use_rth: bool = True,
) -> pd.DataFrame:
    """
    Pull historical OHLCV data from IBKR for a stock ticker.

    Example:
        df = get_ibkr_data("SPY", period="1y", interval="1d")
    """

    ticker = ticker.strip().upper()

    duration = PERIOD_TO_DURATION.get(period)
    if duration is None:
        raise ValueError(f"Unsupported period: {period}. Supported: {list(PERIOD_TO_DURATION.keys())}")

    bar_size = INTERVAL_TO_BAR_SIZE.get(interval)
    if bar_size is None:
        raise ValueError(f"Unsupported interval: {interval}. Supported: {list(INTERVAL_TO_BAR_SIZE.keys())}")

    ib = IB()

    try:
        ib.connect(host, port, clientId=client_id)

        contract = Stock(ticker, "SMART", "USD")
        ib.qualifyContracts(contract)

        bars = ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=use_rth,
            formatDate=1,
        )

        if not bars:
            raise ValueError(f"No IBKR historical bars returned for {ticker}")

        df = util.df(bars)
        df = normalize_ibkr_df(df)

        return df

    finally:
        if ib.isConnected():
            ib.disconnect()
