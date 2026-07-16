import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="AI S&P & Index Scanner", layout="wide")

# Title and Description
st.title("📊 Robust S&P Sector & Custom Index Scanner")
st.markdown("Scan your personal watchlist or major S&P industry sectors. Fully stable, zero external scraping dependencies.")

# --- HARDCODED S&P 500 SECTORS ---
# Over 140 of the highest-volume, market-moving stocks categorized by GICS sectors
SP500_SECTOR_MAP = {
    "Technology": ["AAPL", "MSFT", "NVDA", "AVGO", "CSCO", "ORCL", "ACN", "ADBE", "CRM", "AMD", "TXN", "QCOM", "INTC", "IBM", "AMAT", "LRCX", "ADI", "NOW", "PANW", "SNPS", "CDNS"],
    "Financials": ["JPM", "BAC", "WFC", "C", "MS", "GS", "BRK-B", "V", "MA", "AXP", "BLK", "SCHW", "CB", "MMC", "SPGI", "PGR", "AFL"],
    "Health Care": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "PFE", "DHR", "ISRG", "AMGN", "GILD", "BMY", "VRTX", "CVS", "BDX", "BSX"],
    "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "BKNG", "TJX", "CMG", "ORLY", "GM", "F", "MAR", "HLT", "LVS"],
    "Consumer Staples": ["WMT", "PG", "KO", "PEP", "COST", "PM", "EL", "MO", "MDLZ", "CL", "TGT", "KHC", "DG", "KR", "STZ"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL", "BKR", "HES", "WMB", "DVN"],
    "Communication Services": ["META", "GOOGL", "NFLX", "TMUS", "DIS", "T", "VZ", "CMCSA", "CHTR", "EA", "TTWO"],
    "Industrials": ["CAT", "GE", "UNP", "HON", "UPS", "LMT", "RTX", "DE", "BA", "CSX", "NSC", "ADP", "WM", "FDX", "ETN", "ITW"],
    "Utilities": ["NEE", "SO", "DUK", "CEG", "AEP", "SRE", "D", "EXC", "PCG", "XEL", "ED"],
    "Materials": ["LIN", "APD", "SHW", "FCX", "ECL", "NUE", "NEM", "DOW", "DD", "ALB"],
    "Real Estate": ["PLD", "AMT", "EQIX", "CCI", "WY", "PSA", "O", "SPG"]
}

DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]

# --- 1. SIDEBAR CONFIGURATION ---
st.sidebar.header("1. Choose Your Data Source")
source_type = st.sidebar.radio(
    "Data Source:",
    ["Custom Watchlist", "S&P 500 Sector List", "Dow Jones 30"]
)

# Manage Ticker Population
if source_type == "Custom Watchlist":
    default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL"
    watchlist_input = st.sidebar.text_area("Edit Watchlist (comma-separated):", default_watchlist)
    # Automatically remove duplicates and spaces
    tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
    
elif source_type == "S&P 500 Sector List":
    sectors = ["All Sectors"] + list(SP500_SECTOR_MAP.keys())
    selected_sector = st.sidebar.selectbox("Filter S&P 500 by Sector:", sectors)
    
    if selected_sector == "All Sectors":
        # Combine all tickers from all sectors into one big flat list
        raw_tickers = []
        for sect_tickers in SP500_SECTOR_MAP.values():
            raw_tickers.extend(sect_tickers)
    else:
        raw_tickers = SP500_SECTOR_MAP[selected_sector]
        
    # Remove duplicates while maintaining order
    raw_tickers = list(dict.fromkeys(raw_tickers))
    
    # Unleash slider to scan the entire set
    max_scan = st.sidebar.slider("Number of Stocks to Scan:", 5, len(raw_tickers), len(raw_tickers))
    tickers = raw_tickers[:max_scan]
    
    if max_scan > 50:
        st.sidebar.warning(f"⚠️ Scanning {max_scan} stocks may take up to 30-45 seconds depending on connection speeds.")
    
else:
    tickers = list(dict.fromkeys(DOW_30)) # Remove duplicates

st.sidebar.write(f"**Loaded {len(tickers)} tickers to scan.**")

st.sidebar.write("---")
st.sidebar.header("2. Set Scanner Parameters")
atr_period = st.sidebar.slider("ATR Period (Volatility)", 5, 30, 14)
risk_multiplier = st.sidebar.slider("ATR Risk Multiplier", 1.0, 3.0, 1.5, step=0.1)

st.sidebar.write("---")
st.sidebar.header("3. Filter Dashboard Display")
filter_signal = st.sidebar.multiselect(
    "Show only these signals in dashboard:",
    ["🟢 BUY TRIGGER", "🟡 HOLD (Bullish Trend)", "⚪ HOLD (Bearish/Cash)", "🔴 SELL TRIGGER"],
    default=["🟢 BUY TRIGGER", "🟡 HOLD (Bullish Trend)", "⚪ HOLD (Bearish/Cash)", "🔴 SELL TRIGGER"]
)

# --- 2. SIGNAL LOGIC FUNCTION ---
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
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = latest['Close']
        atr = latest['ATR']
        
        bullish_cross = (prev['EMA_9'] <= prev['EMA_21']) and (latest['EMA_9'] > latest['EMA_21'])
        bearish_cross = (prev['EMA_9'] >= prev['EMA_21']) and (latest['EMA_9'] < latest['EMA_21'])
        
        signal = "⚪ HOLD (Bearish/Cash)"
        stop_loss = 0.0
        target_1 = 0.0
        target_2 = 0.0
        
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
            "Target 1": round(target_1, 2) if target_1 > 0 else "-",
            "Target 2": round(target_2, 2) if target_2 > 0 else "-",
            "RSI": round(latest['RSI'], 1),
            "ATR": round(atr, 2)
        }
    except Exception as e:
        return None

# --- 3. RUN SCANNER INTERFACE ---
if st.button("🔍 Run Scanner Now", type="primary"):
    with st.spinner(f"Scanning {len(tickers)} tickers... This may take a moment."):
        results = []
        for ticker in tickers:
            data = scan_ticker(ticker)
            if data:
                results.append(data)
                
        if results:
            scan_df = pd.DataFrame(results)
            
            # Master Calculations
            total_scanned = len(scan_df)
            buy_triggers = len(scan_df[scan_df['Signal'] == "🟢 BUY TRIGGER"])
            bullish_holds = len(scan_df[scan_df['Signal'] == "🟡 HOLD (Bullish Trend)"])
            sell_triggers = len(scan_df[scan_df['Signal'] == "🔴 SELL TRIGGER"])
            
            # Apply Sidebar Display Filters to the table
            filtered_df = scan_df[scan_df['Signal'].isin(filter_signal)]
            
            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Scanned", total_scanned)
            col2.metric("🟢 Active Buy Triggers", buy_triggers)
            col3.metric("🟡 Bullish Holds", bullish_holds)
            col4.metric("🔴 Active Sell Triggers", sell_triggers)
            
            st.write("---")
            
            # Interactive Table
            st.subheader(f"Filtered Results ({len(filtered_df)} showing)")
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df, 
                    use_container_width=True,
                    column_config={
                        "Signal": st.column_config.TextColumn("Signal Rating"),
                        "Price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                        "Stop Loss": st.column_config.TextColumn("Dynamic Stop Loss"),
                        "Target 1": st.column_config.TextColumn("Profit Target 1"),
                        "Target 2": st.column_config.TextColumn("Profit Target 2")
                    }
                )
            else:
                st.info("No tickers match your active filter criteria. Try expanding the sidebar filters.")
        else:
            st.error("No valid data retrieved. Please check your setup and try again.")
