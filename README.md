# Bybit Triangular Arbitrage Bot

This Python-based bot leverages the Bybit SDK to identify and execute triangular arbitrage opportunities in real-time. It's designed to interact with the cryptocurrency market, specifically through the Bybit exchange, to capture profitable trades arising from price discrepancies between three different currency pairs (triangular arbitrage).

## Disclaimer
This bot only loses money due to other high-frequency traders on the market absolving your order before it gets completely filled. Run it at your own risk. Consider yourself advised that YOU WILL LOSE MONEY as how the bot is.

## How It Works

API Calls: The bot begins its operation by making two critical API calls:
Tickers: Retrieves market data, including prices and sizes for different trading pairs.
Symbols: Fetches available trading symbols, crucial for identifying valid triangular arbitrage paths.

## Core Functions

### `symbol_price_dict(tickers)`
- **Purpose**: Constructs a dictionary from the tickers' data, extracting and converting relevant market data like `bid1Price`, `ask1Price`, `bid1Size`, `ask1Size`, and `lastPrice` for each trading pair into floats. This function ensures that all necessary data is prepared for arbitrage calculations.
- **Parameters**:
  - `tickers`: A list of ticker information fetched from the API.
- **Returns**: A dictionary keyed by the symbol of each trading pair containing its market data.

### `get_crypto_combinations(api_response, base)`
- **Purpose**: Generates all possible triangular combinations of currencies that can be used for arbitrage based on the fetched symbols. It ensures that each combination has a logical trading loop that can return to the original currency.
- **Parameters**:
  - `api_response`: The list of all trading pairs obtained from the API.
  - `base`: The base currency to evaluate for potential arbitrage opportunities.
- **Returns**: A list of dictionaries, each representing a valid triangular arbitrage path.

### `run_arbitrage(...)`
- **Purpose**: Evaluates each triangular combination for profitability based on current market prices, transaction fees, and the specified investment amount. It calculates potential returns and decides whether to execute the trades.
- **Parameters**: Investment details, market data, flags for production and liquidity protection, etc.
- **Returns**: If profitable, executes trades and returns the profit amount; otherwise, it returns `None`.

### Trade Execution Functions
- **`place_trade_orders(...)`**: Handles the execution of trade orders based on the calculated arbitrage path and market conditions.
- **`place_buy_oder_api(...)` and `place_buy_oder_3_api(...)`**: Specific API wrappers to place buy and sell orders, respectively.

## Account and Order Management Functions

- **`get_coin_balance(coin)`**
Purpose: Retrieves the current balance of a specified coin from the user's account, critical for determining available funds before placing trades.
Parameters:
coin: The cryptocurrency for which the balance is required.
Returns: The balance of the specified coin.

- **`place_buy_oder_api(symbol, qty, side)`** and **`place_buy_oder_3_api(symbol, qty, side)`**
Purpose: Places market orders with the specified quantity and side (buy or sell). These functions are specialized for different market unit specifications (quoteCoin or baseCoin).
Parameters:
symbol: The trading symbol for the order.
qty: The quantity of the order.
side: Specifies whether the order is a buy or a sell.
Returns: Response from the API after placing the order.

- **`place_batch_order(scrip1, scrip2, scrip3, qty, scrip_prices)`**
Purpose: Places a batch of orders simultaneously, useful for executing multiple steps of an arbitrage strategy in quick succession.
Parameters:
scrip1, scrip2, scrip3: The trading symbols for the batch orders.
qty: A dictionary specifying quantities for each order.
scrip_prices: Prices at which to place each order.
Returns: Batch order response from the API.

## Arbitrage Logic

Data Fetching: The bot starts by fetching current market data (tickers) and trading symbols (symbols).
Data Processing:
Uses symbol_price_dict to organize price and size data.
Uses get_crypto_combinations to form all possible arbitrage paths.
Arbitrage Evaluation:
For each potential path, run_arbitrage evaluates the profitability considering current market prices, expected transaction fees, and liquidity.
If a profitable opportunity is found and production mode is on, it executes the trades immediately and logs the profit.
Loop and Delay: Continuously loops through the logic, with a delay between iterations to comply with API rate limits and avoid throttling. 

1. **Data Fetching**: The bot starts by fetching current market data (`tickers`) and trading symbols (`symbols`).
2. **Data Processing**:
   - Uses `symbol_price_dict` to organize price and size data.
   - Uses `get_crypto_combinations` to form all possible arbitrage paths.
3. **Arbitrage Evaluation**:
   - For each potential path, `run_arbitrage` evaluates the profitability considering current market prices, expected transaction fees, and liquidity.
   - If a profitable opportunity is found and production mode is on, it executes the trades immediately and logs the profit.
4. **Loop and Delay**: Continuously loops through the logic, with a delay between iterations to comply with API rate limits and avoid throttling.

## Deployment and Operation

The bot is designed to run continuously, monitoring the market for arbitrage opportunities. It requires a stable server environment with a constant internet connection. Proper API keys and access permissions must be set up in the Bybit account for the bot to execute trades.
Set the variables found in request.py, like: 
- PRODUCTION = True/False - Execute the orders or just look for opportunities.
- LIQUIDITY_PROTECTION = True/False - Explained ahead.
- INVESTMENT_AMOUNT_BASE_CURRENCY = - QTY of the base currency(s) to use in the trade.
- MIN_PROFIT_DOLLARS = 0.05 - Used to avoid slippage in order execution. 
- BROKERAGE_PER_TRANSACTION_PERCENT = 0.1 - Fee bybit charges per most of the transactions.
- base_currencies = ["USDT"] - Can be more than one, make sure you have the available qty of each base coin used as the qty set in INVESTMENT_AMOUNT_BASE_CURRENCY.

### Safety Features
- **Realistic Evaluation**: It uses ask price as the price to buy and bid price as the price to sell in order to calculate the profitability since they are more accurate values than the current market price.
- **Liquidity Checks**: Ensures that the initial investment and the following trades' amounts will be absorved by the market on the bid and ask prices calculated, ensuring that the order will be filled by only one buyer or seller, so being executed at only one price.
-  **Executing orders on best price**: By using the market price to execute the order, we ensure that the order will be filled completely with the best price in the market, to avoid a trade getting stuck for the market not absorving the order on the limit price set.
-  **Dynamic qty**: After each order, we request the balance of the purchased coin to ensure that the next order won't have the error of passing the wrong qty amount, since the actual purchased amount varies from the calculated qty since we execute the order at the best market price, thus it is filled with many different price sub-orders, which leads to an unprecise qty compared to the calculated one.
-  **Exchange fee calculated**: The expected final qty from each trade is calculated considering the exchange fees.
-  **Math Library**: most of the important calculations are done with the Math library, ensuring precision. 

### Required libraries
-**time**
-**pandas**
-**datetime**
-**math**
