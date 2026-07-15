import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="AI Multi-Stock Watchlist Scanner", layout="wide")

# Title and Description
st.title("📊 Custom AI Stock Watchlist Scanner")
st.markdown("Scan your favorite tickers simultaneously for active triggers or ongoing trends with volatility-adjusted stops and targets.")

# 1. SIDEBAR INPUTS
st.sidebar.header("Configuration")
default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL"
watchlist_input = st.sidebar.text_area("Edit Watchlist (comma-separated):", default_watchlist)

# Parse list
tickers = [t.strip().upper() for t in watchlist_input.split(",") if t.strip()]

# Parameters
atr_period = st.sidebar.slider("ATR Period (Volatility)", 5, 30, 14)
risk_multiplier = st.sidebar.slider("ATR Risk Multiplier", 1.0, 3.0, 1.5, step=0.1)

# 2. SIGNAL LOGIC FUNCTION WITH MULTI-LEVEL "HOLD" DIAGNOSTICS
def scan_ticker(ticker_symbol):
    try:
        # Fetch 60 days of data
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="60d")
        
        if df.empty or len(df) < 25:
            return None
        
        # Calculate Indicators
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(atr_period).mean()
        
        # Grab last 2 rows to evaluate crossovers
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = latest['Close']
        atr = latest['ATR']
        
        # Crossover logic
        bullish_cross = (prev['EMA_9'] <= prev['EMA_21']) and (latest['EMA_9'] > latest['EMA_21'])
        bearish_cross = (prev['EMA_9'] >= prev['EMA_21']) and (latest['EMA_9'] < latest['EMA_21'])
        
        signal = "⚪ HOLD (Neutral/Cash)"
        stop_loss = 0.0
        target_1 = 0.0
        target_2 = 0.0
        
        # Determine Signal State
        if bullish_cross and latest['RSI'] > 40:
            signal = "🟢 BUY TRIGGER"
            stop_loss = price - (risk_multiplier * atr)
            target_1 = price + (risk_multiplier * atr)
            target_2 = price + (2 * risk_multiplier * atr)
            
        elif bearish_cross or (latest['RSI'] > 70 and latest['EMA_9'] < latest['EMA_21']):
            signal = "🔴 SELL TRIGGER"
            stop_loss = price + (risk_multiplier * atr)
            target_1 = price - (risk_multiplier * atr)
            target_2 = price - (2 * risk_multiplier * atr)
            
        elif latest['EMA_9'] > latest['EMA_21']:
            signal = "🟡 HOLD (Bullish Trend)"
            stop_loss = price - (risk_multiplier * atr)
            target_1 = price + (risk_multiplier * atr)
            target_2 = price + (2 * risk_multiplier * atr)
            
        else:
            signal = "⚪ HOLD (Bearish/Cash)"
            stop_loss = price + (risk_multiplier * atr)
            target_1 = price - (risk_multiplier * atr)
            target_2 = price - (2 * risk_multiplier * atr)
            
        return {
            "Ticker": ticker_symbol,
            "Price": round(price, 2),
            "Signal": signal,
            "Stop Loss": round(stop_loss, 2) if stop_loss > 0 else "-",
            "Target 1 (1:1 R:R)": round(target_1, 2) if target_1 > 0 else "-",
            "Target 2 (1:2 R:R)": round(target_2, 2) if target_2 > 0 else "-",
            "RSI (14)": round(latest['RSI'], 1),
            "ATR": round(atr, 2)
        }
    except Exception as e:
        return None

# 3. RUN SCANNER INTERFACE
if st.button("🔍 Run Scanner Now", type="primary"):
    with st.spinner(f"Scanning {len(tickers)} tickers..."):
        results = []
        for ticker in tickers:
            data = scan_ticker(ticker)
            if data:
                results.append(data)
                
        if results:
            scan_df = pd.DataFrame(results)
            
            # Display overall stats
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Scanned", len(scan_df))
            col2.metric("🟢 Active Buy Triggers", len(scan_df[scan_df['Signal'] == "🟢 BUY TRIGGER"]))
            col3.metric("🟡 Bullish Holds", len(scan_df[scan_df['Signal'] == "🟡 HOLD (Bullish Trend)"]))
            col4.metric("🔴 Active Sell Triggers", len(scan_df[scan_df['Signal'] == "🔴 SELL TRIGGER"]))
            
            st.write("---")
            
            # Interactive Dataframe
            st.subheader("Scanner Dashboard")
            st.dataframe(
                scan_df, 
                use_container_width=True,
                column_config={
                    "Signal": st.column_config.TextColumn("Signal Rating"),
                    "Price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                    "Stop Loss": st.column_config.TextColumn("Dynamic Stop Loss"),
                    "Target 1 (1:1 R:R)": st.column_config.TextColumn("Profit Target 1"),
                    "Target 2 (1:2 R:R)": st.column_config.TextColumn("Profit Target 2")
                }
            )
        else:
            st.error("No valid data retrieved. Please check your watchlist ticker symbols.")
