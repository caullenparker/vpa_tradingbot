from ib_insync import *

ib = IB()

print("Connecting...")
ib.connect("127.0.0.1", 7497, clientId=3)

contract = Stock("SPY", "SMART", "USD")
ib.qualifyContracts(contract)

bars = ib.reqHistoricalData(
    contract,
    endDateTime="",
    durationStr="1 M",
    barSizeSetting="1 day",
    whatToShow="TRADES",
    useRTH=True,
    formatDate=1
)

print(f"Bars received: {len(bars)}")

for bar in bars[-5:]:
    print(bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume)

ib.disconnect()