from ib_insync import *

ib = IB()

try:
    print("Connecting to IBKR...")

    ib.connect(
        "127.0.0.1",
        7497,
        clientId=4
    )

    print("Connected!")

    contract = Stock("SPY", "SMART", "USD")
    ib.qualifyContracts(contract)

    order = MarketOrder(
        "BUY",
        1
    )

    print("Submitting paper order...")

    trade = ib.placeOrder(
        contract,
        order
    )

    # Wait for updates
    ib.sleep(5)

    print("\nOrder Status:")
    print(trade.orderStatus.status)

    print("\nFill Information:")

    for fill in trade.fills:
        print(fill)

finally:
    ib.disconnect()

    print("\nDisconnected.")