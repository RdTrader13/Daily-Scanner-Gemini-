import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Set page config with a wide layout
st.set_config = st.set_page_config(page_title="AlphaScan Interface", layout="wide", initial_sidebar_state="expanded")

# --- 1. THEME MATRIX ROUTER ---
st.sidebar.header("🎨 Interface Customization")
theme_choice = st.sidebar.selectbox(
    "Select UI Theme Workspace:",
    ["Quantum Dark Core", "Art Deco (Turn of the Century)", "Standard Dark Mode", "Standard Light Mode"]
)

# Define CSS profiles based on selection
if theme_choice == "Quantum Dark Core":
    bg_app = "#0B0F19"
    text_main = "#F8FAFC"
    border_color = "#10B981"
    card_bg = "#1E293B"
    metric_bg = "#1E293B"
    font_family = "'Inter', sans-serif"
    header_html = f"""
        <div style="background-color: {card_bg}; padding: 24px; border-radius: 12px; border-left: 5px solid {border_color}; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <h1 style="color: {text_main} !important; margin: 0; font-family: {font_family}; font-weight: 700; letter-spacing: -0.5px;">⚡ AlphaScan AI Core</h1>
            <p style="color: #94A3B8 !important; margin: 5px 0 0 0; font-size: 1.05rem;">Quantum-grade volatility filters & structural trend tracking engine.</p>
        </div>
    """
elif theme_choice == "Art Deco (Turn of the Century)":
    bg_app = "#11161B"
    text_main = "#F3EAD3"  # Cream warm white
    border_color = "#C5A059" # Metallic Matte Gold
    card_bg = "#1C232B"
    metric_bg = "#1A2129"
    font_family = "'Playfair Display', 'Times New Roman', serif"
    header_html = f"""
        <div style="background-color: {card_bg}; padding: 30px; border-radius: 4px; border: 2px solid {border_color}; border-double: 6px {border_color}; text-align: center; margin-bottom: 25px; background-image: linear-gradient(45deg, #1C232B 25%, #161C22 25%, #161C22 50%, #1C232B 50%, #1C232B 75%, #161C22 75%, #161C22 100%); background-size: 40px 40px;">
            <h1 style="color: {border_color} !important; margin: 0; font-family: {font_family}; font-weight: 900; letter-spacing: 3px; text-transform: uppercase; text-shadow: 1px 1px 2px #000;">THE ALPHASCAN CHRONICLE</h1>
            <div style="width: 150px; height: 2px; background-color: {border_color}; margin: 10px auto;"></div>
            <p style="color: {text_main} !important; margin: 5px 0 0 0; font-size: 1.1rem; font-style: italic; font-family: {font_family};">Automated Financial Machinery & Market Vector Diagnostics.</p>
        </div>
    """
elif theme_choice == "Standard Dark Mode":
    bg_app = "#0E1117"
    text_main = "#FFFFFF"
    border_color = "#30363D"
    card_bg = "#161B22"
    metric_bg = "#161B22"
    font_family = "sans-serif"
    header_html = f"<div style='padding:10px;'><h1>📊 Dark Mode Engine</h1></div>"
else:  # Light Mode
    bg_app = "#FFFFFF"
    text_main = "#1F2937"
    border_color = "#E5E7EB"
    card_bg = "#F9FAFB"
    metric_bg = "#F3F4F6"
    font_family = "sans-serif"
    header_html = f"<div style='padding:10px;'><h1>📊 Light Mode Engine</h1></div>"

# Inject Global Structural Layout Overrides based on selected parameters
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_app} !important;
        color: {text_main} !important;
    }}
    div[data-testid="stMetric"] {{
        background-color: {metric_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: { '4px' if theme_choice == "Art Deco (Turn of the Century)" else '10px' } !important;
        padding: 15px 20px;
    }}
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {text_main} !important;
    }}
    h1, h2, h3, p {{
        font-family: {font_family} !important;
        color: {text_main} !important;
    }}
    </style>
""", unsafe_html=True)

# Render Custom Banner HTML Layer
st.markdown(header_html, unsafe_html=True)


# --- DATA ENGINE LAYERS ---
FULL_SP500 = [
    "A", "AAL", "AAPL", "ABBV", "ABNB", "ABT", "ACGL", "ACN", "ADBE", "ADI", "ADM", "ADSK", "ADT", "AEE", "AEP", "AES", "AFL", "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALL", "ALLE", "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN", "ANET", "ANSS", "AON", "AOS", "APA", "APD", "APH", "APO", "APTV", "ARE", "ATO", "AVB", "AVGO", "AVY", "AWK", "AXON", "AXP", "AZO",
    "BA", "BAC", "BALL", "BAX", "BBY", "BDX", "BEN", "BF-B", "BG", "BIIB", "BIO", "BK", "BKNG", "BKR", "BLDR", "BLK", "BMY", "BR", "BRK-B", "BRO", "BSX", "BWA", "BX", "BXP",
    "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCK", "CCL", "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CI", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "COR", "COST", "CPB", "CPRT", "CPT", "CRL", "CRM", "CSCO", "CSGP", "CSX", "CTAS", "CTRA", "CTSH", "CTVA", "CVS", "CVX", "CZR",
    "D", "DAL", "DAY", "DD", "DE", "DECK", "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR", "DOC", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "DXC",
    "EA", "ECL", "ED", "EFX", "EG", "EIX", "EL", "ELV", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN", "ETR", "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR",
    "F", "FANG", "FAST", "FI", "FICO", "FIS", "FITB", "FLT", "FMC", "FOXA", "FOXB", "FRT", "FSLR", "FTNT", "FTV",
    "GD", "GE", "GEHC", "GEV", "GILD", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC", "GPN", "GRMN", "GS", "GWW",
    "HAL", "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUBB", "HUM", "HWM",
    "IBM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INTC", "INTU", "INVH", "IP", "IPG", "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ",
    "J", "JBHT", "JBL", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KDP", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KVUE", "L", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LULU", "LUV", "LVS", "LW", "LYB", "LYV",
    "MA", "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", "MO", "MOH", "MOS", "MPC", "MPWR", "MRK", "MRNA", "MS", "MSI", "MSFT", "MTB", "MTD", "MU", 
    "NDAQ", "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOW", "NRG", "NSC", "NTAP", "NTR", "NUE", "NVDA", "NVR", "NXPI",
    "O", "ODFL", "OKE", "OMC", "ON", "ORLY", "ORCL", "OTIS", "OXY",
    "PANW", "PARA", "PAYC", "PAYX", "PCAR", "PCG", "PEG", "PEP", "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PKI", "PLD", "PLTR", "PM", "PNC", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PYPL",
    "QCOM", "QRVO", "RCL", "REG", "REGN", "RF", "RHI", "RMD", "ROK", "ROL", "ROP", "ROST", "RPRX", "RTX", "RVTY", "SBAC", "SBUX", "SCHW", "SHW", "SIRI", "SITM", "SJM", "SLB", "SNA", "SNPS", "SO", "SPG", "SPGI", "SRE", "STE", "STLD", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYK", "SYY",
    "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGT", "TJX", "TMO", "TMUS", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXN", "TXT", "TYL",
    "UAL", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB", "V", "VFC", "VICI", "VLO", "VLTO", "VMC", "VNO", "VNT", "VRSK", "VRSN", "VRTX", "VTR", "VTRS", "VZ",
    "WAB", "WAT", "WBA", "WBD", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WMT", "WRB", "WST", "WTW", "WY", "WYNN", "XCEL", "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS"
]

DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]

# --- SIDEBAR SELECTORS ---
st.sidebar.header("📁 Core Matrix Framework")
source_type = st.sidebar.radio(
    "Data Source Configuration:",
    ["Custom Watchlist", "Full S&P 500 Index", "Dow Jones 30"]
)

if source_type == "Custom Watchlist":
    default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL"
    watchlist_input = st.sidebar.text_area("Edit Watchlist Arrays:", default_watchlist)
    tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
elif source_type == "Full S&P 500 Index":
    raw_tickers = list(dict.fromkeys(FULL_SP500))
    max_scan = st.sidebar.slider("Scan Processing Depth:", 5, len(raw_tickers), 50)
    tickers = raw_tickers[:max_scan]
else:
    tickers = list(dict.fromkeys(DOW_30))

st.sidebar.write("---")
st.sidebar.header("⚙️ Parametric Modifiers")
atr_period = st.sidebar.slider("ATR Measurement Lookback", 5, 30, 14)
risk_multiplier = st.sidebar.slider("Risk Envelope Scalar (Stops)", 1.0, 4.0, 1.5, step=0.1)

st.sidebar.write("---")
st.sidebar.header("🎯 Target Horizon Multipliers")
target_1_multiplier = st.sidebar.slider("Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1)
target_2_multiplier = st.sidebar.slider("Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1)

st.sidebar.write("---")
st.sidebar.header("👁️ Filter Viewports")
filter_signal = st.sidebar.multiselect(
    "Active Render States:",
    ["🟢 BUY TRIGGER", "🟡 HOLD (Bullish Trend)", "⚪ HOLD (Bearish/Cash)", "🔴 SELL TRIGGER"],
    default=["🟢 BUY TRIGGER", "🟡 HOLD (Bullish Trend)", "⚪ HOLD (Bearish/Cash)", "🔴 SELL TRIGGER"]
)

# --- SIGNAL CALCULATOR ---
def scan_ticker(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="60d")
        if df.empty or len(df) < 25: return None
        
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(atr_period).mean()
        
        latest, prev = df.iloc[-1], df.iloc[-2]
        price, atr = latest['Close'], latest['ATR']
        risk_amount = risk_multiplier * atr
        
        bullish_cross = (prev['EMA_9'] <= prev['EMA_21']) and (latest['EMA_9'] > latest['EMA_21'])
        bearish_cross = (prev['EMA_9'] >= prev['EMA_21']) and (latest['EMA_9'] < latest['EMA_21'])
        
        signal = "⚪ HOLD (Bearish/Cash)"
        stop_loss, target_1, target_2 = 0.0, 0.0, 0.0
        
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
            "Ticker": ticker_symbol, "Price": round(price, 2), "Signal": signal,
            "Stop Loss": round(stop_loss, 2) if stop_loss > 0 else "-",
            "Target 1": round(target_1, 2) if target_1 > 0 else "-",
            "Target 2": round(target_2, 2) if target_2 > 0 else "-",
            "RSI": round(latest['RSI'], 1), "ATR": round(atr, 2)
        }
    except Exception: return None

# --- RUN PROCESSING CORE ---
if st.button("🔥 Run Computational Matrix Scan", type="primary", use_container_width=True):
    with st.spinner("Executing system architecture sweeps..."):
        results = [scan_ticker(t) for t in tickers if scan_ticker(t) is not None]
                
        if results:
            scan_df = pd.DataFrame(results)
            filtered_df = scan_df[scan_df['Signal'].isin(filter_signal)]
            
            # Metric Rows
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Nodes Swept", len(scan_df))
            col2.metric("Buy Formations", len(scan_df[scan_df['Signal'] == "🟢 BUY TRIGGER"]))
            col3.metric("Bullish Structural Holds", len(scan_df[scan_df['Signal'] == "🟡 HOLD (Bullish Trend)"]))
            col4.metric("Active Liquidations", len(scan_df[scan_df['Signal'] == "🔴 SELL TRIGGER"]))
            
            st.markdown("<br>", unsafe_html=True)
            st.subheader(f"📊 Live Output Dashboard ({len(filtered_df)} layers rendering)")
            
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df, use_container_width=True, height=500,
                    column_config={
                        "Price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                        "Stop Loss": st.column_config.NumberColumn("Calculated Stop", format="$%.2f"),
                        "Target 1": st.column_config.NumberColumn(f"Target 1 ({target_1_multiplier}:1)", format="$%.2f"),
                        "Target 2": st.column_config.NumberColumn(f"Target 2 ({target_2_multiplier}:1)", format="$%.2f")
                    }
                )
            else:
                st.info("No nodes match current layer criteria.")
        else:
            st.error("Matrix compilation error.")
