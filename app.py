
import streamlit as st
import yfinance as yf
import pandas as pd

# --------------------------------------------------
# APP TITLE AND DESCRIPTION
# --------------------------------------------------

st.title("Stock Comparison Dashboard")

st.write(
    "Welcome to the Stock Comparison Dashboard! "
    "This app allows users to compare different stocks, "
    "view historical performance, and see how much an "
    "investment would have grown over time."
)

# --------------------------------------------------
# USER INPUTS
# --------------------------------------------------

st.header("Choose Your Investments")

stocks = {
    "AMD": "AMD",
    "NVIDIA": "NVDA",
    "Apple": "AAPL",
    "Microsoft": "MSFT"
}

stock1 = st.selectbox(
    "Select your first stock:",
    list(stocks.keys())
)

stock2 = st.selectbox(
    "Select your second stock:",
    [name for name in stocks if name != stock1]
)

period = st.selectbox(
    "Select the time period:",
    ["1mo", "6mo", "1y", "3y", "5y"],
    index=3
)

investment = st.number_input(
    "Enter your starting investment amount ($):",
    min_value=100.0,
    value=1000.0,
    step=100.0
)

# --------------------------------------------------
# DOWNLOAD HISTORICAL STOCK DATA
# --------------------------------------------------

@st.cache_data(ttl=3600)
def get_stock_data(ticker, selected_period):
    data = yf.Ticker(ticker).history(
        period=selected_period,
        auto_adjust=True
    )
    return data["Close"]

st.header("Stock Performance Comparison")

try:
    with st.spinner("Downloading stock prices..."):
        prices1 = get_stock_data(
            stocks[stock1], period
        )

        prices2 = get_stock_data(
            stocks[stock2], period
        )

    # Combine both stocks into one table
    prices = pd.concat(
        [prices1.rename(stock1),
         prices2.rename(stock2)],
        axis=1
    ).dropna()

    if len(prices) < 2:
        st.error(
            "Not enough stock data is available. "
            "Please select another time period."
        )
        st.stop()

    # --------------------------------------------------
    # CALCULATE INVESTMENT GROWTH
    # --------------------------------------------------

    growth = prices / prices.iloc[0] * investment

    final_value1 = growth[stock1].iloc[-1]
    final_value2 = growth[stock2].iloc[-1]

    return1 = (
        (final_value1 / investment) - 1
    ) * 100

    return2 = (
        (final_value2 / investment) - 1
    ) * 100

    # --------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------

    st.subheader("Investment Growth Chart")

    st.write(
        "The chart below shows how your starting "
        "investment would have changed over the "
        "selected time period."
    )

    st.line_chart(growth)

    st.subheader("Investment Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label=f"{stock1} Investment Value",
            value=f"${final_value1:,.2f}",
            delta=f"{return1:.2f}%"
        )

    with col2:
        st.metric(
            label=f"{stock2} Investment Value",
            value=f"${final_value2:,.2f}",
            delta=f"{return2:.2f}%"
        )

    # --------------------------------------------------
    # COMPARISON TABLE
    # --------------------------------------------------

    st.subheader("Stock Comparison Table")

    comparison = pd.DataFrame({
        "Stock": [stock1, stock2],
        "Starting Investment": [
            investment, investment
        ],
        "Final Value": [
            final_value1, final_value2
        ],
        "Total Return (%)": [
            return1, return2
        ]
    })

    st.dataframe(
        comparison.round(2),
        hide_index=True
    )

    # --------------------------------------------------
    # DYNAMIC INVESTMENT SUMMARY
    # --------------------------------------------------

    st.subheader("Investment Summary")

    if return1 > return2:
        winner = stock1
        better_return = return1
    elif return2 > return1:
        winner = stock2
        better_return = return2
    else:
        winner = None

    if winner is None:
        st.success(
            f"{stock1} and {stock2} had equal "
            "percentage returns over this period."
        )
    else:
        st.success(
            f"Based on historical performance, "
            f"{winner} had the higher return of "
            f"{better_return:.2f}% over the "
            f"selected time period."
        )

    st.write(
        "This comparison is based on historical "
        "stock prices. Past performance does not "
        "guarantee future investment results."
    )

except Exception as error:
    st.error(
        "Unable to download stock data. "
        "Please check your internet connection "
        "and try again."
    )
    st.caption(f"Technical details: {error}")
