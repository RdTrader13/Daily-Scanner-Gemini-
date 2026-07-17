import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="AI S&P 500 Complete Scanner", layout="wide")

# Title and Description
st.title("📊 Complete AI S&P 500 Index Scanner")
st.markdown("Scan your personal watchlist, the Dow 30, or the entire S&P 500 with custom, user-defined Profit Target Multipliers.")

# --- COMPACT HARDCODED FULL S&P 500 TICKER LIST (500+ SYMBOLS) ---
FULL_SP500 = [
    "A", "AAL", "AAPL", "ABBV", "ABNB", "ABT", "ACGL", "ACN", "ADBE", "ADI", "ADM", "ADSK", "ADT", "AEE", "AEP", "AES", "AFL", "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALL", "ALLE", "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN", "ANET", "ANSS", "AON", "AOS", "APA", "APD", "APH", "APO", "APTV", "ARE", "ATO", "AVB", "AVGO", "AVY", "AWK", "AXON", "AXP", "AZO",
    "BA", "BAC", "BALL", "BAX", "BBY", "BDX", "BEN", "BF-B", "BG", "BIIB", "BIO", "BK", "BKNG", "BKR", "BLDR", "BLK", "BMY", "BR", "BRK-B", "BRO", "BSX", "BWA", "BX", "BXP",
    "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCK", "CCL", "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CI", "CINF", "Cisco", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "COR", "COST", "CPB", "CPRT", "CPT", "CRL", "CRM", "CSCO", "CSGP", "CSX", "CTAS", "CTRA", "CTSH", "CTVA", "CVS", "CVX", "CZR",
    "D", "DAL", "DAY", "DD", "DE", "DECK", "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DISH", "DLR", "DLTR", "DOC", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "DXC",
    "EA", "ECL", "ED", "EFX", "EG", "EIX", "EL", "ELV", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN", "ETR", "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR",
    "F", "FANG", "FAST", "FI", "FICO", "FIS", "FITB", "FLT", "FMC", "FOXA", "FOXB", "FRT", "FSLR", "FTNT", "FTV",
    "GD", "GE", "GEHC", "GEV", "GILD", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC", "GPN", "GRMN", "GS", "GWW",
    "HAL", "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUBB", "HUM", "HWM",
    "IBM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INTC", "INTU", "INVH", "IP", "IPG", "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ",
    "J", "JBHT", "JBL", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "JRE", "K", "KDP", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LULU", "LUV", "LVS", "LW", "LYB", "LYV",
    "MA", "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", "MO", "MOH", "MOS", "MPC", "MPWR", "MRK", "MRNA", "MS", "MSI", "MSFT", "MTB", "MTD", "MU", "MULN", "MYL",
    "NDAQ", "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NIQ", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTR", "NUE", "NVDA", "NVR", "NWM", "NWL", "NWS", "NWSA", "NXPI",
    "O", "ODFL", "OKE", "OMC", "ON", "ORLY", "ORCL", "OTIS", "OXY",
    "PANW", "PARA", "PAYC", "PAYX", "PCAR", "PCG", "PCLN", "PDCO", "PDD", "PEAK", "PEG", "PEP", "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PKI", "PLD", "PLTR", "PM", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PX", "PXD", "PYPL",
    "QCOM", "QRVO", "RCL", "RE", "REG", "REGN", "RF", "RHI", "RJM", "RMD", "ROK", "ROL", "ROP", "ROST", "RPRX", "RPT", "RTX", "RVTY", "SBAC", "SBUX", "SCG", "SCHW", "SHW", "SIRI", "SITM", "SIVB", "SJM", "SLB", "SLG", "SNA", "SNPS", "SO", "SPG", "SPGI", "SPLK", "SRE", "STE", "STLD", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYK", "SYY",
    "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TEVA", "TFC", "TFX", "TGT", "TIW", "TJX", "TMO", "TMUS", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXN", "TXT", "TYL",
    "UAL", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB", "V", "VALE", "VFC", "VICI", "VLO", "VLTO", "VMC", "VNO", "VNT", "VRSK", "VRSN", "VRTX", "VTR", "VTRS", "VZ",
    "WAB", "WAT", "WBA", "WBD", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WMT", "WRB", "WRK", "WST", "WTW", "WY", "WYNN", "XCEL", "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS"
]

DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]

# --- 1. SIDEBAR CONFIGURATION ---
st.sidebar.header("1. Data Source Selection")
source_type = st.sidebar.radio(
    "Data Source:",
    ["Custom Watchlist", "Full S&P 500 Index (All 500+)", "Dow Jones 30"]
)

if source_type == "Custom Watchlist":
    default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL"
    watchlist_input = st.sidebar.text_area("Edit Watchlist (comma-separated):", default_watchlist)
    tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
    
elif source_type == "Full S&P 500 Index (All 500+)":
    raw_tickers = list(dict.fromkeys(FULL_SP500))
    max_scan = st.sidebar.slider("Number of Stocks to Scan:", 5, len(raw_tickers), 50)
    tickers = raw_tickers[:max_scan]
    if max_scan > 50:
        st.sidebar.warning(f"⚠️ Scanning {max_scan} stocks will take roughly {round(max_scan * 0.25)} seconds based on connection bounds.")
else:
    tickers = list(dict.fromkeys(DOW_30))

st.sidebar.write(f"**Loaded {len(tickers)} tickers to scan.**")

st.sidebar.write("---")
st.sidebar.header("2. Set Dynamic Risk Parameters")
atr_period = st.sidebar.slider("ATR Period (Volatility Noise)", 5, 30, 14)
risk_multiplier = st.sidebar.slider("ATR Risk Multiplier (Stop Loss)", 1.0, 4.0, 1.5, step=0.1)

st.sidebar.write("---")
st.sidebar.header("3. Custom Profit Target Levels")
# User configurable risk-to-reward multipliers
target_1_multiplier = st.sidebar.slider("Target 1 Risk/Reward Ratio (e.g., 1.5 = 1.5x Risk):", 0.5, 5.0, 1.5, step=0.1)
target_2_multiplier = st.sidebar.slider("Target 2 Risk/Reward Ratio (e.g., 3.0 = 3.0x Risk):", 1.0, 10.0, 3.0, step=0.1)

st.sidebar.write("---")
st.sidebar.header("4. Filter Dashboard Display")
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
        
        # Calculate the base monetary risk amount (Entry Price down to Stop Loss Level)
        risk_amount = risk_multiplier * atr
        
        bullish_cross = (prev['EMA_9'] <= prev['EMA_21']) and (latest['EMA_9'] > latest['EMA_21'])
        bearish_cross = (prev['EMA_9'] >= prev['EMA_21']) and (latest['EMA_9'] < latest['EMA_21'])
        
        signal = "⚪ HOLD (Bearish/Cash)"
        stop_loss = 0.0
        target_1 = 0.0
        target_2 = 0.0
        
        if bullish_cross and latest['RSI'] > 40:
            signal = "🟢 BUY TRIGGER"
            stop_loss = price - risk_amount
            target_1 = price + (risk_amount * target_1_multiplier)
            target_2 = price + (risk_amount * target_2_multiplier)
            
        elif bearish_cross or (latest['RSI'] > 70 and latest['EMA_9'] < latest['EMA_21']):
            signal = "🔴 SELL TRIGGER"
            stop_loss = price + risk_amount
            target_1 = price - (risk_amount * target_1_multiplier)
            target_2 = price - (risk_amount * target_2_multiplier)
            
        elif latest['EMA_9'] > latest['EMA_21']:
            signal = "🟡 HOLD (Bullish Trend)"
            stop_loss = price - risk_amount
            target_1 = price + (risk_amount * target_1_multiplier)
            target_2 = price + (risk_amount * target_2_multiplier)
            
        else:
            signal = "⚪ HOLD (Bearish/Cash)"
            stop_loss = price + risk_amount
            target_1 = price - (risk_amount * target_1_multiplier)
            target_2 = price - (risk_amount * target_2_multiplier)
            
        return {
            "Ticker": ticker_symbol,
            "Price": round(price, 2),
            "Signal": signal,
            "Stop Loss": round(stop_loss, 2) if stop_loss > 0 else "-",
            f"Target 1 ({target_1_multiplier}:1 R:R)": round(target_1, 2) if target_1 > 0 else "-",
            f"Target 2 ({target_2_multiplier}:1 R:R)": round(target_2, 2) if target_2 > 0 else "-",
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
            # Handle dynamic column names for target matching
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
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No tickers match your active filter criteria. Try expanding the sidebar filters.")
        else:
            st.error("No valid data retrieved. Please check your setup and try again.")
