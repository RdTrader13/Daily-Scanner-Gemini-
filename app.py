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
    ["Large Cap Core Matrix", "Squeeze / Penny Stock Multiplier"]
)

# --- TICKER SOURCE CONFIGURATION ---
FULL_SP500 = ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "TSLA", "BRK-B", "LLY", "JPM", "XOM", "UNH", "V", "PG", "MA", "AVGO", "HD", "CVX", "MRK", "ABBV", "COST", "PEP", "ADBE", "WMT", "BAC", "KO", "MCD", "CRM", "CSCO", "ACN", "AMD", "INTC", "TXN", "QCOM", "AMAT", "LRCX", "ADI", "MU", "PANW", "SNPS"]
DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]

if scan_strategy == "Large Cap Core Matrix":
    st.sidebar.header("📁 Core Matrix Framework")
    source_type = st.sidebar.radio("Data Source Configuration:", ["Custom Watchlist", "Full S&P 500 Index", "Dow Jones 30"])

    if source_type == "Custom Watchlist":
        default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL"
        watchlist_input = st.sidebar.text_area("Edit Watchlist Arrays:", default_watchlist)
        tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
    elif source_type == "Full S&P 500 Index":
        raw_tickers = list(dict.fromkeys(FULL_SP500))
        max_scan = st.sidebar.slider("Scan Processing Depth:", 5, len(raw_tickers), 20)
        tickers = raw_tickers[:max_scan]
    else:
        tickers = list(dict.fromkeys(DOW_30))
    max_price_filter = 99999.0
else:
    # High-volatility micro/mid-caps prone to massive single-day moves
    st.sidebar.header("📁 Squeeze Asset Array")
    penny_input = st.sidebar.text_area(
        "Speculative Screener Nodes:", 
        "SOUN, BBAI, LCID, GRND, NKLA, NIO, OPEN, SOFI, PTON, MARA, RIOT, CLSK, HUT, CLOV, MQ, NXDR"
    )
    tickers = list(dict.fromkeys([t.strip().upper() for t in penny_input.split(",") if t.strip()]))
    max_price_filter = 15.00  # Enforces hard cap on micro-cap price targets

st.sidebar.write("---")
st.sidebar.header("⚙️ Risk Parameters")
atr_period = st.sidebar.slider("ATR Measurement Lookback", 5, 30, 14)
risk_multiplier = st.sidebar.slider("Risk Envelope Scalar (Stops)", 1.0, 4.0, 1.5, step=0.1)

st.sidebar.write("---")
st.sidebar.header("🎯 Target Horizon Multipliers")
target_1_multiplier = st.sidebar.slider("Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1)
target_2_multiplier = st.sidebar.slider("Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1)


# --- DATA & MATH LOGIC ---
def calculate_indicators(df):
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
        df = yf.Ticker(ticker_symbol).history(period="60d")
        if df.empty or len(df) < 25: return None
        df = calculate_indicators(df)
        
        latest, prev = df.iloc[-1], df.iloc[-2]
        price = latest['Close']
        
        # Enforce strategy profile threshold filter
        if price > max_price_filter: return None
        
        atr = latest['ATR']
        risk_amount = risk_multiplier * atr
        
        ema_pinch = abs(latest['EMA_9'] - latest['EMA_21']) / latest['EMA_21']
        vol_spike = latest['Relative_Volume']
        
        # Coiling spring mathematical evaluation
        is_coiling = "CRITICAL SQUEEZE" if (ema_pinch < 0.015 and vol_spike > 1.2) else ("Yes" if ema_pinch < 0.015 else "No")
        
        bullish_cross = (prev['EMA_9'] <= prev['EMA_21']) and (latest['EMA_9'] > latest['EMA_21'])
        bearish_cross = (prev['EMA_9'] >= prev['EMA_21']) and (latest['EMA_9'] < latest['EMA_21'])
        
        # Signal Generation Router
        if scan_strategy == "Squeeze / Penny Stock Multiplier":
            if bullish_cross or (is_coiling == "CRITICAL SQUEEZE" and latest['Close'] > latest['EMA_9']):
                signal = "🟢 EXPANSION TRIGGER"
            else:
                signal = "⚪ MONITOR COILING EFFECT"
        else:
            if bullish_cross and latest['RSI'] > 40:
                signal = "🟢 BUY TRIGGER"
            elif bearish_cross or (latest['RSI'] > 70 and latest['EMA_9'] < latest['EMA_21']):
                signal = "🔴 SELL TRIGGER"
            elif latest['EMA_9'] > latest['EMA_21']:
                signal = "🟡 HOLD (Bullish Trend)"
            else:
                signal = "⚪ HOLD (Bearish/Cash)"
                
        # Handle execution calculation targets
        if "BUY" in signal or "EXPANSION" in signal or "Bullish" in signal:
            stop = price - risk_amount
            t1 = price + (risk_amount * target_1_multiplier)
            t2 = price + (risk_amount * target_2_multiplier)
        else:
            stop = price + risk_amount
            t1 = price - (risk_amount * target_1_multiplier)
            t2 = price - (risk_amount * target_2_multiplier)
            
        return {
            "Ticker": ticker_symbol, "Price": round(price, 2), "Signal": signal,
            "Stop Loss": round(stop, 2), "Target 1": round(t1, 2), "Target 2": round(t2, 2),
            "RSI": round(latest['RSI'], 1), "Relative Volume": round(vol_spike, 2), 
            "EMA Pinch %": round(ema_pinch * 100, 2), "Compression Status": is_coiling
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
    if scan_strategy == "Large Cap Core Matrix":
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
    
    chart_df = yf.Ticker(selected_ticker).history(period="60d")
    chart_df = calculate_indicators(chart_df)
    row = scan_df[scan_df['Ticker'] == selected_ticker].iloc[0]
    
    # Render Plots
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], name="Price Structure"))
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_9'], line=dict(color='orange', width=1.5), name="9 EMA"))
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_21'], line=dict(color='cyan', width=1.5), name="21 EMA"))
    
    fig.add_hline(y=row['Stop Loss'], line_dash="dash", line_color="red", annotation_text="Calculated Stop Placement")
    fig.add_hline(y=row['Target 1'], line_dash="dash", line_color="lightgreen", annotation_text="Target 1 Horizon Line")
    fig.add_hline(y=row['Target 2'], line_dash="dash", line_color="green", annotation_text="Target 2 Horizon Line")
    
    fig.update_layout(title=f"{selected_ticker} Technical Execution Geometry Map", template="plotly_dark", xaxis_rangeslider_visible=False, height=520)
    st.plotly_chart(fig, use_container_width=True)
