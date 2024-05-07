import wrap
import api
import time

PRODUCTION = True
LIQUIDITY_PROTECTION = False
INVESTMENT_AMOUNT_BASE_CURRENCY = 5
MIN_PROFIT_DOLLARS = 0.05
BROKERAGE_PER_TRANSACTION_PERCENT = 0.1
base_currencies = ["USDT", "USDC"]  # List of currencies to check for arbitrage

while True:
    time.sleep(2)  # Delay each iteration to avoid rate limit issues
    tickers = api.get_tickers()
    symbols = api.get_symbols()

    if tickers and symbols and tickers["retMsg"] == "OK" and symbols["retMsg"] == "OK":
        tickers = tickers["result"]['list']
        symbols = symbols["result"]['list']

        for base_currency in base_currencies:  # Iterate over each base currency
            response = wrap.run_arbitrage(INVESTMENT_AMOUNT_BASE_CURRENCY, MIN_PROFIT_DOLLARS,BROKERAGE_PER_TRANSACTION_PERCENT, base_currency, tickers, symbols, PRODUCTION, LIQUIDITY_PROTECTION)

            if PRODUCTION:
                if response is not None:
                    print("Profit of: ", (response - INVESTMENT_AMOUNT_BASE_CURRENCY))
                    break  # Exit after finding the first arbitrage opportunity when in production mode
                else:
                    print(f"No arbitrage opportunity found for {base_currency}")
    else:
        print("Failed to fetch tickers or symbols or the response was not OK.")
