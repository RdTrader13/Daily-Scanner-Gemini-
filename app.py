import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests  # Import requests to handle browser masking

# Set page config
st.set_page_config(page_title="Live AI S&P 500 & Index Scanner", layout="wide")

# Title and Description
st.title("📊 Live AI S&P 500 & Index Scanner")
st.markdown("Scan your personal watchlist or dynamically query the S&P 500 by industry sector.")

# --- DYNAMIC S&P 500 WIKIPEDIA SCRAPER WITH BROWSER MASKING ---
@st.cache_data(ttl=86400)  # Cache the data for 24 hours so it's lightning-fast
def get_sp500_data():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        # Disguise the request as a real browser visit
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        tables = pd.read_html(response.text)
        df = tables[0]
        # Clean ticker symbols (Wikipedia uses dots instead of hyphens, e.g., BRK.B instead of BRK-B)
        df['Symbol'] = df['Symbol'].str.replace('.', '-', regex=False)
        return df[['Symbol', 'Security', 'GICS Sector']]
    except Exception as e:
        # Fixed Fallback list of top 30 S&P 500 stocks if Wikipedia is down (XOM is only listed once here)
        fallback = pd.DataFrame({
            'Symbol': ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "TSLA", "BRK-B", "LLY", "JPM", "XOM", "UNH", "V", "PG", "MA", "AVGO", "HD", "CVX", "MRK", "ABBV", "COST", "PEP", "ADBE", "WMT", "BAC", "KO", "MCD", "CRM", "CSCO", "ACN"],
            'Security': ["Apple", "Microsoft", "Amazon", "NVIDIA", "Meta", "Alphabet", "Tesla", "Berkshire Hathaway", "Eli Lilly", "JPMorgan Chase", "ExxonMobil", "UnitedHealth", "Visa", "Procter & Gamble", "Mastercard", "Broadcom", "Home Depot", "Chevron", "Merck", "AbbVie", "Costco", "PepsiCo", "Adobe", "Walmart", "Bank of America", "Coca-Cola", "McDonald's", "Salesforce", "Cisco", "Accenture"],
            'GICS Sector': ["Information Technology", "Information Technology", "Consumer Discretionary", "Information Technology", "Communication Services", "Communication Services", "Consumer Discretionary", "Financials", "Health Care", "Financials", "Energy", "Health Care", "Financials", "Consumer Staples", "Financials", "Information Technology", "Consumer Discretionary", "Energy", "Health Care", "Health Care", "Consumer Staples", "Consumer Staples", "Information Technology", "Consumer Staples", "Financials", "Consumer Staples", "Consumer Discretionary", "Information Technology", "Information Technology", "Information Technology"]
        })
        return fallback

# Fetch the live list
sp500_df = get_sp500_data()

# Static presets for other indexes
DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]

# --- 1. SIDEBAR CONFIGURATION ---
st.sidebar.header("1. Choose Your Data Source")
source_type = st.sidebar.radio(
    "Data Source:",
    ["Custom Watchlist", "Live S&P 500 (Dynamically Loaded)", "Dow Jones 30"]
)

# Manage Ticker Population
if source_type == "Custom Watchlist":
    default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL"
    watchlist_input = st.sidebar.text_area("Edit Watchlist (comma-separated):", default_watchlist)
    # Remove duplicates
    tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
    
elif source_type == "Live S&P 500 (Dynamically Loaded)":
    sectors = ["All Sectors"] + list(sp500_df['GICS Sector'].unique())
    selected_sector = st.sidebar.selectbox("Filter S&P 500 by Sector:", sectors)
    
    if selected_sector == "All Sectors":
        filtered_sp500 = sp500_df
    else:
        filtered_sp500 = sp500_df[sp500_df['GICS Sector'] == selected_sector]
        
    # Get tickers and remove duplicates while keeping order
    raw_tickers = list(dict.fromkeys(filtered_sp500['Symbol'].tolist()))
    
    # Unleash slider to the full size of the filtered list (can be all 500+)
    max_scan = st.sidebar.slider("Number of Stocks to Scan:", 5, len(raw_tickers), min(100, len(raw_tickers)))
    tickers = raw_tickers[:max_scan]
    
    # Helpful execution speed warning
    if max_scan > 100:
        st.sidebar.warning(f"⚠️ Scanning {max_scan} stocks may take 1 to 2 minutes depending on Yahoo Finance speeds.")
    
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
