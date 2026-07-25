# IBKR Data Provider Starter

This gives VPA TradingBot a local IBKR historical data source.

## Requirements

TWS Paper Trading must be open and logged in.

Your TWS API settings should have:

```text
Enable ActiveX and Socket Clients = checked
Read-Only API = unchecked
Socket port = 7497
Allow connections from localhost only = checked
```

## Install

```powershell
pip install ib-insync pandas
```

## Files

```text
ibkr_data_provider.py
ibkr_data_test.py
```

## Run test

```powershell
python ibkr_data_test.py
```

Expected output:

```text
Rows: ...
open high low close volume
...
```

## Next integration step

In the dashboard file, replace the current `get_data()` yfinance function with a wrapper that calls:

```python
from ibkr_data_provider import get_ibkr_data

df = get_ibkr_data(ticker, period, interval)
```

Important: this IBKR provider works locally while TWS is open. It will not work directly on Render unless TWS/IB Gateway is running somewhere accessible to the Render app.
