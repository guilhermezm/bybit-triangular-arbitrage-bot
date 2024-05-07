import functions
import pandas as pd

def run_arbitrage(INVESTMENT_AMOUNT_DOLLARS, MIN_PROFIT_DOLLARS, BROKERAGE_PER_TRANSACTION_PERCENT, base_currency, tickers, symbols, PRODUCTION, LIQUIDITY_PROTECTION):

    symbol_price_dict = functions.symbol_price_dict(tickers)

    combinations = functions.get_crypto_combinations(symbols, base_currency)

    print(f'No. of crypto combinations: {len(combinations)}')

    if not PRODUCTION:
        combinations_df = pd.DataFrame(combinations)
        print(combinations_df.head())

    opportunities = []
    for combination in combinations:
        base = combination['base']
        intermediate = combination['intermediate']
        ticker = combination['ticker']

        if base and intermediate and ticker:
            s1 = {'base': intermediate, 'quote': base, 'symbol': f'{intermediate}{base}'}
            s2 = {'base': ticker, 'quote': intermediate, 'symbol': f'{ticker}{intermediate}'}
            s3 = {'base': ticker, 'quote': base, 'symbol': f'{ticker}{base}'}

            result = functions.perform_triangular_arbitrage(s1, s2, s3, INVESTMENT_AMOUNT_DOLLARS, BROKERAGE_PER_TRANSACTION_PERCENT, MIN_PROFIT_DOLLARS, symbol_price_dict, LIQUIDITY_PROTECTION)
            if result and result['profit_loss'] > 0:
                opportunities.append(result)

    if opportunities:
        opportunities.sort(key=lambda x: x['profit_loss'], reverse=True)
        opportunity = opportunities[0]
        print(f"PROFIT-{opportunity['time']}:{opportunity['type']}, {opportunity['sequence']}, {opportunity['scrip_prices']}, Profit: {opportunity['profit_loss']}")
        if PRODUCTION == True:
            return functions.place_trade_orders('BUY_BUY_SELL', opportunity['scrip1'], opportunity['scrip2'], opportunity['scrip3'], opportunity['initial_investment'], opportunity['scrip_prices'])
