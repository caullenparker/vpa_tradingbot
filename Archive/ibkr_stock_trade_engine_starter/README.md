# IBKR Stock Trade Engine Starter

This is the first VPA TradingBot execution engine.

It is long-only shares, paper-trading first.

## Files

```text
ibkr_trade_engine.py
ibkr_trade_engine_test.py
ibkr_positions_test.py
```

## Requirements

TWS Paper Trading must be open and logged in.

API settings:

```text
Enable ActiveX and Socket Clients = checked
Read-Only API = unchecked
Socket port = 7497
Allow connections from localhost only = checked
```

## Install

```powershell
pip install ib-insync
```

## Test current positions

```powershell
python ibkr_positions_test.py
```

## Test a $1,000 paper buy

```powershell
python ibkr_trade_engine_test.py
```

This will:
1. Connect to TWS paper.
2. Pull market price or recent historical close.
3. Calculate shares for about $1,000.
4. Submit a market BUY order.
5. Skip the order if you already own the ticker.

## Next step

Wire this into the VPA scanner:

```python
if latest_buy_signal:
    buy_stock_dollars(ticker, dollars_per_trade=1000)
```
