import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go  # Premium free charting tool

# Set page config with a wide layout
st.set_page_config(page_title="AlphaScan Visual Engine", layout="wide", initial_sidebar_state="expanded")

# --- INTERFACE THEME STYLING ---
theme_choice = st.sidebar.selectbox(
    "Select UI Theme Workspace:",
    ["Quantum Dark Core", "Art Deco (Turn of the Century)", "Standard Dark Mode", "Standard Light Mode"]
)

if theme_choice == "Quantum Dark Core":
    bg_app, text_main, border_color, metric_bg, font_family = "#0B0F19", "#F8FAFC", "#10B981", "#1E293B", "'Inter', sans-serif"
    header_html = '<div style="background-color: #1E293B; padding: 24px; border-radius: 12px; border-left: 5px solid #10B981; margin-bottom: 25px;"><h3>⚡ AlphaScan Visual Core</h3></div>'
elif theme_choice == "Art Deco (Turn of the Century)":
    bg_app, text_main, border_color, metric_bg, font_family = "#11161B", "#F3EAD3", "#C5A059", "#1A2129", "'Playfair Display', serif"
    header_html = '<div style="background-color: #1C232B; padding: 24px; border-radius: 4px; border: 2px solid #C5A059; border-style: double; border-width: 6px; text-align: center; margin-bottom: 25px;"><h3>THE VISUAL ALPHASCAN CHRONICLE</h3></div>'
elif theme_choice == "Standard Dark Mode":
    bg_app, text_main, border_color, metric_bg, font_family = "#0E1117", "#FFFFFF", "#30363D", "#161B22", "sans-serif"
    header_html = "<div><h1>📊 Dark Mode Engine</h1></div>"
else:
    bg_app, text_main, border_color, metric_bg, font_family = "#FFFFFF", "#1F2937", "#E5E7EB", "#F3F4F6", "sans-serif"
    header_html = "<div><h1>📊 Light Mode Engine</h1></div>"

css_payload = f"<style>.stApp {{ background-color: {bg_app} !important; color: {text_main} !important; }} div[data-testid='stMetric'] {{ background-color: {metric_bg} !important; border: 1px solid {border_color} !important; border-radius: 10px !important; }} h1, h2, h3, p {{ font-family: {font_family} !important; color: {text_main} !important; }}</style>"
st.html(css_payload)
st.html(header_html)

# --- COMPLETE TICKER LIST ---
FULL_SP500 = ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "TSLA", "BRK-B", "LLY", "JPM", "XOM", "UNH", "V", "PG", "MA", "AVGO", "HD", "CVX", "MRK", "ABBV", "COST", "PEP", "ADBE", "WMT", "BAC", "KO", "MCD", "CRM", "CSCO", "ACN", "AMD", "INTC", "TXN", "QCOM", "AMAT", "LRCX", "ADI", "MU", "PANW", "SNPS"]
DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]

st.sidebar.header("📁 Data Inputs")
source_type = st.sidebar.radio("Data Source Configuration:", ["Custom Watchlist", "Full S&P 500 Index", "Dow Jones 30"])

if source_type == "Custom Watchlist":
    default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL"
    watchlist_input = st.sidebar.text_area("Edit Watchlist:", default_watchlist)
    tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
elif source_type == "Full S&P 500 Index":
    raw_tickers = list(dict.fromkeys(FULL_SP500))
    max_scan = st.sidebar.slider("Scan Depth:", 5, len(raw_tickers), 20)
    tickers = raw_tickers[:max_scan]
else:
    tickers = list(dict.fromkeys(DOW_30))

st.sidebar.write("---")
st.sidebar.header("⚙️ Risk Parameters")
atr_period = st.sidebar.slider("ATR Lookback Window", 5, 30, 14)
risk_multiplier = st.sidebar.slider("Risk Scalar (Stop Loss)", 1.0, 4.0, 1.5, step=0.1)
target_1_multiplier = st.sidebar.slider("Target 1 Multiplier (R:R)", 0.5, 5.0, 1.5, step=0.1)
target_2_multiplier = st.sidebar.slider("Target 2 Multiplier (R:R)", 1.0, 10.0, 3.0, step=0.1)

# --- ENGINE LOGIC ---
def calculate_indicators(df):
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
    df['ATR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(atr_period).mean()
    return df

def scan_ticker(ticker_symbol):
    try:
        df = yf.Ticker(ticker_symbol).history(period="60d")
        if df.empty or len(df) < 25: return None
        df = calculate_indicators(df)
        latest, prev = df.iloc[-1], df.iloc[-2]
        price, atr = latest['Close'], latest['ATR']
        risk_amount = risk_multiplier * atr
        
        bullish_cross = (prev['EMA_9'] <= prev['EMA_21']) and (latest['EMA_9'] > latest['EMA_21'])
        bearish_cross = (prev['EMA_9'] >= prev['EMA_21']) and (latest['EMA_9'] < latest['EMA_21'])
        
        # Squeeze Detection Logic (Coiling Spring)
        ema_pct_difference = abs(latest['EMA_9'] - latest['EMA_21']) / latest['EMA_21']
        is_squeezing = "Yes" if ema_pct_difference < 0.01 else "No"
        
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
            "Stop Loss": round(stop, 2), "Target 1": round(t1, 2), "Target 2": round(t2, 2),
            "RSI": round(latest['RSI'], 1), "ATR": round(atr, 2), "Coiling Spring?": is_squeezing
        }
    except Exception: return None

# --- RUN PROCESSING CORE ---
if st.button("🔥 Run Technical Mapping & Scan", type="primary", use_container_width=True):
    with st.spinner("Compiling structural market layers..."):
        results = [res for t in tickers if (res := scan_ticker(t)) is not None]
        
        if results:
            st.session_state['scan_data'] = pd.DataFrame(results)
            st.session_state['run_success'] = True
        else:
            st.error("Data mapping compilation error.")

# --- RENDER DASHBOARD & CHARTS ---
if st.session_state.get('run_success'):
    scan_df = st.session_state['scan_data']
    
    # KPI Matrix
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nodes Evaluated", len(scan_df))
    c2.metric("🟢 Buy Triggers", len(scan_df[scan_df['Signal'] == "🟢 BUY TRIGGER"]))
    c3.metric("🟡 Bullish Holds", len(scan_df[scan_df['Signal'] == "🟡 HOLD (Bullish Trend)"]))
    c4.metric("Squeezed (Coiling)", len(scan_df[scan_df['Coiling Spring?'] == "Yes"]))
    
    st.html("<br>")
    st.dataframe(scan_df, use_container_width=True, height=350)
    
    st.html("<br>---")
    st.subheader("🎯 Interactive Execution Chart Window")
    selected_ticker = st.selectbox("Select Ticker to Graph Layout:", scan_df['Ticker'].tolist())
    
    # Fetch data specifically for plotting the chosen stock
    chart_df = yf.Ticker(selected_ticker).history(period="60d")
    chart_df = calculate_indicators(chart_df)
    row = scan_df[scan_df['Ticker'] == selected_ticker].iloc[0]
    
    # Build Interactive Candlestick Chart via Plotly
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_9'], line=dict(color='orange', width=1.5), name="9 EMA"))
    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_21'], line=dict(color='cyan', width=1.5), name="21 EMA"))
    
    # Map target line references overlay
    if row['Stop Loss'] != "-":
        fig.add_hline(y=row['Stop Loss'], line_dash="dash", line_color="red", annotation_text="Stop Loss")
        fig.add_hline(y=row['Target 1'], line_dash="dash", line_color="lightgreen", annotation_text="Target 1")
        fig.add_hline(y=row['Target 2'], line_dash="dash", line_color="green", annotation_text="Target 2")
        
    fig.update_layout(title=f"{selected_ticker} Execution Roadmap Layout", template="plotly_dark", xaxis_rangeslider_visible=False, height=550)
    st.plotly_chart(fig, use_container_width=True)
