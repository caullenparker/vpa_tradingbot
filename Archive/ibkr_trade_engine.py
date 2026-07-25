# ibkr_trade_engine.py
# IBKR paper-trading stock execution engine for VPA TradingBot.
# Long shares only. Educational only. Not financial advice.

from ib_insync import IB, Stock, MarketOrder, LimitOrder
import math


IBKR_HOST = "127.0.0.1"
IBKR_PORT = 7497
IBKR_CLIENT_ID = 20

DEFAULT_DOLLARS_PER_TRADE = 1000


def connect_ibkr(client_id=IBKR_CLIENT_ID):
    ib = IB()
    ib.connect(IBKR_HOST, IBKR_PORT, clientId=client_id)
    return ib


def get_market_price(ib, ticker):
    """
    Gets a usable market price.
    Tries live/delayed market data first. Falls back to recent historical close.
    """
    contract = Stock(ticker.upper(), "SMART", "USD")
    ib.qualifyContracts(contract)

    market_data = ib.reqMktData(contract, "", False, False)
    ib.sleep(3)

    price = market_data.marketPrice()

    ib.cancelMktData(contract)

    if price is not None and not math.isnan(price) and price > 0:
        return float(price)

    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr="5 D",
        barSizeSetting="1 day",
        whatToShow="TRADES",
        useRTH=True,
        formatDate=1,
    )

    if not bars:
        raise ValueError(f"Could not get market price or historical close for {ticker}")

    return float(bars[-1].close)


def calculate_share_quantity(price, dollars_per_trade=DEFAULT_DOLLARS_PER_TRADE):
    if price <= 0:
        raise ValueError("Price must be greater than zero.")

    qty = int(dollars_per_trade // price)

    if qty < 1:
        qty = 1

    return qty


def get_positions(ib):
    positions = ib.positions()

    clean_positions = []

    for pos in positions:
        clean_positions.append({
            "account": pos.account,
            "ticker": pos.contract.symbol,
            "secType": pos.contract.secType,
            "exchange": pos.contract.exchange,
            "currency": pos.contract.currency,
            "quantity": float(pos.position),
            "avgCost": float(pos.avgCost),
        })

    return clean_positions


def has_open_stock_position(ib, ticker):
    ticker = ticker.upper()

    for pos in get_positions(ib):
        if (
            pos["ticker"].upper() == ticker
            and pos["secType"] == "STK"
            and pos["quantity"] != 0
        ):
            return True

    return False


def build_stock_order(action, qty, order_type="MKT", limit_price=None, outside_rth=False):
    """
    Creates an explicit IBKR stock order.

    order_type:
        "MKT" = market order
        "LMT" = limit order
    """
    action = action.upper()
    order_type = order_type.upper()

    if order_type == "MKT":
        order = MarketOrder(action, qty)

    elif order_type == "LMT":
        if limit_price is None:
            raise ValueError("limit_price is required for limit orders.")

        order = LimitOrder(action, qty, round(float(limit_price), 2))

    else:
        raise ValueError("order_type must be 'MKT' or 'LMT'.")

    # Make settings explicit so IBKR/TWS presets do not surprise us.
    order.tif = "DAY"
    order.outsideRth = outside_rth
    order.transmit = True

    return order


def buy_stock_dollars(
    ticker,
    dollars_per_trade=DEFAULT_DOLLARS_PER_TRADE,
    client_id=IBKR_CLIENT_ID,
    order_type="MKT",
    outside_rth=False,
):
    """
    Buys approximately $1,000 of stock.

    Defaults to a DAY market order during regular trading hours.
    Prevents duplicate long positions in the same ticker.

    For after-hours testing, you can use:
        buy_stock_dollars("SPY", 1000, order_type="LMT", outside_rth=True)
    """
    ticker = ticker.upper()
    ib = connect_ibkr(client_id=client_id)

    try:
        if has_open_stock_position(ib, ticker):
            return {
                "ticker": ticker,
                "action": "SKIP",
                "reason": "Open position already exists",
            }

        price = get_market_price(ib, ticker)
        qty = calculate_share_quantity(price, dollars_per_trade)

        contract = Stock(ticker, "SMART", "USD")
        ib.qualifyContracts(contract)

        order = build_stock_order(
            action="BUY",
            qty=qty,
            order_type=order_type,
            limit_price=price,
            outside_rth=outside_rth,
        )

        trade = ib.placeOrder(contract, order)
        ib.sleep(5)

        return {
            "ticker": ticker,
            "action": "BUY",
            "order_type": order_type.upper(),
            "outside_rth": outside_rth,
            "dollars_per_trade": dollars_per_trade,
            "estimated_price": price,
            "shares": qty,
            "order_status": trade.orderStatus.status,
            "filled": float(trade.orderStatus.filled),
            "remaining": float(trade.orderStatus.remaining),
            "avg_fill_price": float(trade.orderStatus.avgFillPrice or 0),
            "fills": [str(fill) for fill in trade.fills],
        }

    finally:
        if ib.isConnected():
            ib.disconnect()


def sell_stock_all(
    ticker,
    client_id=IBKR_CLIENT_ID + 1,
    order_type="MKT",
    outside_rth=False,
):
    """
    Sells all currently held shares for the ticker.
    """
    ticker = ticker.upper()
    ib = connect_ibkr(client_id=client_id)

    try:
        position_qty = 0

        for pos in get_positions(ib):
            if pos["ticker"].upper() == ticker and pos["secType"] == "STK":
                position_qty = int(pos["quantity"])
                break

        if position_qty <= 0:
            return {
                "ticker": ticker,
                "action": "SKIP",
                "reason": "No long position to sell",
            }

        price = get_market_price(ib, ticker)

        contract = Stock(ticker, "SMART", "USD")
        ib.qualifyContracts(contract)

        order = build_stock_order(
            action="SELL",
            qty=position_qty,
            order_type=order_type,
            limit_price=price,
            outside_rth=outside_rth,
        )

        trade = ib.placeOrder(contract, order)
        ib.sleep(5)

        return {
            "ticker": ticker,
            "action": "SELL",
            "order_type": order_type.upper(),
            "outside_rth": outside_rth,
            "shares": position_qty,
            "estimated_price": price,
            "order_status": trade.orderStatus.status,
            "filled": float(trade.orderStatus.filled),
            "remaining": float(trade.orderStatus.remaining),
            "avg_fill_price": float(trade.orderStatus.avgFillPrice or 0),
            "fills": [str(fill) for fill in trade.fills],
        }

    finally:
        if ib.isConnected():
            ib.disconnect()
