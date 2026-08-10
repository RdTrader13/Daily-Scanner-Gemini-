import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Set page config with a wide layout
st.set_page_config(page_title="AlphaScan Pro Engine", layout="wide", initial_sidebar_state="expanded")

# --- INTERFACE THEME STYLING ---
theme_choice = st.sidebar.selectbox(
    "Select UI Theme Workspace:",
    ["Quantum Dark Core", "Art Deco (Turn of the Century)", "Standard Dark Mode", "Standard Light Mode"]
)

if theme_choice == "Quantum Dark Core":
    bg_app, text_main, border_color, metric_bg, font_family = "#0B0F19", "#F8FAFC", "#10B981", "#1E293B", "'Inter', sans-serif"
    header_html = '<div style="background-color: #1E293B; padding: 24px; border-radius: 12px; border-left: 5px solid #10B981; margin-bottom: 25px;"><h3>⚡ AlphaScan Execution Suite</h3></div>'
elif theme_choice == "Art Deco (Turn of the Century)":
    bg_app, text_main, border_color, metric_bg, font_family = "#11161B", "#F3EAD3", "#C5A059", "#1A2129", "'Playfair Display', serif"
    header_html = '<div style="background-color: #1C232B; padding: 24px; border-radius: 4px; border: 2px solid #C5A059; border-style: double; border-width: 6px; text-align: center; margin-bottom: 25px;"><h3>THE TECHNICAL MOMENTUM CHRONICLE</h3></div>'
elif theme_choice == "Standard Dark Mode":
    bg_app, text_main, border_color, metric_bg, font_family = "#0E1117", "#FFFFFF", "#30363D", "#161B22", "sans-serif"
    header_html = "<div><h1>📊 Dark Mode Engine</h1></div>"
else:
    bg_app, text_main, border_color, metric_bg, font_family = "#FFFFFF", "#1F2937", "#E5E7EB", "#F3F4F6", "sans-serif"
    header_html = "<div><h1>📊 Light Mode Engine</h1></div>"

css_payload = f"<style>.stApp {{ background-color: {bg_app} !important; color: {text_main} !important; }} div[data-testid='stMetric'] {{ background-color: {metric_bg} !important; border: 1px solid {border_color} !important; border-radius: 10px !important; }} h1, h2, h3, p {{ font-family: {font_family} !important; color: {text_main} !important; }}</style>"
st.html(css_payload)
st.html(header_html)


# --- STRATEGY ROUTING ENGINE ---
st.sidebar.header("🎯 Strategy Mode")
scan_strategy = st.sidebar.radio(
    "Select Scanning Framework:",
    ["Universal 4-HMA Trend-Following", "Large Cap Core Matrix", "Squeeze / Penny Stock Multiplier"]
)

# --- TICKER SOURCE CONFIGURATION ---
FULL_SP500 = ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "TSLA", "BRK-B", "LLY", "JPM", "XOM", "UNH", "V", "PG", "MA", "AVGO", "HD", "CVX", "MRK", "ABBV", "COST", "PEP", "ADBE", "WMT", "BAC", "KO", "MCD", "CRM", "CSCO", "ACN", "AMD", "INTC", "TXN", "QCOM", "AMAT", "LRCX", "ADI", "MU", "PANW", "SNPS"]
DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]
Top_ETFs = [“BITO”, “TSLL”, “SNXX”, “TQQQ”, “NVD”, “MSTU”, “SQQQ”, “SOXL”, “MUU”, “SOXS”, “DRAM”, “SPY”, “SPDN”, “QQQ”, “IBIT”, “PLTD”, “TSLG”, “XLF”, “XLE”, “DAMD”, “HYG”, “ETHA”, “EEM”, “LQD”, “FXI”, “KORU”, “TLT”, “IWM”, “KWEB”, “TSDD”, “EWZ”, “TZA”, “EWY”, “NOWL”, “GDX”, “SCHD”, “BTCZ”, “QID”, “CONL”, “SGOV”, “XLU”, “NVDL”, “SLV”, “MSTZ”, “IONZ”, “RWM”, “IGV”, “RKLZ”, “MUD”, “KRE”, “AMZD”, “RGTZ”, “OKLL”, “IEMG”, “EFA”, “SCHX”, “SPXS”, “SPYM”, “XLK”, “XLP”, “SMH”, “XLB”, “AVS”, “VEA”, “USHY”, “MULL”, “XLV”, “SNDQ”, “SOXX”, “BIL”, “SCHG”, “RSP”, “IEFA”, “SPXU”, “VXX”, “AAPD”, “SCO”, “LABD”, “BMNU”, “XBI”, “SH”, “NVDX”, “PSLV”, “SCHB”, “VCIT”, “BITX”, “PSQ”, “VWO”, “BKLN”, “AGG”, “GOVT”, “TSLQ”, “MSFU”, “XLY”, “UVXY”, “BND”, “VOO”, “IVV”, “SCHF”, “UNG”]

if scan_strategy == "Squeeze / Penny Stock Multiplier":
    st.sidebar.header("📁 Squeeze Asset Array")
    penny_input = st.sidebar.text_area(
        "Speculative Screener Nodes:", 
        "SOUN, BBAI, LCID, GRND, NKLA, NIO, OPEN, SOFI, PTON, MARA, RIOT, CLSK, HUT, CLOV, MQ, NXDR"
    )
    tickers = list(dict.fromkeys([t.strip().upper() for t in penny_input.split(",") if t.strip()]))
    max_price_filter = 15.00
else:
    st.sidebar.header("📁 Core Matrix Framework")
    source_type = st.sidebar.radio("Data Source Configuration:", ["Custom Watchlist", "Full S&P 500 Index", "Dow Jones 30"])

    if source_type == "Custom Watchlist":
        default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL, LLY, JPM"
        watchlist_input = st.sidebar.text_area("Edit Watchlist Arrays:", default_watchlist)
        tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
    elif source_type == "Full S&P 500 Index":
        raw_tickers = list(dict.fromkeys(FULL_SP500))
        max_scan = st.sidebar.slider("Scan Processing Depth:", 5, len(raw_tickers), 20)
        tickers = raw_tickers[:max_scan]
    else:
        tickers = list(dict.fromkeys(DOW_30))
    max_price_filter = 99999.0

st.sidebar.write("---")
st.sidebar.header("⚙️ Risk Parameters")
atr_period = st.sidebar.slider("ATR Measurement Lookback", 5, 30, 14)
risk_multiplier = st.sidebar.slider("Risk Envelope Scalar (Stops)", 1.0, 4.0, 1.5, step=0.1)

st.sidebar.write("---")
st.sidebar.header("🎯 Target Horizon Multipliers")
target_1_multiplier = st.sidebar.slider("Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1)
target_2_multiplier = st.sidebar.slider("Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1)


# --- HMA MATH CALCULATOR ---
def calculate_wma(series, length):
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(lambda weights_arr: np.dot(weights_arr, weights) / weights.sum(), raw=True)

def calculate_hma(series, length=20):
    half_length = int(length / 2)
    sqrt_length = int(np.sqrt(length))
    wma_half = calculate_wma(series, half_length)
    wma_full = calculate_wma(series, length)
    diff = 2 * wma_half - wma_full
    return calculate_wma(diff, sqrt_length)

# --- TECHNICAL INDICATORS ---
def calculate_indicators(df):
    # Trend Filters for 4-HMA Strategy
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # Universal 4-HMA Indicator Cluster (Period 20)
    df['HMA_Open'] = calculate_hma(df['Open'], 20)   # Yellow Line
    df['HMA_Close'] = calculate_hma(df['Close'], 20) # White Line
    df['HMA_High'] = calculate_hma(df['High'], 20)   # Green Line
    df['HMA_Low'] = calculate_hma(df['Low'], 20)     # Red Line
    
    # Baseline EMA/RSI Filters
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Volume Profiles
    df['Vol_Avg'] = df['Volume'].rolling(window=10).mean()
    df['Relative_Volume'] = df['Volume'] / (df['Vol_Avg'] + 1e-10)
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    df['ATR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(atr_period).mean()
    return df

def scan_ticker(ticker_symbol):
    try:
        df = yf.Ticker(ticker_symbol).history(period="250d")
        if df.empty or len(df) < 200: return None
        df = calculate_indicators(df)
        
        latest, prev, prev_2 = df.iloc[-1], df.iloc[-2], df.iloc[-3]
        price = latest['Close']
        
        if price > max_price_filter: return None
        
        atr = latest['ATR']
        risk_amount = risk_multiplier * atr
        
        ema_pinch = abs(latest['EMA_9'] - latest['EMA_21']) / latest['EMA_21']
        vol_spike = latest['Relative_Volume']
        is_coiling = "CRITICAL SQUEEZE" if (ema_pinch < 0.015 and vol_spike > 1.2) else ("Yes" if ema_pinch < 0.015 else "No")
        
        bullish_cross = (prev['EMA_9'] <= prev['EMA_21']) and (latest['EMA_9'] > latest['EMA_21'])
        bearish_cross = (prev['EMA_9'] >= prev['EMA_21']) and (latest['EMA_9'] < latest['EMA_21'])
        
        # --- STRATEGY ROUTING LOGIC ---
        if scan_strategy == "Universal 4-HMA Trend-Following":
            above_smas = (price > latest['SMA_50']) and (price > latest['SMA_200'])
            
            # Crossover Check 1: Happened Today
            cross_today = (prev['HMA_Close'] <= prev['HMA_Open']) and (latest['HMA_Close'] > latest['HMA_Open'])
            # Crossover Check 2: Happened Yesterday
            cross_yesterday = (prev_2['HMA_Close'] <= prev_2['HMA_Open']) and (prev['HMA_Close'] > prev['HMA_Open'])
            
            recent_cross = cross_today or cross_yesterday
            hma_close_sloping_up = latest['HMA_Close'] > prev['HMA_Close']
            hma_open_sloping_up = latest['HMA_Open'] > prev['HMA_Open']
            
            # Bound Band Evaluation Logic
            hma_high = max(latest['HMA_High'], latest['HMA_Low'])
            hma_low = min(latest['HMA_High'], latest['HMA_Low'])
            is_inside_hma_channel = (price >= hma_low) and (price <= hma_high)
            
            # Initial Stop Loss set to HMA Red Line (Low)
            stop = latest['HMA_Low']
            t1 = price + (risk_amount * target_1_multiplier)
            t2 = price + (risk_amount * target_2_multiplier)
            
            if above_smas and recent_cross and hma_close_sloping_up and hma_open_sloping_up:
                signal = "🟢 4-HMA BUY ENTRY (Recent Cross)"
            elif price < latest['HMA_Low']:
                signal = "🔴 4-HMA EXIT TRIGGER"
            elif is_inside_hma_channel:
                signal = "🟡 4-HMA HOLD (Consolidating inside HMA Band)"
            elif latest['HMA_Close'] > latest['HMA_Open'] and above_smas:
                signal = "🟡 4-HMA BULLISH TREND (Extended Cross)"
            else:
                signal = "⚪ 4-HMA NEUTRAL / WAIT"
                
        elif scan_strategy == "Squeeze / Penny Stock Multiplier":
            stop = price - risk_amount
            t1 = price + (risk_amount * target_1_multiplier)
            t2 = price + (risk_amount * target_2_multiplier)
            if bullish_cross or (is_coiling == "CRITICAL SQUEEZE" and latest['Close'] > latest['EMA_9']):
                signal = "🟢 EXPANSION TRIGGER"
            else:
                signal = "⚪ MONITOR COILING EFFECT"
        else:
            if bullish_cross and latest['RSI'] > 40:
                signal = "🟢 BUY TRIGGER"
                stop, t1, t2 = price - risk_amount, price + (risk_amount * target_1_multiplier), price + (risk_amount * target_2_multiplier)
            elif bearish_cross or (latest['RSI'] > 70 and latest['EMA_9'] < latest['EMA_21']):
                signal = "🔴 SELL TRIGGER"
                stop, t1, t2 = price + risk_amount, price - (risk_amount * target_1_multiplier), price - (risk_amount * target_2_multiplier)
            elif latest['EMA_9'] > latest['EMA_21']:
                signal = "🟡 HOLD (Bullish Trend)"
                stop, t1, t2 = price - risk_amount, price + (risk_amount * target_1_multiplier), price + (risk_amount * target_2_multiplier)
            else:
                signal = "⚪ HOLD (Bearish/Cash)"
                stop, t1, t2 = price + risk_amount, price - (risk_amount * target_1_multiplier), price - (risk_amount * target_2_multiplier)
            
        return {
            "Ticker": ticker_symbol, "Price": round(price, 2), "Signal": signal,
            "HMA Red Stop": round(latest['HMA_Low'], 2) if scan_strategy == "Universal 4-HMA Trend-Following" else round(stop, 2),
            "Target 1": round(t1, 2), "Target 2": round(t2, 2),
            "50 SMA": round(latest['SMA_50'], 2), "200 SMA": round(latest['SMA_200'], 2),
            "RSI": round(latest['RSI'], 1), "Compression Status": is_coiling
        }
    except Exception: return None

# --- RUN PROCESSING CORE ---
if st.button("🔥 Execute System Framework Architecture Scan", type="primary", use_container_width=True):
    with st.spinner("Processing framework algorithms..."):
        results = [res for t in tickers if (res := scan_ticker(t)) is not None]
        if results:
            st.session_state['scan_data'] = pd.DataFrame(results)
            st.session_state['run_success'] = True
        else:
            st.error("No valid matrix node data found.")

# --- RENDER DASHBOARD INTERFACES ---
if st.session_state.get('run_success'):
    scan_df = st.session_state['scan_data']
    
    # KPI Matrix Rows
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nodes Evaluated", len(scan_df))
    if scan_strategy == "Universal 4-HMA Trend-Following":
        c2.metric("🟢 Fresh Buy Entries", len(scan_df[scan_df['Signal'].str.contains("Recent Cross")]))
        c3.metric("🟡 Trend Holds", len(scan_df[scan_df['Signal'].str.contains("BULLISH TREND|Consolidating")]))
        c4.metric("🔴 Exit Alerts", len(scan_df[scan_df['Signal'] == "🔴 4-HMA EXIT TRIGGER"]))
    elif scan_strategy == "Large Cap Core Matrix":
        c2.metric("🟢 Buy Triggers", len(scan_df[scan_df['Signal'] == "🟢 BUY TRIGGER"]))
        c3.metric("🔴 Sell Triggers", len(scan_df[scan_df['Signal'] == "🔴 SELL TRIGGER"]))
        c4.metric("Consolidating Squeezes", len(scan_df[scan_df['Compression Status'] != "No"]))
    else:
        c2.metric("🟢 Breakout Formations", len(scan_df[scan_df['Signal'] == "🟢 EXPANSION TRIGGER"]))
        c3.metric("🔥 Critical Springs", len(scan_df[scan_df['Compression Status'] == "CRITICAL SQUEEZE"]))
        c4.metric("Normal Coils", len(scan_df[scan_df['Compression Status'] == "Yes"]))
        
    st.html("<br>")
    st.dataframe(scan_df, use_container_width=True, height=350)
    
    st.html("<br>---")
    st.subheader("🎯 Interactive Structural Chart Window")
    selected_ticker = st.selectbox("Select Target Node Layer to Visual Map:", scan_df['Ticker'].tolist())
    
    chart_df = yf.Ticker(selected_ticker).history(period="150d")
    chart_df = calculate_indicators(chart_df)
    row = scan_df[scan_df['Ticker'] == selected_ticker].iloc[0]
    
    # Render Plots
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], name="Price Structure"))
    
    if scan_strategy == "Universal 4-HMA Trend-Following":
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_Open'], line=dict(color='yellow', width=1.5), name="HMA 20 (Open)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_Close'], line=dict(color='white', width=1.5), name="HMA 20 (Close)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_High'], line=dict(color='green', width=1.5), name="HMA 20 (High)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_Low'], line=dict(color='red', width=1.5), name="HMA 20 (Low / Trailing Stop)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['SMA_50'], line=dict(color='blue', width=1, dash='dot'), name="50 SMA"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['SMA_200'], line=dict(color='purple', width=1, dash='dot'), name="200 SMA"))
    else:
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_9'], line=dict(color='orange', width=1.5), name="9 EMA"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_21'], line=dict(color='cyan', width=1.5), name="21 EMA"))
        fig.add_hline(y=row['HMA Red Stop'], line_dash="dash", line_color="red", annotation_text="Calculated Stop Placement")
        fig.add_hline(y=row['Target 1'], line_dash="dash", line_color="lightgreen", annotation_text="Target 1 Horizon Line")
        fig.add_hline(y=row['Target 2'], line_dash="dash", line_color="green", annotation_text="Target 2 Horizon Line")
    
    fig.update_layout(title=f"{selected_ticker} Technical Execution Geometry Map", template="plotly_dark", xaxis_rangeslider_visible=False, height=520)
    st.plotly_chart(fig, use_container_width=True)
