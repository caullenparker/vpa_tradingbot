# ibkr_data_test.py
# Safe test for IBKR historical data provider.
# No orders are placed.

from ibkr_data_provider import get_ibkr_data


ticker = "SPY"

print(f"Requesting IBKR historical data for {ticker}...")

df = get_ibkr_data(
    ticker=ticker,
    period="6mo",
    interval="1d"
)

print("\nData received!")
print(f"Rows: {len(df)}")
print("\nLast 10 rows:")
print(df.tail(10))
