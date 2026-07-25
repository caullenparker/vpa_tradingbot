# ibkr_trade_engine_test.py
# Safe paper-trading test.
# Buys approximately $1,000 of SPY in your IBKR paper account.
# Educational only. Not financial advice.

from ibkr_trade_engine import buy_stock_dollars


result = buy_stock_dollars(
    ticker="SPY",
    dollars_per_trade=1000
)

print("\nTrade Result:")
for key, value in result.items():
    print(f"{key}: {value}")
