import api
import datetime
import math

def truncate_float(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)  # handle scientific notation
    i, p, d = s.partition('.')
    return float('.'.join([i, (d+'0'*n)[:n]]))

def get_crypto_combinations(api_response, base):
    market_symbols = [item['symbol'] for item in api_response]
    combinations = []

    for sym1 in api_response:

        sym1_token1 = sym1['baseCoin']
        sym1_token2 = sym1['quoteCoin']

        if (sym1_token2 == base):
            for sym2 in api_response:

                sym2_token1 = sym2['baseCoin']
                sym2_token2 = sym2['quoteCoin']

                if (sym1_token1 == sym2_token2):
                    for sym3 in api_response:

                        sym3_token1 = sym3['baseCoin']
                        sym3_token2 = sym3['quoteCoin']

                        if ((sym2_token1 == sym3_token1) and (sym3_token2 == sym1_token2)):
                            combination = {
                                'base': sym1_token2,
                                'intermediate': sym1_token1,
                                'ticker': sym2_token1,
                            }
                            combinations.append(combination)

    return combinations

def fetch_current_ticker_price(symbol, symbol_price_dict, op):
    symbol = symbol_price_dict.get(symbol)
    if(op == "Sell"):
        return symbol.get("bid1Price", None)
    elif(op == "Buy"):
        return symbol.get("ask1Price", None)

def check_bidAsk_size(symbol, symbol_price_dict, amount, op):
    #the amount always needs to be referent to the base, like want to buy 100 of BTCUSDT, 100 needs to refer to BTC.
    symbol = symbol_price_dict.get(symbol)
    if (op == "Sell"):
        if(symbol.get("bid1Size") > amount):
            return True
        else:
            print("Sell", symbol.get("bid1Size"), amount)
            return False
    elif (op == "Buy"):
        if(symbol.get("ask1Size") > amount):
            return True
        else:
            print("Buy", symbol.get("ask1Size"), amount)
            return False

def check_if_float_zero(value):
    return math.isclose(value, 0.0, abs_tol=1e-3)

def calculate_buy(current_price, investment_amount):
    if not check_if_float_zero(current_price):
        return investment_amount / current_price
    else:
        return 0

def check_buy_buy_sell(scrip1, scrip2, scrip3, initial_investment, symbol_price_dict, exchange_fee_rate, LIQUIDITY_PROTECTION):
    exchange_fee_rate = exchange_fee_rate/100  # convert porcentage to decimal

    # first trade BUY
    current_price1 = fetch_current_ticker_price(scrip1, symbol_price_dict, "Buy")
    if current_price1 is None:
        return 0, {}

    if("USDC" in scrip1 or scrip1 == "USDTEUR"):
        #there is no brokrage in Bybit
        effective_investment1 = initial_investment
    else:
        effective_investment1 = initial_investment * (1 - exchange_fee_rate)

    buy_quantity1 = effective_investment1 / current_price1

    if(LIQUIDITY_PROTECTION == True):
        bidAsk_size1 = check_bidAsk_size(scrip1, symbol_price_dict, buy_quantity1, "Buy")
        if bidAsk_size1 is False:
            print("There is no sufficient liquidity for ", scrip1)
            return 0, {}


    # second trade BUY
    current_price2 = fetch_current_ticker_price(scrip2, symbol_price_dict, "Buy")
    if current_price2 is None:
        return 0, {}

    if ("USDC" in scrip2 or scrip2 == "USDTEUR"):
        # there is no brokrage in Bybit
        effective_investment2 = buy_quantity1
    else:
        effective_investment2 = buy_quantity1 * (1 - exchange_fee_rate)

    buy_quantity2 = effective_investment2 / current_price2

    if (LIQUIDITY_PROTECTION == True):
        bidAsk_size2 = check_bidAsk_size(scrip2, symbol_price_dict, buy_quantity2, "Buy")
        if bidAsk_size2 is False:
            print("There is no sufficient liquidity for ", scrip2)
            return 0, {}

    # third trade SELL
    current_price3 = fetch_current_ticker_price(scrip3, symbol_price_dict, "Sell")
    if current_price3 is None:
        return 0, {}

    if ("USDC" in scrip3 or scrip3 == "USDTEUR"):
        # there is no brokrage in Bybit
        effective_investment3 = buy_quantity2
    else:
        effective_investment3 = buy_quantity2 * (1 - exchange_fee_rate)

    final_amount = effective_investment3 * current_price3

    if (LIQUIDITY_PROTECTION == True):
        bidAsk_size3 = check_bidAsk_size(scrip3, symbol_price_dict, buy_quantity2, "Sell")
        if bidAsk_size3 is False:
            print("There is no sufficient liquidity for ", scrip3)
            return 0, {}


    scrip_prices = {
        scrip1: current_price1,
        scrip2: current_price2,
        scrip3: current_price3
    }

    return final_amount, scrip_prices


def symbol_price_dict(tickers):
    symbol_price_dict = {}
    for ticker in tickers:
        fail = False
        for item in ticker:
            if(ticker.get(item) is None or ticker.get(item) == 0 or ticker.get(item) == ''):
                fail = True
        if fail:
            continue
        else:
            symbol_price_dict[ticker.get('symbol')] = {
                'bid1Price': float(ticker.get('bid1Price')),  # Convert to float, provide default as 0
                'bid1Size': float(ticker.get('bid1Size')),
                'ask1Price': float(ticker.get('ask1Price')),
                'ask1Size': float(ticker.get('ask1Size')),
                'lastPrice': float(ticker.get('lastPrice'))
            }
    return symbol_price_dict
def check_profit_loss(total_price_after_sell, initial_investment, min_profit):
    min_profitable_price = initial_investment + min_profit
    profit_loss = total_price_after_sell - min_profitable_price
    return profit_loss

def perform_triangular_arbitrage(scrip1, scrip2, scrip3, initial_investment, transaction_brokerage, min_profit, symbol_price_dict, LIQUIDITY_PROTECTION):

    final_amount, scrip_prices = check_buy_buy_sell(scrip1['symbol'], scrip2['symbol'], scrip3['symbol'], initial_investment, symbol_price_dict, transaction_brokerage, LIQUIDITY_PROTECTION)

    if final_amount > 1:
        profit_loss = check_profit_loss(final_amount, initial_investment, min_profit)

        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        return {
            "time": current_time,
            "type": "BUY/BUY/SELL",
            "scrip1":scrip1,
            "scrip2": scrip2,
            "scrip3": scrip3,
            "initial_investment": initial_investment,
            "scrip_prices": scrip_prices,
            "sequence": f"{scrip1},{scrip2},{scrip3}",
            "profit_loss": truncate_float(profit_loss, 2)
        }

#trade functions
def place_trade_orders(type, scrip1, scrip2, scrip3, initial_amount, scrip_prices):
    if type == 'BUY_BUY_SELL':

        quantities = {}
        quantities[scrip1['symbol']] = initial_amount
        quantities[scrip2['symbol']] = initial_amount / scrip_prices[scrip1['symbol']]
        quantities[scrip3['symbol']] = quantities[scrip1['symbol']] / scrip_prices[scrip2['symbol']]
        response = []

        response.append(api.place_buy_oder_api(scrip1['symbol'], initial_amount, 'Buy'))
        intermediate_qty = api.get_coin_balance(scrip1['base'])
        print(intermediate_qty)

        response.append(api.place_buy_oder_api(scrip2['symbol'], intermediate_qty, 'Buy'))
        ticker_qty = api.get_coin_balance(scrip2['base'])

        response.append(api.place_buy_oder_3_api(scrip3['symbol'], ticker_qty, 'Sell'))
        final_qty = api.get_coin_balance(scrip3['quote'])

        return final_qty
        #response.append(api.place_batch_order(scrip1, scrip2, scrip3, quantities, scrip_prices))
    """
    elif type == 'BUY_SELL_SELL':
        s1_quantity = initial_amount / scrip_prices[scrip1]
        place_buy_order(scrip1, s1_quantity, scrip_prices[scrip1])

        s2_quantity = s1_quantity
        place_sell_order(scrip2, s2_quantity, scrip_prices[scrip2])

        s3_quantity = s2_quantity * scrip_prices[scrip2]
        place_sell_order(scrip3, s3_quantity, scrip_prices[scrip3])
    """
