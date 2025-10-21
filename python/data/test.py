from returns import expected_returns

tickers = ["AAPL","MSFT","TSLA","NVDA","SPY"]
exp_returns = expected_returns(tickers, period="6mo", price_interval="1d", freq="W")
print(exp_returns)
