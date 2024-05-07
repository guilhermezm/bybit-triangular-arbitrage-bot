import functions
from pybit.unified_trading import HTTP
session = HTTP(
    testnet=False,
    api_key="",
    api_secret="",
)

def get_coin_balance(coin):
    response = session.get_coin_balance(
        accountType="UNIFIED",
        coin=coin
    )
    return float(response['result']['balance']['walletBalance'])

def place_buy_oder_api(symbol, qty, syde):
    qty = functions.truncate_float(qty, 2)
    response = session.place_order(
        category="spot",
        symbol=symbol,
        side=syde,
        orderType="Market",
        timeInForce="FOK",
        marketUnit="quoteCoin",
        qty=qty
    )
    print(response)
    return response

def place_buy_oder_3_api(symbol, qty, syde):
    qty = functions.truncate_float(qty, 2)
    response = session.place_order(
        category="spot",
        symbol=symbol,
        side=syde,
        orderType="Market",
        timeInForce="FOK",
        marketUnit="baseCoin",
        qty=qty
    )
    print(response)
    return response

def place_batch_order(scrip1, scrip2, scrip3, qty, scrip_prices):
    session.place_batch_order(
    category="spot",
    request=[
        {
            "symbol": scrip1,
            "side": "Buy",
            "orderType": "Limit",
            "isLeverage": 0,
            "qty": qty[scrip1],
            "price": scrip_prices[scrip1],
            "timeInForce": "FOK",
            "marketUnit": "quoteCoin",
            "orderLinkId": "arbitrage"
        },
        {
            "symbol": scrip2,
            "side": "Sell",
            "orderType": "Limit",
            "isLeverage": 0,
            "qty": qty[scrip2],
            "price": scrip_prices[scrip2],
            "timeInForce": "FOK",
            "marketUnit": "quoteCoin",
            "orderLinkId": "arbitrage"
        },
        {
            "symbol": scrip3,
            "side": "Sell",
            "orderType": "Limit",
            "isLeverage": 0,
            "qty": qty[scrip3],
            "price": scrip_prices[scrip3],
            "timeInForce": "FOK",
            "marketUnit" : "baseCoin",
            "orderLinkId": "arbitrage"
        }
    ]
    )

def get_tickers():
    return session.get_tickers(category="spot")

def get_symbols():
    return session.get_instruments_info(category="spot")
