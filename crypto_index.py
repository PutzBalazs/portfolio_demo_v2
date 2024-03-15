import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def get_price(symbol, interval, limit):
    kline_url = "https://api.binance.us/api/v3/klines"
    closed_prices = []
    params = {
        'symbol': f'{symbol}USDT',
        'interval': f'{interval}',
        'limit': {limit}
    }
    response = requests.get(kline_url, params=params)
    #print("Fetching data for", symbol, "...")
    if response.status_code == 200:
        data = response.json()
        for entry in data:
            closed_prices.append(float(entry[4]))
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    return closed_prices

allocation = {
    "ETH": 0.14,
    "BNB": 0.09,
    "XRP": 0.13,
    "ADA": 0.12,
    "AVAX": 0.09,
    "DOT": 0.13,
    "LINK": 0.09,
    "MATIC": 0.08,
    "UNI": 0.05,
    "FIL": 0.03,
    "ATOM": 0.03,
    "AAVE": 0.02
}
# Test if weights are applied correctly
weight_sum = sum(allocation.values())
if weight_sum != 1:
    print(f"Allocation weights do not sum to 1. Sum: {weight_sum}")

days = 700
# Get historical prices for each cryptocurrency
historical_prices = {}
for symbol in allocation.keys():
    prices = get_price(symbol, '1d', days)
    historical_prices[symbol] = prices
#print(f"Historiycal prices: {historical_prices}")
 
# Adjust for weight in portfolio
for symbol, prices in historical_prices.items():
    for i in range(0, days):
        prices[i] *= allocation[symbol]

#print(f"Historiycal prices weighted: {historical_prices}")

# Calculate the portfolio value for each day
portfolio_values = []
for i in range(days):
    daily_portfolio_value = sum(historical_prices[symbol][i] for symbol in allocation)
    portfolio_values.append(daily_portfolio_value)

df = pd.DataFrame(portfolio_values)

# Define the dates (last 7 days)
today = pd.Timestamp.now().floor('D')
dates = [today - pd.DateOffset(days=i) for i in range(days)]
#format dates
dates = [date.strftime('%Y-%m-%d') for date in dates]
df["Date"] = dates[::-1]
df.set_index("Date", inplace=True)

results_df = pd.DataFrame({
    "Date": df.index,
    "Portfolio_Value": portfolio_values,
})
#print(f"Portfolio values: {portfolio_values}")

# Adding a sidebar
st.sidebar.title('Allocation')

# Pie chart for allocations
allocation_df = pd.DataFrame(allocation.items(), columns=["Crypto", "Allocation"])

st.markdown("## Allocations")
fig, ax = plt.subplots(figsize=(4, 4))
fig.patch.set_facecolor('black')
wedges, texts = ax.pie(allocation.values(), startangle=90)
ax.axis('equal')
alloc_txt = [f"{crypto}: {allocation:.0%}" for crypto, allocation in allocation.items()]
ax.legend(wedges, alloc_txt,
          title="Allocations",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1),
          fontsize='small')

# Plotting
st.line_chart(results_df.set_index("Date"), use_container_width=True)
st.sidebar.pyplot(fig)