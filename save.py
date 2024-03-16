import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime


def get_price(symbol, interval, limit):
    kline_url = "https://api.binance.us/api/v3/klines"
    closed_prices = []
    params = {
        'symbol': f'{symbol}USDT',
        'interval': f'{interval}',
        'limit': {limit}
    }
    response = requests.get(kline_url, params=params)
    # print("Fetching data for", symbol, "...")
    if response.status_code == 200:
        data = response.json()
        for entry in data:
            closed_prices.append(float(entry[4]))
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    return closed_prices


def update_100(days, allocation):
    update_portfolio(days, allocation, "portfolio_values_100.csv")


def update_200(days, allocation):
    update_portfolio(days, allocation, "portfolio_values_200.csv")


def update_portfolio(days, allocation, filename):
    # Test if weights are applied correctly
    weight_sum = sum(allocation.values())
    if weight_sum != 1:
        st.sidebar.error("Allocation weights must sum to 1. Please adjust the values.")
        return

    # Get historical prices for each cryptocurrency
    historical_prices = {}
    for symbol in allocation.keys():
        prices = get_price(symbol, '1d', days)
        historical_prices[symbol] = prices

    # Adjust for weight in portfolio
    for symbol, prices in historical_prices.items():
        for i in range(0, days):
            prices[i] *= allocation[symbol]

    # Calculate the portfolio value for each day
    portfolio_values = []
    for i in range(days):
        daily_portfolio_value = sum(historical_prices[symbol][i] for symbol in allocation)
        portfolio_values.append(daily_portfolio_value)

    df = pd.DataFrame(portfolio_values)

    # Define the dates (last 7 days)
    today = pd.Timestamp.now().floor('D')
    dates = [today - pd.DateOffset(days=i) for i in range(days)]
    # format dates
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    df["Date"] = dates[::-1]
    df.set_index("Date", inplace=True)

    results_df = pd.DataFrame({
        "Date": df.index,
        "Portfolio_Value": portfolio_values,
    })

    # Save the results to a csv file
    results_df.to_csv(filename, index=False)


# Adding a sidebar
st.sidebar.title('Allocation')

# Define initial allocation
initial_allocation = {
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

# Input fields for allocation
allocation = {}
for crypto, weight in initial_allocation.items():
    allocation[crypto] = st.sidebar.number_input(f"Allocation for {crypto}", min_value=0.0, max_value=1.0, value=weight, step=0.01)

# Validate allocation sum
if sum(allocation.values()) != 1:
    st.sidebar.error("Allocation weights must sum to 1. Please adjust the values.")
    st.stop()

# Save the updated allocation to a csv file
allocation_df = pd.DataFrame(allocation.items(), columns=["Crypto", "Allocation"])
allocation_df.to_csv("allocation.csv", index=False)

# Pie chart for allocations
st.markdown("## Allocations")
fig, ax = plt.subplots(figsize=(4, 4))
fig.patch.set_facecolor((38 / 255, 39 / 255, 48 / 255))  # Set background color
wedges, texts = ax.pie(allocation.values(), startangle=90)
ax.axis('equal')
alloc_txt = [f"{crypto}: {allocation:.0%}" for crypto, allocation in allocation.items()]
ax.legend(wedges, alloc_txt,
          title="Allocations",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1),
          fontsize='small')

# Plotting initial Line Chart
results_df = pd.read_csv("portfolio_values.csv")
line_chart = st.line_chart(results_df.set_index("Date"), use_container_width=True)

# Input field for number of days
days_input = st.sidebar.number_input("Number of Days (max 500)", min_value=1, max_value=500, value=100)

# Dropdown for updating the chart
update_option = st.sidebar.selectbox("Update Chart for:", ["Last 100 Days", "Last 200 Days"])

if update_option == "Last 100 Days":
    if st.sidebar.button("Update Chart (Last 100 Days)"):
        update_100(days_input, allocation)
        st.rerun()

elif update_option == "Last 200 Days":
    if st.sidebar.button("Update Chart (Last 200 Days)"):
        update_200(days_input, allocation)
        st.rerun()

