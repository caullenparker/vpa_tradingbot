# ibkr_positions_test.py
# Shows current IBKR paper stock positions.

from ibkr_trade_engine import connect_ibkr, get_positions


ib = connect_ibkr(client_id=30)

try:
    positions = get_positions(ib)

    print("\nCurrent Positions:")

    if not positions:
        print("No open positions.")
    else:
        for pos in positions:
            print(pos)

finally:
    ib.disconnect()
