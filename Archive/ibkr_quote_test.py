from ib_insync import *

ib = IB()

print("Connecting...")
ib.connect("127.0.0.1", 7497, clientId=2)

symbol = "SPY"

contract = Stock(symbol, "SMART", "USD")
ib.qualifyContracts(contract)

ticker = ib.reqMktData(contract, "", False, False)

ib.sleep(3)

print(f"\nQuote for {symbol}:")
print(f"Bid: {ticker.bid}")
print(f"Ask: {ticker.ask}")
print(f"Last: {ticker.last}")
print(f"Close: {ticker.close}")
print(f"Market Price: {ticker.marketPrice()}")

ib.cancelMktData(contract)
ib.disconnect()