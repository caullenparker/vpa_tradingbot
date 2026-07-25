from ib_insync import *

ib = IB()

print("Connecting...")
ib.connect("127.0.0.1", 7497, clientId=1)

print("\nConnected!")

print("\nAccounts:")
print(ib.managedAccounts())

print("\nAccount Summary:")

for item in ib.accountSummary():
    if item.tag in [
        "NetLiquidation",
        "BuyingPower",
        "CashBalance",
        "AvailableFunds"
    ]:
        print(f"{item.tag}: {item.value}")

ib.disconnect()