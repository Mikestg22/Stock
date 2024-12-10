
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_stock_data(ticker, start_date, end_date):
    """Fetch historical stock data using yfinance."""
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        return stock_data
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

def calculate_moving_averages(data, short_window=50, long_window=200):
    """Calculate short-term and long-term moving averages."""
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data

def calculate_rsi(data, window=14):
    """Calculate the Relative Strength Index (RSI)."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    """Calculate MACD and Signal Line."""
    data['MACD'] = data['Close'].ewm(span=short_window, adjust=False).mean() - \
                   data['Close'].ewm(span=long_window, adjust=False).mean()
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
    return data

def identify_signals(data):
    """Identify buy/sell signals based on moving averages."""
    data['Signal'] = 0
    data['Signal'][data['Short_MA'] > data['Long_MA']] = 1
    data['Signal'][data['Short_MA'] <= data['Long_MA']] = -1
    return data

# Streamlit App
st.title("Stock Market Investment App")
st.sidebar.header("Input Options")

# User Inputs
ticker = st.sidebar.text_input("Stock Ticker Symbol (e.g., AAPL, TSLA)", "AAPL")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-01-01"))

# Fetch and Process Data
if st.sidebar.button("Analyze"):
    st.write(f"Fetching data for **{ticker}**...")
    stock_data = fetch_stock_data(ticker, start_date, end_date)

    if stock_data is not None and not stock_data.empty:
        # Calculate indicators and signals
        stock_data = calculate_moving_averages(stock_data)
        stock_data = calculate_rsi(stock_data)
        stock_data = calculate_macd(stock_data)
        stock_data = identify_signals(stock_data)

        # Display stock data
        st.subheader(f"Stock Data for {ticker}")
        st.dataframe(stock_data.tail(10))

        # Plot stock price and moving averages
        st.subheader(f"Price Trends for {ticker}")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(stock_data.index, stock_data['Close'], label="Close Price", alpha=0.75)
        ax.plot(stock_data.index, stock_data['Short_MA'], label="50-Day MA", linestyle="--")
        ax.plot(stock_data.index, stock_data['Long_MA'], label="200-Day MA", linestyle="--")
        ax.legend()
        ax.set_title(f"{ticker} Price with Moving Averages")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        st.pyplot(fig)

        # Plot RSI
        st.subheader(f"RSI (Relative Strength Index) for {ticker}")
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.plot(stock_data.index, stock_data['RSI'], label="RSI", color="purple")
        ax.axhline(70, linestyle="--", color="red", label="Overbought (70)")
        ax.axhline(30, linestyle="--", color="green", label="Oversold (30)")
        ax.legend()
        ax.set_title("RSI Trend")
        ax.set_xlabel("Date")
        st.pyplot(fig)

        # Plot MACD
        st.subheader(f"MACD (Moving Average Convergence Divergence) for {ticker}")
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(stock_data.index, stock_data['MACD'], label="MACD", color="blue")
        ax.plot(stock_data.index, stock_data['Signal_Line'], label="Signal Line", color="orange")
        ax.axhline(0, linestyle="--", color="gray", alpha=0.7)
        ax.legend()
        ax.set_title("MACD Trend")
        ax.set_xlabel("Date")
        st.pyplot(fig)

        # Show recommendations
        last_signal = stock_data['Signal'].iloc[-1]
        if last_signal == 1:
            st.success("**Recommendation: BUY** - Short MA is above Long MA.")
        elif last_signal == -1:
            st.error("**Recommendation: SELL** - Short MA is below Long MA.")
        else:
            st.warning("**Recommendation: HOLD** - No clear trend detected.")
    else:
        st.error("No data found for the given ticker or date range.")
