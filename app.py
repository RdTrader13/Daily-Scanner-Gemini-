import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
from sqlalchemy import create_engine, text

# Set page config
st.set_page_config(page_title="AlphaScan Execution Suite", layout="wide", initial_sidebar_state="expanded")

# --- 1. PRIVATE APP SECURITY ---
def check_password():
    """Returns True if the user has entered the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("### 🔐 Private Access Required")
        user_password = st.text_input("Enter Passcode:", type="password", key="app_pass_input")
        
        # Change this string to your preferred master passcode or use st.secrets
        APP_PASSCODE = st.secrets.get("APP_PASSCODE", "MyTradingApp2026!") 
        
        if st.button("Unlock Dashboard"):
            if user_password == APP_PASSCODE:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect Passcode")
        st.stop()

check_password()

# --- 2. SUPABASE POSTGRES CONNECTION ---
# Fallback uses environment secret or direct URI string
DEFAULT_URI = "postgresql://postgres:oGBXMxgBOXD9q0KP@db.qcdmggsmfuyezazxgdbm.supabase.co:5432/postgres"
DB_URI = st.secrets.get("DATABASE_URL", DEFAULT_URI)

@st.cache_resource
def get_db_engine():
    return create_engine(DB_URI, pool_pre_ping=True)

engine = get_db_engine()

def init_db():
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS active_positions (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) NOT NULL,
                strategy VARCHAR(100) NOT NULL,
                entry_date VARCHAR(20) NOT NULL,
                budget_price NUMERIC NOT NULL,
                actual_fill_price NUMERIC NOT NULL,
                shares INT NOT NULL,
                stop_loss NUMERIC NOT NULL,
                target_1 VARCHAR(50),
                target_2 VARCHAR(50),
                notes TEXT
            );
        '''))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS trade_journal (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) NOT NULL,
                strategy VARCHAR(100) NOT NULL,
                entry_date VARCHAR(20) NOT NULL,
                exit_date VARCHAR(20) NOT NULL,
                holding_days INT NOT NULL,
                budget_price NUMERIC NOT NULL,
                actual_fill_price NUMERIC NOT NULL,
                exit_price NUMERIC NOT NULL,
                shares INT NOT NULL,
                realized_pnl NUMERIC NOT NULL,
                pnl_pct NUMERIC NOT NULL,
                slippage NUMERIC NOT NULL,
                notes TEXT
            );
        '''))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS account_snapshots (
                id SERIAL PRIMARY KEY,
                snapshot_date VARCHAR(20) NOT NULL,
                cash_balance NUMERIC NOT NULL,
                position_value NUMERIC NOT NULL,
                total_account_value NUMERIC NOT NULL,
                notes TEXT
            );
        '''))
        conn.commit()

init_db()

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("📌 Navigation")
app_mode = st.sidebar.radio("Go to Page:", ["⚡ AlphaScan Engine", "💼 Active Portfolio Manager", "📖 Trade Journal & Analytics"])

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

# ==========================================
# PAGE 1: ALPHASCAN ENGINE
# ==========================================
if app_mode == "⚡ AlphaScan Engine":
    st.sidebar.header("🎯 Strategy Mode")
    scan_strategy = st.sidebar.radio(
        "Select Scanning Framework:",
        ["Universal 4-HMA Trend-Following", "Large Cap Core Matrix", "Squeeze / Penny Stock Multiplier"],
        key="strategy_choice"
    )

    FULL_SP500 = ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "TSLA", "BRK-B", "LLY", "JPM", "XOM", "UNH", "V", "PG", "MA", "AVGO", "HD", "CVX", "MRK", "ABBV", "COST", "PEP", "ADBE", "WMT", "BAC", "KO", "MCD", "CRM", "CSCO", "ACN", "AMD", "INTC", "TXN", "QCOM", "AMAT", "LRCX", "ADI", "MU", "PANW", "SNPS"]
    DOW_30 = ["AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]
    TOP_ETFS = ["BITO", "TSLL", "SNXX", "TQQQ", "NVD", "MSTU", "SQQQ", "SOXL", "MUU", "SOXS", "DRAM", "SPY", "SPDN", "QQQ", "IBIT", "PLTD", "TSLG", "XLF", "XLE", "DAMD", "HYG", "ETHA", "EEM", "LQD", "FXI", "KORU", "TLT", "IWM", "KWEB", "TSDD", "EWZ", "TZA", "EWY", "NOWL", "GDX", "SCHD", "BTCZ", "QID", "CONL", "SGOV", "XLU", "NVDL", "SLV", "MSTZ", "IONZ", "RWM", "IGV", "RKLZ", "MUD", "KRE", "AMZD", "RGTZ", "OKLL", "IEMG", "EFA", "SCHX", "SPXS", "SPYM", "XLK", "XLP", "SMH", "XLB", "AVS", "VEA", "USHY", "MULL", "XLV", "SNDQ", "SOXX", "BIL", "SCHG", "RSP", "IEFA", "SPXU", "VXX", "AAPD", "SCO", "LABD", "BMNU", "XBI", "SH", "NVDX", "PSLV", "SCHB", "VCIT", "BITX", "PSQ", "VWO", "BKLN", "AGG", "GOVT", "TSLQ", "MSFU", "XLY", "UVXY", "BND", "VOO", "IVV", "SCHF", "UNG"]

    if scan_strategy == "Squeeze / Penny Stock Multiplier":
        st.sidebar.header("📁 Squeeze Asset Array")
        penny_input = st.sidebar.text_area("Speculative Screener Nodes:", "SOUN, BBAI, LCID, GRND, NKLA, NIO, OPEN, SOFI, PTON, MARA, RIOT, CLSK, HUT, CLOV, MQ, NXDR", key="penny_input_key")
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

    if scan_strategy == "Universal 4-HMA Trend-Following":
        hma_stop_mode = st.sidebar.selectbox("HMA Stop-Loss Mode:", ["Most Recent Red HMA Low", "2nd Most Recent Red HMA Low", "ATR Multiplier"], key="hma_stop_mode_key")
        risk_multiplier = st.sidebar.slider("Risk Envelope Scalar (ATR)", 0.5, 5.0, 1.5, step=0.1, key="risk_multiplier_key") if hma_stop_mode == "ATR Multiplier" else 1.5
        st.sidebar.write("---")
        exit_style = st.sidebar.radio("Select Exit Methodology:", ["Hybrid Scale-Out (Fixed Targets + Trail)", "Pure Trailing Exit (No Fixed Targets)"], key="exit_style_key")
        if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)":
            target_1_multiplier = st.sidebar.slider("Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1, key="t1_mult_key")
            target_2_multiplier = st.sidebar.slider("Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1, key="t2_mult_key")
        else:
            target_1_multiplier, target_2_multiplier = None, None
    else:
        exit_style = "Hybrid Scale-Out (Fixed Targets + Trail)"
        risk_multiplier = st.sidebar.slider("Risk Envelope Scalar (Stops)", 1.0, 4.0, 1.5, step=0.1, key="risk_multiplier_key")
        st.sidebar.write("---")
        target_1_multiplier = st.sidebar.slider("Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1, key="t1_mult_key")
        target_2_multiplier = st.sidebar.slider("Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1, key="t2_mult_key")

    def calculate_wma(series, length):
        weights = np.arange(1, length + 1)
        return series.rolling(length).apply(lambda w: np.dot(w, weights) / weights.sum(), raw=True)

    def calculate_hma(series, length=20):
        wma_half = calculate_wma(series, int(length / 2))
        wma_full = calculate_wma(series, length)
        return calculate_wma(2 * wma_half - wma_full, int(np.sqrt(length)))

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
        rs = gain.rolling(14).mean() / (loss.rolling(14).mean() + 1e-10)
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
                recent_cross = ((prev['HMA_Close'] <= prev['HMA_Open']) and (latest['HMA_Close'] > latest['HMA_Open'])) or ((prev_2['HMA_Close'] <= prev_2['HMA_Open']) and (prev['HMA_Close'] > prev['HMA_Open']))
                hma_close_sloping_up = latest['HMA_Close'] > prev['HMA_Close']
                hma_open_sloping_up = latest['HMA_Open'] > prev['HMA_Open']
                closed_above_white = price > latest['HMA_Close']
                hma_high, hma_low = max(latest['HMA_High'], latest['HMA_Low']), min(latest['HMA_High'], latest['HMA_Low'])
                is_inside_hma_channel = (price >= hma_low) and (price <= hma_high)
                
                red_hma_df = df[df['HMA_Close'] < df['HMA_Open']]
                if hma_stop_mode == "Most Recent Red HMA Low":
                    stop = red_hma_df.iloc[-1]['HMA_Low'] if not red_hma_df.empty else latest['HMA_Low']
                    stop_type = "Most Recent Red HMA Low"
                elif hma_stop_mode == "2nd Most Recent Red HMA Low":
                    stop = red_hma_df.iloc[-2]['HMA_Low'] if len(red_hma_df) >= 2 else (red_hma_df.iloc[-1]['HMA_Low'] if not red_hma_df.empty else latest['HMA_Low'])
                    stop_type = "2nd Most Recent Red HMA Low"
                else:
                    stop = price - risk_amount
                    stop_type = f"ATR Multiplier ({risk_multiplier}x)"
                
                risk_per_share = max(price - stop, 0.01)
                t1_val = round(price + (risk_per_share * target_1_multiplier), 2) if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)" else "PURE TRAIL"
                t2_val = round(price + (risk_per_share * target_2_multiplier), 2) if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)" else "PURE TRAIL"
                
                if above_smas and recent_cross and hma_close_sloping_up and hma_open_sloping_up and closed_above_white:
                    signal = "🟢 BUY ENTRY"
                elif price < stop: signal = "🔴 EXIT TRIGGER"
                elif is_inside_hma_channel: signal = "🟡 HOLD (Consolidating)"
                elif latest['HMA_Close'] > latest['HMA_Open'] and above_smas: signal = "🟡 BULLISH TREND"
                else: signal = "⚪ NEUTRAL / WAIT"
                    
            elif scan_strategy == "Squeeze / Penny Stock Multiplier":
                stop = price - risk_amount
                stop_type = "ATR Envelope"
                t1_val = round(price + (risk_amount * target_1_multiplier), 2)
                t2_val = round(price + (risk_amount * target_2_multiplier), 2)
                signal = "🟢 EXPANSION TRIGGER" if (bullish_cross or (is_coiling == "CRITICAL SQUEEZE" and latest['Close'] > latest['EMA_9'])) else "⚪ MONITOR COILING"
            else:
                stop_type = "ATR Envelope"
                if bullish_cross and latest['RSI'] > 40:
                    signal, stop = "🟢 BUY TRIGGER", price - risk_amount
                    t1_val, t2_val = round(price + (risk_amount * target_1_multiplier), 2), round(price + (risk_amount * target_2_multiplier), 2)
                elif bearish_cross or (latest['RSI'] > 70 and latest['EMA_9'] < latest['EMA_21']):
                    signal, stop = "🔴 SELL TRIGGER", price + risk_amount
                    t1_val, t2_val = round(price - (risk_amount * target_1_multiplier), 2), round(price - (risk_amount * target_2_multiplier), 2)
                elif latest['EMA_9'] > latest['EMA_21']:
                    signal, stop = "🟡 HOLD (Bullish)", price - risk_amount
                    t1_val, t2_val = round(price + (risk_amount * target_1_multiplier), 2), round(price + (risk_amount * target_2_multiplier), 2)
                else:
                    signal, stop = "⚪ HOLD (Cash)", price + risk_amount
                    t1_val, t2_val = round(price - (risk_amount * target_1_multiplier), 2), round(price - (risk_amount * target_2_multiplier), 2)
                
            return {
                "Ticker": ticker_symbol, "Price": round(price, 2), "Signal": signal,
                "Calculated Stop": round(stop, 2), "Stop Type": stop_type,
                "Target 1": t1_val, "Target 2": t2_val,
                "50 SMA": round(latest['SMA_50'], 2), "200 SMA": round(latest['SMA_200'], 2),
                "RSI": round(latest['RSI'], 1), "Compression Status": is_coiling
            }
        except Exception: return None

    if st.button("🔥 Execute System Framework Architecture Scan", type="primary", use_container_width=True):
        with st.spinner("Processing framework algorithms..."):
            results = [res for t in tickers if (res := scan_ticker(t)) is not None]
            if results:
                st.session_state['scan_data'] = pd.DataFrame(results)
                st.session_state['total_nodes'] = len(tickers)
                st.session_state['run_success'] = True
            else: st.error("No valid matrix node data found.")

    if st.session_state.get('run_success'):
        scan_df = st.session_state['scan_data']
        total_nodes = st.session_state.get('total_nodes', len(scan_df))
        buy_hits = len(scan_df[scan_df['Signal'].str.contains('🟢')])
        exit_hits = len(scan_df[scan_df['Signal'].str.contains('🔴')])
        hold_hits = len(scan_df[scan_df['Signal'].str.contains('🟡')])
        neutral_hits = len(scan_df[scan_df['Signal'].str.contains('⚪')])

        st.markdown("### 🔍 **Scan Results Summary**")
        sc_col1, sc_col2, sc_col3, sc_col4, sc_col5 = st.columns(5)
        sc_col1.metric("Nodes Scanned", f"{total_nodes} Tickers")
        sc_col2.metric("🟢 Actionable Buy Signals", f"{buy_hits} Hits")
        sc_col3.metric("🔴 Exit Triggers", f"{exit_hits} Hits")
        sc_col4.metric("🟡 Trend Holds", f"{hold_hits} Hits")
        sc_col5.metric("⚪ Neutral / Cash", f"{neutral_hits} Hits")
        
        st.write("---")
        st.dataframe(scan_df, use_container_width=True, height=280)
        st.write("---")
        st.subheader("🧮 Position Sizing & Direct Portfolio Logging")
        
        calc_col1, calc_col2 = st.columns([1, 1.2])
        with calc_col1:
            available_signals = ["Show All Categories"] + sorted(scan_df['Signal'].unique().tolist())
            selected_signal_filter = st.selectbox("Filter Assets by Signal State:", available_signals, key="signal_filter_key")
            filtered_calc_df = scan_df[scan_df['Signal'] == selected_signal_filter] if selected_signal_filter != "Show All Categories" else scan_df
                
            if not filtered_calc_df.empty:
                calc_ticker = st.selectbox("Select Asset from Scanned List:", filtered_calc_df['Ticker'].tolist(), key="calc_select_key")
                ticker_data = filtered_calc_df[filtered_calc_df['Ticker'] == calc_ticker].iloc[0]
                
                budget_price_val = float(ticker_data['Price'])
                stop_val = float(ticker_data['Calculated Stop'])
                t1_val, t2_val = str(ticker_data['Target 1']), str(ticker_data['Target 2'])
                risk_per_share = max(budget_price_val - stop_val, 0.01)
                
                acc_balance = st.number_input("Total Account Balance ($)", min_value=100.0, value=10000.0, step=500.0)
                avail_cash = st.number_input("Available Cash ($)", min_value=0.0, value=5000.0, step=500.0)
                risk_pct = st.slider("Account Risk Tolerance (%)", 0.25, 5.0, 1.0, 0.25) / 100.0
                max_cap_pct = st.slider("Max Capital Allocation (%)", 1.0, 50.0, 10.0, 1.0) / 100.0
            else: calc_ticker = None

        with calc_col2:
            if calc_ticker is not None:
                dollar_risk_allowed = acc_balance * risk_pct
                max_capital_allowed = avail_cash * max_cap_pct
                
                shares_by_risk = int(dollar_risk_allowed / risk_per_share)
                shares_by_cap = int(max_capital_allowed / budget_price_val)
                shares_by_cash = int(avail_cash / budget_price_val)
                final_shares = max(0, min(shares_by_risk, shares_by_cap, shares_by_cash))
                
                st.markdown("### **Entry Position Allocation**")
                st.metric("Recommended Share Count", f"{final_shares:,} Shares")
                st.metric("Budget Capital Required", f"${final_shares * budget_price_val:,.2f}")
                
                st.write("---")
                st.markdown("#### **💾 Log Trade to Portfolio Manager**")
                actual_fill_price_input = st.number_input("Actual Broker Fill Price ($)", min_value=0.01, value=budget_price_val, step=0.01)
                entry_date_input = st.date_input("Entry Date", value=datetime.today())
                trade_notes = st.text_input("Trade Notes / Setup Context", value=f"Scanned from {scan_strategy}")
                
                if st.button("🚀 Open & Track Position", type="primary"):
                    with engine.connect() as conn:
                        conn.execute(
                            text('''
                                INSERT INTO active_positions (ticker, strategy, entry_date, budget_price, actual_fill_price, shares, stop_loss, target_1, target_2, notes)
                                VALUES (:t, :s, :ed, :bp, :afp, :sh, :sl, :t1, :t2, :n)
                            '''),
                            {
                                "t": calc_ticker, "s": scan_strategy, "ed": str(entry_date_input),
                                "bp": budget_price_val, "afp": actual_fill_price_input, "sh": final_shares,
                                "sl": stop_val, "t1": t1_val, "t2": t2_val, "n": trade_notes
                            }
                        )
                        pos_cost = actual_fill_price_input * final_shares
                        new_cash = max(0.0, avail_cash - pos_cost)
                        conn.execute(
                            text('''
                                INSERT INTO account_snapshots (snapshot_date, cash_balance, position_value, total_account_value, notes)
                                VALUES (:sd, :cb, :pv, :tav, :n)
                            '''),
                            {
                                "sd": str(entry_date_input), "cb": new_cash, "pv": pos_cost,
                                "tav": acc_balance, "n": f"Opened Position: {calc_ticker}"
                            }
                        )
                        conn.commit()
                    st.success(f"✅ Position for {calc_ticker} logged successfully to Supabase cloud!")

# ==========================================
# PAGE 2: ACTIVE PORTFOLIO MANAGER
# ==========================================
elif app_mode == "💼 Active Portfolio Manager":
    st.subheader("💼 Active Position Management Core")
    
    df_active = pd.read_sql("SELECT * FROM active_positions ORDER BY id DESC", con=engine)
    
    if df_active.empty:
        st.info("No active positions tracked. Open positions using the AlphaScan Engine scanner.")
    else:
        st.write("### **Live Open Positions (Fully Editable Log)**")
        df_active['Fill_Slippage_$'] = df_active['actual_fill_price'] - df_active['budget_price']
        
        edited_df = st.data_editor(
            df_active[['id', 'ticker', 'strategy', 'entry_date', 'budget_price', 'actual_fill_price', 'Fill_Slippage_$', 'shares', 'stop_loss', 'target_1', 'target_2', 'notes']],
            disabled=['id', 'Fill_Slippage_$'],
            use_container_width=True,
            key="active_editor_all"
        )
        
        if st.button("💾 Save Active Position Edits", type="primary"):
            with engine.connect() as conn:
                for idx, row in edited_df.iterrows():
                    conn.execute(
                        text('''
                            UPDATE active_positions 
                            SET ticker = :t, strategy = :s, entry_date = :ed, budget_price = :bp, 
                                actual_fill_price = :afp, shares = :sh, stop_loss = :sl, 
                                target_1 = :t1, target_2 = :t2, notes = :n
                            WHERE id = :id
                        '''),
                        {
                            "t": row['ticker'], "s": row['strategy'], "ed": str(row['entry_date']),
                            "bp": float(row['budget_price']), "afp": float(row['actual_fill_price']),
                            "sh": int(row['shares']), "sl": float(row['stop_loss']),
                            "t1": str(row['target_1']), "t2": str(row['target_2']),
                            "n": row['notes'], "id": int(row['id'])
                        }
                    )
                conn.commit()
            st.success("✅ All position modifications updated and saved!")
            st.rerun()

        st.write("---")
        st.subheader("🚪 Exit & Close Position")
        
        pos_id_to_close = st.selectbox("Select Active Position to Close:", df_active['id'].tolist(), format_func=lambda x: f"ID #{x} - {df_active[df_active['id']==x]['ticker'].values[0]} ({df_active[df_active['id']==x]['shares'].values[0]} Shares)")
        selected_pos = df_active[df_active['id'] == pos_id_to_close].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        exit_date = c1.date_input("Exit Date", value=datetime.today())
        exit_price = c2.number_input("Broker Exit Fill Price ($)", min_value=0.01, value=float(selected_pos['actual_fill_price']), step=0.01)
        
        try:
            entry_dt = datetime.strptime(str(selected_pos['entry_date']), "%Y-%m-%d").date()
        except Exception:
            entry_dt = datetime.today().date()
            
        holding_days = max((exit_date - entry_dt).days, 1)
        
        shares = int(selected_pos['shares'])
        actual_fill_price = float(selected_pos['actual_fill_price'])
        budget_price = float(selected_pos['budget_price'])
        
        realized_pnl = round((exit_price - actual_fill_price) * shares, 2)
        pnl_pct = round(((exit_price - actual_fill_price) / actual_fill_price) * 100, 2)
        slippage = round(actual_fill_price - budget_price, 2)
        
        c3.metric("Projected Realized P&L", f"${realized_pnl:,.2f}", f"{pnl_pct}%")
        
        if st.button("🔒 Confirm Exit & Transfer to Trader Journal", type="primary"):
            with engine.connect() as conn:
                conn.execute(
                    text('''
                        INSERT INTO trade_journal (ticker, strategy, entry_date, exit_date, holding_days, budget_price, actual_fill_price, exit_price, shares, realized_pnl, pnl_pct, slippage, notes)
                        VALUES (:t, :s, :ed, :xd, :hd, :bp, :afp, :xp, :sh, :pnl, :pnl_p, :slip, :n)
                    '''),
                    {
                        "t": selected_pos['ticker'], "s": selected_pos['strategy'], "ed": str(selected_pos['entry_date']),
                        "xd": str(exit_date), "hd": holding_days, "bp": budget_price,
                        "afp": actual_fill_price, "xp": exit_price, "sh": shares,
                        "pnl": realized_pnl, "pnl_p": pnl_pct, "slip": slippage, "n": selected_pos['notes']
                    }
                )
                conn.execute(text("DELETE FROM active_positions WHERE id = :id"), {"id": int(pos_id_to_close)})
                conn.commit()
            st.success(f"Position {selected_pos['ticker']} closed and committed to Journal!")
            st.rerun()

# ==========================================
# PAGE 3: TRADE JOURNAL & ANALYTICS (PRO DASHBOARD)
# ==========================================
else:
    st.subheader("📖 Modern Trader Analytics Dashboard")
    
    df_journal = pd.read_sql("SELECT * FROM trade_journal ORDER BY id DESC", con=engine)
    df_snapshots = pd.read_sql("SELECT * FROM account_snapshots ORDER BY id DESC", con=engine)
    
    with st.expander("📸 Record Balance Snapshot", expanded=False):
        c1, c2, c3 = st.columns(3)
        snap_cash = c1.number_input("Liquid Cash ($)", min_value=0.0, value=5000.0, step=500.0)
        snap_positions = c2.number_input("Active Position Value ($)", min_value=0.0, value=5000.0, step=500.0)
        snap_notes = c3.text_input("Snapshot Context Note", value="Periodic Balance Check")
        
        if st.button("💾 Record Balance Snapshot"):
            with engine.connect() as conn:
                conn.execute(
                    text('''
                        INSERT INTO account_snapshots (snapshot_date, cash_balance, position_value, total_account_value, notes)
                        VALUES (:sd, :cb, :pv, :tav, :n)
                    '''),
                    {
                        "sd": str(datetime.today().date()), "cb": snap_cash,
                        "pv": snap_positions, "tav": snap_cash + snap_positions, "n": snap_notes
                    }
                )
                conn.commit()
            st.success("Snapshot saved!")
            st.rerun()

    total_trades = len(df_journal)
    wins = len(df_journal[df_journal['realized_pnl'] > 0]) if not df_journal.empty else 0
    losses = len(df_journal[df_journal['realized_pnl'] < 0]) if not df_journal.empty else 0
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0.0
    
    avg_win = df_journal[df_journal['realized_pnl'] > 0]['realized_pnl'].mean() if wins > 0 else 0.0
    avg_loss = abs(df_journal[df_journal['realized_pnl'] < 0]['realized_pnl'].mean()) if losses > 0 else 1.0
    win_loss_ratio = round(avg_win / avg_loss, 2) if avg_loss > 0 else avg_win

    net_pnl = df_journal['realized_pnl'].sum() if not df_journal.empty else 0.0

    dash_col1, dash_col2, dash_col3, dash_col4 = st.columns([1, 1.2, 1, 1.2])
    
    with dash_col1:
        st.markdown("#### **Winstreak & Volume**")
        st.metric("Total Trades Logged", f"{total_trades} Trades", f"{wins} Wins / {losses} Losses")
        st.metric("Avg Execution Slippage", f"${df_journal['slippage'].mean():.2f}" if not df_journal.empty else "$0.00")

    with dash_col2:
        st.markdown("#### **Winrate Gauge**")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=win_rate,
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#10B981"},
                'steps': [
                    {'range': [0, 50], 'color': "#EF4444"},
                    {'range': [50, 100], 'color': "#1E293B"}
                ]
            }
        ))
        fig_gauge.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10), template="plotly_dark")
        st.plotly_chart(fig_gauge, use_container_width=True)

    with dash_col3:
        st.markdown("#### **Win / Loss Ratio**")
        st.metric("Avg Win / Avg Loss Ratio", f"{win_loss_ratio:.2f}")
        st.metric("Net Realized P&L", f"${net_pnl:,.2f}")

    with dash_col4:
        st.markdown("#### **Strategy Radar Score**")
        categories = ['Win Rate', 'Profit Factor', 'Avg Days', 'Return %']
        fig_radar = go.Figure(go.Scatterpolar(
            r=[win_rate, min(win_loss_ratio * 20, 100), 50, min(max(net_pnl / 100, 0), 100)],
            theta=categories,
            fill='toself',
            line_color='#3B82F6'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            showlegend=False, height=180, margin=dict(l=20, r=20, t=10, b=10), template="plotly_dark"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.write("---")

    mid_col1, mid_col2 = st.columns([1, 1.2])

    with mid_col1:
        st.markdown("### 📅 **Monthly Trading Calendar Heatmap**")
        if not df_journal.empty:
            df_journal['exit_dt'] = pd.to_datetime(df_journal['exit_date'])
            df_journal['Day'] = df_journal['exit_dt'].dt.day
            calendar_data = df_journal.groupby('Day')['realized_pnl'].sum().reset_index()
            
            fig_cal = px.bar(calendar_data, x='Day', y='realized_pnl', title="PnL Distribution by Day of Month ($)", color='realized_pnl', color_continuous_scale=['#EF4444', '#10B981'])
            fig_cal.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_cal, use_container_width=True)
        else:
            st.info("Log trades in the journal to view trading calendar heatmap.")

    with mid_col2:
        st.markdown("### 📈 **Total Portfolio Balance & Liquidity**")
        if not df_snapshots.empty:
            df_snapshots['snapshot_date_dt'] = pd.to_datetime(df_snapshots['snapshot_date'])
            df_snaps_sorted = df_snapshots.sort_values('snapshot_date_dt')
            
            fig_area = go.Figure()
            fig_area.add_trace(go.Scatter(
                x=df_snaps_sorted['snapshot_date_dt'], y=df_snaps_sorted['cash_balance'],
                name="Liquid Cash ($)", mode='lines', stackgroup='one',
                line=dict(width=0.5, color='#3B82F6'), fillcolor='rgba(59, 130, 246, 0.4)'
            ))
            fig_area.add_trace(go.Scatter(
                x=df_snaps_sorted['snapshot_date_dt'], y=df_snaps_sorted['position_value'],
                name="Active Positions ($)", mode='lines', stackgroup='one',
                line=dict(width=0.5, color='#F59E0B'), fillcolor='rgba(245, 158, 11, 0.4)'
            ))
            fig_area.add_trace(go.Scatter(
                x=df_snaps_sorted['snapshot_date_dt'], y=df_snaps_sorted['total_account_value'],
                name="Total Balance ($)", mode='lines+markers',
                line=dict(color='#10B981', width=3)
            ))
            fig_area.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("Log balance snapshots to render portfolio area chart.")

    st.write("---")
    st.markdown("### 📜 **Historical Trade Journal Records**")
    st.dataframe(df_journal, use_container_width=True)
