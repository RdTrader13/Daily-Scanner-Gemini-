Adding a selector for exit styles gives you total flexibility to switch between locking in structured profit targets and riding pure, uncapped trends.
### **What Was Added**
 * **Exit Mode Selector:** Choose between **"Hybrid Scale-Out (Fixed Targets + Trail)"** and **"Pure Trailing Exit (No Fixed Targets)"** in the sidebar.
 * **Dynamic Table Adjustments:** When set to *Pure Trailing Exit*, the Target columns dynamically update to display **"PURE TRAIL"**, keeping your scanner focused strictly on your trailing stop level.
 * **Adaptive Position Sizing Engine:** The calculator adjusts automatically based on your active mode, focusing purely on risk and total share allocation when targets are disabled.
## 💻 Overwrite Code (app.py)
Copy and paste this updated script into your app.py file:
```python
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
    ["Universal 4-HMA Trend-Following", "Large Cap Core Matrix", "Squeeze / Penny Stock Multiplier"],
    key="strategy_choice"
)

# --- TICKER SOURCE CONFIGURATION ---
FULL_SP500 = ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "TSLA", "BRK-B", "LLY", "JPM", "XOM", "UNH", "V", "PG", "MA", "AVGO", "HD", "CVX", "MRK", "ABBV", "COST", "PEP", "ADBE", "WMT", "BAC", "KO", "MCD", "CRM", "CSCO", "ACN", "AMD", "INTC", "TXN", "QCOM", "AMAT", "LRCX", "ADI", "MU", "PANW", "SNPS"]
DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]
TOP_ETFS = ["BITO", "TSLL", "SNXX", "TQQQ", "NVD", "MSTU", "SQQQ", "SOXL", "MUU", "SOXS", "DRAM", "SPY", "SPDN", "QQQ", "IBIT", "PLTD", "TSLG", "XLF", "XLE", "DAMD", "HYG", "ETHA", "EEM", "LQD", "FXI", "KORU", "TLT", "IWM", "KWEB", "TSDD", "EWZ", "TZA", "EWY", "NOWL", "GDX", "SCHD", "BTCZ", "QID", "CONL", "SGOV", "XLU", "NVDL", "SLV", "MSTZ", "IONZ", "RWM", "IGV", "RKLZ", "MUD", "KRE", "AMZD", "RGTZ", "OKLL", "IEMG", "EFA", "SCHX", "SPXS", "SPYM", "XLK", "XLP", "SMH", "XLB", "AVS", "VEA", "USHY", "MULL", "XLV", "SNDQ", "SOXX", "BIL", "SCHG", "RSP", "IEFA", "SPXU", "VXX", "AAPD", "SCO", "LABD", "BMNU", "XBI", "SH", "NVDX", "PSLV", "SCHB", "VCIT", "BITX", "PSQ", "VWO", "BKLN", "AGG", "GOVT", "TSLQ", "MSFU", "XLY", "UVXY", "BND", "VOO", "IVV", "SCHF", "UNG"]

if scan_strategy == "Squeeze / Penny Stock Multiplier":
    st.sidebar.header("📁 Squeeze Asset Array")
    penny_input = st.sidebar.text_area(
        "Speculative Screener Nodes:", 
        "SOUN, BBAI, LCID, GRND, NKLA, NIO, OPEN, SOFI, PTON, MARA, RIOT, CLSK, HUT, CLOV, MQ, NXDR",
        key="penny_input_key"
    )
    tickers = list(dict.fromkeys([t.strip().upper() for t in penny_input.split(",") if t.strip()]))
    max_price_filter = 15.00
else:
    st.sidebar.header("📁 Core Matrix Framework")
    source_type = st.sidebar.radio("Data Source Configuration:", ["Custom Watchlist", "Top ETFs Array", "Full S&P 500 Index", "Dow Jones 30"], key="source_type_key")

    if source_type == "Custom Watchlist":
        default_watchlist = "AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL, LLY, JPM"
        watchlist_input = st.sidebar.text_area("Edit Watchlist Arrays:", default_watchlist, key="watchlist_input_key")
        tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
    elif source_type == "Top ETFs Array":
        raw_etfs = list(dict.fromkeys(TOP_ETFS))
        max_scan = st.sidebar.slider("ETF Scan Processing Depth:", 5, len(raw_etfs), 30, key="etf_scan_depth_key")
        tickers = raw_etfs[:max_scan]
    elif source_type == "Full S&P 500 Index":
        raw_tickers = list(dict.fromkeys(FULL_SP500))
        max_scan = st.sidebar.slider("Scan Processing Depth:", 5, len(raw_tickers), 20, key="sp_scan_depth_key")
        tickers = raw_tickers[:max_scan]
    else:
        tickers = list(dict.fromkeys(DOW_30))
    max_price_filter = 99999.0

st.sidebar.write("---")
st.sidebar.header("⚙️ Risk Parameters")
atr_period = st.sidebar.slider("ATR Measurement Lookback", 5, 30, 14, key="atr_period_key")

# HMA SPECIFIC STOP SELECTOR
if scan_strategy == "Universal 4-HMA Trend-Following":
    hma_stop_mode = st.sidebar.selectbox(
        "HMA Stop-Loss Calculation Mode:",
        ["Most Recent Red HMA Low", "2nd Most Recent Red HMA Low", "ATR Multiplier"],
        key="hma_stop_mode_key"
    )
    if hma_stop_mode == "ATR Multiplier":
        risk_multiplier = st.sidebar.slider("Risk Envelope Scalar (ATR)", 0.5, 5.0, 1.5, step=0.1, key="risk_multiplier_key")
    else:
        risk_multiplier = 1.5
        
    st.sidebar.write("---")
    st.sidebar.header("🎯 Exit Strategy Selector")
    exit_style = st.sidebar.radio(
        "Select Exit Methodology:",
        ["Hybrid Scale-Out (Fixed Targets + Trail)", "Pure Trailing Exit (No Fixed Targets)"],
        key="exit_style_key"
    )
    
    if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)":
        target_1_multiplier = st.sidebar.slider("Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1, key="t1_mult_key")
        target_2_multiplier = st.sidebar.slider("Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1, key="t2_mult_key")
    else:
        target_1_multiplier = None
        target_2_multiplier = None
else:
    exit_style = "Hybrid Scale-Out (Fixed Targets + Trail)"
    risk_multiplier = st.sidebar.slider("Risk Envelope Scalar (Stops)", 1.0, 4.0, 1.5, step=0.1, key="risk_multiplier_key")
    st.sidebar.write("---")
    st.sidebar.header("🎯 Target Horizon Multipliers")
    target_1_multiplier = st.sidebar.slider("Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1, key="t1_mult_key")
    target_2_multiplier = st.sidebar.slider("Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1, key="t2_mult_key")


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
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    df['HMA_Open'] = calculate_hma(df['Open'], 20)
    df['HMA_Close'] = calculate_hma(df['Close'], 20)
    df['HMA_High'] = calculate_hma(df['High'], 20)
    df['HMA_Low'] = calculate_hma(df['Low'], 20)
    
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['Vol_Avg'] = df['Volume'].rolling(window=10).mean()
    df['Relative_Volume'] = df['Volume'] / (df['Vol_Avg'] + 1e-10)
    
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
        
        if scan_strategy == "Universal 4-HMA Trend-Following":
            above_smas = (price > latest['SMA_50']) and (price > latest['SMA_200'])
            
            cross_today = (prev['HMA_Close'] <= prev['HMA_Open']) and (latest['HMA_Close'] > latest['HMA_Open'])
            cross_yesterday = (prev_2['HMA_Close'] <= prev_2['HMA_Open']) and (prev['HMA_Close'] > prev['HMA_Open'])
            
            recent_cross = cross_today or cross_yesterday
            hma_close_sloping_up = latest['HMA_Close'] > prev['HMA_Close']
            hma_open_sloping_up = latest['HMA_Open'] > prev['HMA_Open']
            closed_above_white = price > latest['HMA_Close']
            
            hma_high = max(latest['HMA_High'], latest['HMA_Low'])
            hma_low = min(latest['HMA_High'], latest['HMA_Low'])
            is_inside_hma_channel = (price >= hma_low) and (price <= hma_high)
            
            # Dynamic Stop Calculation
            red_hma_df = df[df['HMA_Close'] < df['HMA_Open']]
            if hma_stop_mode == "Most Recent Red HMA Low":
                stop = red_hma_df.iloc[-1]['HMA_Low'] if not red_hma_df.empty else latest['HMA_Low']
                stop_type = "Most Recent Red HMA Low"
            elif hma_stop_mode == "2nd Most Recent Red HMA Low":
                if len(red_hma_df) >= 2:
                    stop = red_hma_df.iloc[-2]['HMA_Low']
                elif not red_hma_df.empty:
                    stop = red_hma_df.iloc[-1]['HMA_Low']
                else:
                    stop = latest['HMA_Low']
                stop_type = "2nd Most Recent Red HMA Low"
            else:
                stop = price - risk_amount
                stop_type = f"ATR Multiplier ({risk_multiplier}x)"
            
            risk_per_share = max(price - stop, 0.01)
            
            if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)":
                t1_val = round(price + (risk_per_share * target_1_multiplier), 2)
                t2_val = round(price + (risk_per_share * target_2_multiplier), 2)
            else:
                t1_val = "PURE TRAIL"
                t2_val = "PURE TRAIL"
            
            if above_smas and recent_cross and hma_close_sloping_up and hma_open_sloping_up and closed_above_white:
                signal = "🟢 4-HMA BUY ENTRY (Recent Cross + Momentum Confirmed)"
            elif price < stop:
                signal = "🔴 4-HMA EXIT TRIGGER"
            elif is_inside_hma_channel:
                signal = "🟡 4-HMA HOLD (Consolidating inside HMA Band)"
            elif latest['HMA_Close'] > latest['HMA_Open'] and above_smas:
                signal = "🟡 4-HMA BULLISH TREND (Extended Cross)"
            else:
                signal = "⚪ 4-HMA NEUTRAL / WAIT"
                
        elif scan_strategy == "Squeeze / Penny Stock Multiplier":
            stop = price - risk_amount
            stop_type = "ATR Envelope"
            t1_val = round(price + (risk_amount * target_1_multiplier), 2)
            t2_val = round(price + (risk_amount * target_2_multiplier), 2)
            if bullish_cross or (is_coiling == "CRITICAL SQUEEZE" and latest['Close'] > latest['EMA_9']):
                signal = "🟢 EXPANSION TRIGGER"
            else:
                signal = "⚪ MONITOR COILING EFFECT"
        else:
            stop_type = "ATR Envelope"
            if bullish_cross and latest['RSI'] > 40:
                signal = "🟢 BUY TRIGGER"
                stop = price - risk_amount
                t1_val = round(price + (risk_amount * target_1_multiplier), 2)
                t2_val = round(price + (risk_amount * target_2_multiplier), 2)
            elif bearish_cross or (latest['RSI'] > 70 and latest['EMA_9'] < latest['EMA_21']):
                signal = "🔴 SELL TRIGGER"
                stop = price + risk_amount
                t1_val = round(price - (risk_amount * target_1_multiplier), 2)
                t2_val = round(price - (risk_amount * target_2_multiplier), 2)
            elif latest['EMA_9'] > latest['EMA_21']:
                signal = "🟡 HOLD (Bullish Trend)"
                stop = price - risk_amount
                t1_val = round(price + (risk_amount * target_1_multiplier), 2)
                t2_val = round(price + (risk_amount * target_2_multiplier), 2)
            else:
                signal = "⚪ HOLD (Bearish/Cash)"
                stop = price + risk_amount
                t1_val = round(price - (risk_amount * target_1_multiplier), 2)
                t2_val = round(price - (risk_amount * target_2_multiplier), 2)
            
        return {
            "Ticker": ticker_symbol, "Price": round(price, 2), "Signal": signal,
            "Calculated Stop": round(stop, 2), "Stop Type": stop_type,
            "Target 1": t1_val, "Target 2": t2_val,
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
        c2.metric("🟢 Confirmed Buy Entries", len(scan_df[scan_df['Signal'].str.contains("BUY ENTRY")]))
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
    
    # --- POSITION SIZING & RISK CALCULATOR WIDGET ---
    st.subheader("🧮 Dynamic Position Sizing & Target Exit Engine")
    
    calc_col1, calc_col2 = st.columns([1, 1.2])
    
    with calc_col1:
        available_signals = ["Show All Categories"] + sorted(scan_df['Signal'].unique().tolist())
        selected_signal_filter = st.selectbox("Filter Assets by Signal State:", available_signals, key="signal_filter_key")
        
        filtered_calc_df = scan_df[scan_df['Signal'] == selected_signal_filter] if selected_signal_filter != "Show All Categories" else scan_df
            
        if not filtered_calc_df.empty:
            calc_ticker = st.selectbox("Select Asset from Scanned List:", filtered_calc_df['Ticker'].tolist(), key="calc_select_key")
            ticker_data = filtered_calc_df[filtered_calc_df['Ticker'] == calc_ticker].iloc[0]
            
            price_val = float(ticker_data['Price'])
            stop_val = float(ticker_data['Calculated Stop'])
            stop_type_label = str(ticker_data['Stop Type'])
            t1_val = ticker_data['Target 1']
            t2_val = ticker_data['Target 2']
            
            risk_per_share = max(price_val - stop_val, 0.01)
            
            st.info(f"**Asset:** {calc_ticker} | **Current Price:** ${price_val:.2f} | **{stop_type_label}:** ${stop_val:.2f} | **Risk/Share:** ${risk_per_share:.2f}")
            
            acc_balance = st.number_input("Total Account Balance ($)", min_value=100.0, value=10000.0, step=500.0, key="acc_balance_key")
            avail_cash = st.number_input("Available Cash ($)", min_value=0.0, value=5000.0, step=500.0, key="avail_cash_key")
            risk_pct = st.slider("Account Risk Tolerance per Trade (%)", min_value=0.25, max_value=5.0, value=1.0, step=0.25, key="risk_pct_slider_key") / 100.0
            
            alloc_base_choice = st.radio(
                "Capital Allocation Cap Base:",
                ["Total Account Balance", "Available Cash"],
                horizontal=True,
                key="alloc_base_choice_key"
            )
            max_cap_pct = st.slider("Max Capital Allocation per Asset (%)", min_value=1.0, max_value=50.0, value=10.0, step=1.0, key="max_cap_pct_slider_key") / 100.0
        else:
            st.warning("No assets match the selected signal state filter.")
            calc_ticker = None

    with calc_col2:
        if calc_ticker is not None:
            dollar_risk_allowed = acc_balance * risk_pct
            max_capital_allowed = (acc_balance * max_cap_pct) if alloc_base_choice == "Total Account Balance" else (avail_cash * max_cap_pct)
            cap_label_text = f"Total Account Cap ({max_cap_pct*100:.0f}%)" if alloc_base_choice == "Total Account Balance" else f"Available Cash Cap ({max_cap_pct*100:.0f}%)"
            
            shares_by_risk = int(dollar_risk_allowed / risk_per_share)
            shares_by_cap = int(max_capital_allowed / price_val)
            shares_by_cash = int(avail_cash / price_val)
            
            final_shares = max(0, min(shares_by_risk, shares_by_cap, shares_by_cash))
            final_invested = final_shares * price_val
            final_actual_risk = final_shares * risk_per_share
            
            if final_shares == shares_by_risk:
                determining_factor = "🛡️ **Risk Tolerance Limit** (Stopped out at exact risk budget)"
            elif final_shares == shares_by_cap:
                determining_factor = f"🔒 **Capital Allocation Cap** ({cap_label_text})"
            else:
                determining_factor = "💵 **Available Cash Limit** (Restricted by liquid funds)"
                
            st.markdown("### **Entry Position Allocation**")
            m1, m2 = st.columns(2)
            m1.metric("Recommended Share Count", f"{final_shares:,} Shares")
            m2.metric("Total Capital Invested", f"${final_invested:,.2f} ({ (final_invested/acc_balance)*100:.1f}% of Account)")
            
            m3, m4 = st.columns(2)
            m3.metric("Max Dollar Risk", f"${final_actual_risk:,.2f} ({ (final_actual_risk/acc_balance)*100:.2f}%)")
            m4.metric("Max Risk Budget", f"${dollar_risk_allowed:,.2f}")
            
            st.write(f"**Primary Sizing Constraint:** {determining_factor}")

    # --- TOGGLEABLE PARTIAL TAKE-PROFIT EXIT ENGINE ---
    if calc_ticker is not None:
        st.write("---")
        if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)":
            show_exit_calc = st.checkbox("🎯 Enable Partial Take-Profit Exit Calculator", value=True, key="show_exit_calc_key")
            
            if show_exit_calc and final_shares > 0:
                st.markdown("#### **Partial Exit Realization Strategy**")
                p_col1, p_col2 = st.columns(2)
                
                t1_num = float(t1_val)
                t2_num = float(t2_val)
                
                with p_col1:
                    t1_sell_pct = st.slider("Target 1 Exit (% of Total Position)", 0.0, 100.0, 33.3, step=0.1, key="t1_sell_pct_key") / 100.0
                    t1_shares_to_sell = int(final_shares * t1_sell_pct)
                    t1_cash_realized = t1_shares_to_sell * t1_num
                    t1_profit_realized = t1_shares_to_sell * (t1_num - price_val)
                    
                    st.metric(f"Sell at Target 1 (${t1_num:.2f})", f"{t1_shares_to_sell:,} Shares")
                    st.write(f"* **Cash Realized:** ${t1_cash_realized:,.2f}")
                    st.write(f"* **Profit Locked In:** ${t1_profit_realized:,.2f}")
                    
                with p_col2:
                    remaining_shares_after_t1 = final_shares - t1_shares_to_sell
                    t2_sell_pct = st.slider("Target 2 Exit (% of Remaining Position)", 0.0, 100.0, 100.0, step=0.1, key="t2_sell_pct_key") / 100.0
                    t2_shares_to_sell = int(remaining_shares_after_t1 * t2_sell_pct)
                    t2_cash_realized = t2_shares_to_sell * t2_num
                    t2_profit_realized = t2_shares_to_sell * (t2_num - price_val)
                    
                    st.metric(f"Sell at Target 2 (${t2_num:.2f})", f"{t2_shares_to_sell:,} Shares")
                    st.write(f"* **Cash Realized:** ${t2_cash_realized:,.2f}")
                    st.write(f"* **Profit Locked In:** ${t2_profit_realized:,.2f}")
                    
                total_projected_profit = t1_profit_realized + t2_profit_realized
                st.success(f"💰 **Total Projected Profit Across Targets:** **${total_projected_profit:,.2f}** ({ (total_projected_profit / final_invested)*100:.2f}% Return on Invested Capital)")
        else:
            st.info("ℹ️ **Pure Trailing Exit Mode Active:** Position is managed dynamically using trailing stop rules without fixed profit targets.")

    st.html("<br>---")
    st.subheader("🎯 Interactive Structural Chart Window")
    
    chart_ticker = calc_ticker if calc_ticker is not None else scan_df['Ticker'].tolist()[0]
    selected_ticker = st.selectbox("Select Target Node Layer to Visual Map:", scan_df['Ticker'].tolist(), index=scan_df['Ticker'].tolist().index(chart_ticker), key="chart_ticker_select_key")
    
    chart_df = yf.Ticker(selected_ticker).history(period="150d")
    chart_df = calculate_indicators(chart_df)
    row = scan_df[scan_df['Ticker'] == selected_ticker].iloc[0]
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], name="Price Structure"))
    
    if scan_strategy == "Universal 4-HMA Trend-Following":
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_Open'], line=dict(color='yellow', width=1.5), name="HMA 20 (Open)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_Close'], line=dict(color='white', width=1.5), name="HMA 20 (Close)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_High'], line=dict(color='green', width=1.5), name="HMA 20 (High)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['HMA_Low'], line=dict(color='red', width=1.5), name="HMA 20 (Low)"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['SMA_50'], line=dict(color='blue', width=1, dash='dot'), name="50 SMA"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['SMA_200'], line=dict(color='purple', width=1, dash='dot'), name="200 SMA"))
        fig.add_hline(y=row['Calculated Stop'], line_dash="dash", line_color="red", annotation_text=f"Stop Loss ({row['Stop Type']})")
        
        if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)":
            fig.add_hline(y=float(row['Target 1']), line_dash="dash", line_color="lightgreen", annotation_text="Target 1 Horizon Line")
            fig.add_hline(y=float(row['Target 2']), line_dash="dash", line_color="green", annotation_text="Target 2 Horizon Line")
    else:
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_9'], line=dict(color='orange', width=1.5), name="9 EMA"))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_21'], line=dict(color='cyan', width=1.5), name="21 EMA"))
        fig.add_hline(y=row['Calculated Stop'], line_dash="dash", line_color="red", annotation_text="Calculated Stop Placement")
        fig.add_hline(y=float(row['Target 1']), line_dash="dash", line_color="lightgreen", annotation_text="Target 1 Horizon Line")
        fig.add_hline(y=float(row['Target 2']), line_dash="dash", line_color="green", annotation_text="Target 2 Horizon Line")
    
    fig.update_layout(title=f"{selected_ticker} Technical Execution Geometry Map", template="plotly_dark", xaxis_rangeslider_visible=False, height=520)
    st.plotly_chart(fig, use_container_width=True)

```
