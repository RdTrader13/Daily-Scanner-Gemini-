import sqlite3
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ==========================================
# --- PAGE CONFIGURATION & APP SETTINGS ---
# ==========================================
st.set_page_config(
    page_title="AlphaScan Execution Suite - Complete Enterprise Workspace",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# --- SECTION 1: PRIVATE APP SECURITY ---
# ==========================================
def check_password():
    """Returns True if the user has entered the correct application passcode."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("### 🔐 Private Access Required")
        user_password = st.text_input(
            "Enter Passcode:", type="password", key="app_pass_input"
        )

        APP_PASSCODE = st.secrets.get("APP_PASSCODE", "MyTradingApp2026!")

        if st.button("Unlock Dashboard"):
            if user_password == APP_PASSCODE:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect Passcode")
        st.stop()


check_password()


# ==========================================
# --- SECTION 2: NAVIGATION & THEME ENGINE ---
# ==========================================
st.sidebar.title("📌 Navigation")
app_mode = st.sidebar.radio(
    "Go to Page:",
    [
        "⚡ AlphaScan Engine",
    ],
)

theme_choice = st.sidebar.selectbox(
    "Select UI Theme Workspace:",
    [
        "Quantum Dark Core",
        "Art Deco (Turn of the Century)",
        "Standard Dark Mode",
        "Standard Light Mode",
    ],
)

if theme_choice == "Quantum Dark Core":
    bg_app, text_main, border_color, metric_bg, font_family = (
        "#0B0F19",
        "#F8FAFC",
        "#10B981",
        "#1E293B",
        "'Inter', sans-serif",
    )
    header_html = (
        '<div style="background-color: #1E293B; padding: 24px; border-radius:'
        " 12px; border-left: 5px solid #10B981; margin-bottom: 25px;'><h3>⚡"
        " AlphaScan Execution Suite</h3></div>"
    )
elif theme_choice == "Art Deco (Turn of the Century)":
    bg_app, text_main, border_color, metric_bg, font_family = (
        "#11161B",
        "#F3EAD3",
        "#C5A059",
        "#1A2129",
        "'Playfair Display', serif",
    )
    header_html = (
        '<div style="background-color: #1C232B; padding: 24px; border-radius:'
        " 4px; border: 2px solid #C5A059; border-style: double; border-width:"
        ' 6px; text-align: center; margin-bottom: 25px;"><h3>THE TECHNICAL'
        " MOMENTUM CHRONICLE</h3></div>"
    )
elif theme_choice == "Standard Dark Mode":
    bg_app, text_main, border_color, metric_bg, font_family = (
        "#0E1117",
        "#FFFFFF",
        "#30363D",
        "#161B22",
        "sans-serif",
    )
    header_html = "<div><h1>📊 Dark Mode Engine</h1></div>"
else:
    bg_app, text_main, border_color, metric_bg, font_family = (
        "#FFFFFF",
        "#1F2937",
        "#E5E7EB",
        "#F3F4F6",
        "sans-serif",
    )
    header_html = "<div><h1>📊 Light Mode Engine</h1></div>"

css_payload = f"<style>.stApp {{ background-color: {bg_app} !important; color: {text_main} !important; }} div[data-testid='stMetric'] {{ background-color: {metric_bg} !important; border: 1px solid {border_color} !important; border-radius: 10px !important; }} h1, h2, h3, p {{ font-family: {font_family} !important; color: {text_main} !important; }}</style>"
st.html(css_payload)
st.html(header_html)


# ==========================================
# --- SECTION 3: MATHEMATICAL INDICATOR SUITE ---
# ==========================================
def calculate_wma(series, length):
    weights = np.arange(1, length + 1)
    return series.rolling(length).apply(
        lambda w: np.dot(w, weights) / weights.sum(), raw=True
    )


def calculate_hma(series, length=20):
    half_length = int(length / 2)
    sqrt_length = int(np.round(np.sqrt(length)))
    wma_half = calculate_wma(series, half_length)
    wma_full = calculate_wma(series, length)
    raw_hma = 2 * wma_half - wma_full
    return calculate_wma(raw_hma, sqrt_length)


def calculate_alma(series, length=34, offset=0.85, sigma=6.0):
    m = int(offset * (length - 1))
    s = length / sigma
    weights = np.exp(-((np.arange(length) - m) ** 2) / (2 * s**2))
    weights /= weights.sum()
    return series.rolling(window=length).apply(
        lambda x: np.dot(x, weights[::-1]), raw=True
    )


def calculate_mhls_and_volatility(df):
    if len(df) < 43:
        return 0, 0.0, 0.0, 0.0

    current_close = df["Close"].iloc[-1]
    lookbacks = [5, 10, 21, 42]
    mhls = 0

    for lb in lookbacks:
        past_close = df["Close"].iloc[-(lb + 1)]
        if current_close > past_close:
            mhls += 1
        elif current_close < past_close:
            mhls -= 1

    weight_map = {4: 1.0, 3: 0.75, 2: 0.50, 1: 0.25}
    score_weight = weight_map.get(mhls, 0.0)

    daily_pct_change = df["Close"].pct_change().abs()
    mean_30d_pct_move = daily_pct_change.iloc[-30:].mean()
    annualized_volatility = mean_30d_pct_move * np.sqrt(365)

    return mhls, score_weight, round(score_weight * 100, 0), annualized_volatility


# ==========================================
# --- SECTION 4: ALPHASCAN CORE ENGINE ---
# ==========================================
if app_mode == "⚡ AlphaScan Engine":
    st.sidebar.header("🎯 Strategy Mode")
    scan_strategy = st.sidebar.radio(
        "Select Scanning Framework:",
        [
            "Universal 4-HMA Trend-Following",
            "Large Cap Core Matrix",
            "Squeeze / Penny Stock Multiplier",
            "Channel Yield & Dividend Engine",
            "Alma Targets & Turtle Pyramiding",
        ],
        key="strategy_choice",
    )

    FULL_SP500 = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "BRK-B", "LLY", "AVGO",
        "JPM", "TSLA", "WMT", "XOM", "UNH", "V", "PG", "MA", "ORCL", "COST", "HD",
        "CVX", "BAC", "ABBV", "NFLX", "KO", "MRK", "AMD", "PEP", "ADBE", "LIN", "TMO",
        "WFC", "CSCO", "ACN", "MCD", "DIS", "ABT", "GE", "INTU", "QCOM", "TXN", "CAT",
        "AMAT", "PM", "VZ", "AXP", "UBER", "PFE", "IBM", "MS", "LOW", "UNP", "AMGN",
        "GS", "NOW", "SPGI", "LRCX", "SYK", "RTX", "HON", "BKNG", "T", "BLK", "TJX",
        "C", "ADP", "SBUX", "COP", "VRTX", "PLTR", "MDLZ", "BA", "BMY", "PANW", "SCHW",
        "ADI", "FI", "CB", "DE", "MMC", "LMT", "TMUS", "ECL", "GEV", "INTC", "SO",
        "GILD", "NKE", "MU", "MO", "PGR", "UPS", "SHW", "DUK", "TT"
    ]
    DOW_30 = [
        "AAPL", "AMZN", "AXP", "BA", "BAC", "CAT", "CRM", "CSCO", "CVX", "DIS", "HD",
        "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE",
        "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"
    ]
    TOP_ETFS = [
        "BITO", "TSLL", "SNXX", "TQQQ", "NVD", "MSTU", "SQQQ", "SOXL", "MUU", "SOXS",
        "DRAM", "SPY", "SPDN", "QQQ", "IBIT", "PLTD", "TSLG", "XLF", "XLE", "DAMD",
        "HYG", "ETHA", "EEM", "LQD", "FXI", "KORU", "TLT", "IWM", "KWEB", "TSDD",
        "EWZ", "TZA", "EWY", "NOWL", "GDX", "SCHD", "BTCZ", "QID", "CONL", "SGOV",
        "XLU", "NVDL", "SLV", "MSTZ", "IONZ", "RWM", "IGV", "RKLZ", "MUD", "KRE",
        "AMZD", "RGTZ", "OKLL", "IEMG", "EFA", "SCHX", "SPXS", "SPYM", "XLK", "XLP",
        "SMH", "XLB", "AVS", "VEA", "USHY", "MULL", "XLV", "SNDQ", "SOXX", "BIL",
        "SCHG", "RSP", "IEFA", "SPXU", "VXX", "AAPD", "SCO", "LABD", "BMNU", "XBI",
        "SH", "NVDX", "PSLV", "SCHB", "VCIT", "BITX", "PSQ", "VWO", "BKLN", "AGG",
        "GOVT", "TSLQ", "MSFU", "XLY", "UVXY", "BND", "VOO", "IVV", "SCHF", "UNG"
    ]
    DEFAULT_SPECULATIVE = [
        "SOUN", "BBAI", "LCID", "GRND", "NKLA", "NIO", "OPEN", "SOFI", "PTON", "MARA",
        "RIOT", "CLSK", "HUT", "CLOV", "MQ", "NXDR"
    ]
    DEFAULT_DIVIDEND = ["NVDY", "CONY", "TSLY", "AMZY", "QDTE", "XDTE", "JEPQ", "SCHD"]
    DEFAULT_ALMA = ["SPY", "QQQ", "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "BTC-USD"]

    max_price_filter = None

    if scan_strategy == "Squeeze / Penny Stock Multiplier":
        st.sidebar.header("📁 Squeeze Asset Array")
        penny_input = st.sidebar.text_area(
            "Speculative Screener Nodes:",
            ", ".join(DEFAULT_SPECULATIVE),
            key="penny_input_key",
        )
        tickers = list(dict.fromkeys([t.strip().upper() for t in penny_input.split(",") if t.strip()]))
        max_price_filter = 15.00
    elif scan_strategy == "Channel Yield & Dividend Engine":
        st.sidebar.header("📁 High-Yield Income Array")
        div_input = st.sidebar.text_area(
            "Income Screener Nodes:",
            ", ".join(DEFAULT_DIVIDEND),
            key="div_input_key",
        )
        tickers = list(dict.fromkeys([t.strip().upper() for t in div_input.split(",") if t.strip()]))
        max_price_filter = None
    elif scan_strategy == "Alma Targets & Turtle Pyramiding":
        st.sidebar.header("📁 Alma Trend Array")
        alma_input = st.sidebar.text_area(
            "Alma Screener Nodes:",
            ", ".join(DEFAULT_ALMA),
            key="alma_input_key",
        )
        tickers = list(dict.fromkeys([t.strip().upper() for t in alma_input.split(",") if t.strip()]))
        max_price_filter = None
    else:
        st.sidebar.header("📁 Core Matrix Framework")
        source_type = st.sidebar.radio(
            "Data Source Configuration:",
            [
                "Custom Watchlist",
                "Top ETFs Array",
                "Full S&P 500 Index",
                "Dow Jones 30",
            ],
            key="source_type_key",
        )
        if source_type == "Custom Watchlist":
            default_watchlist = "GDX, AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL, LLY, JPM"
            watchlist_input = st.sidebar.text_area(
                "Edit Watchlist Arrays:", default_watchlist, key="watchlist_input_key"
            )
            tickers = list(dict.fromkeys([t.strip().upper() for t in watchlist_input.split(",") if t.strip()]))
        elif source_type == "Top ETFs Array":
            raw_etfs = list(dict.fromkeys(TOP_ETFS))
            max_scan = st.sidebar.slider("ETF Scan Depth:", 5, len(raw_etfs), len(raw_etfs), key="etf_depth")
            tickers = raw_etfs[:max_scan]
        elif source_type == "Full S&P 500 Index":
            raw_tickers = list(dict.fromkeys(FULL_SP500))
            max_scan = st.sidebar.slider("S&P 500 Scan Depth:", 10, len(raw_tickers), 50, step=5, key="sp_depth")
            tickers = raw_tickers[:max_scan]
        else:
            tickers = list(dict.fromkeys(DOW_30))
        max_price_filter = None

    st.sidebar.write("---")
    st.sidebar.header("⚙️ Risk Parameters")

    if scan_strategy == "Alma Targets & Turtle Pyramiding":
        alma_len = st.sidebar.slider("ALMA Length", 5, 100, 34, key="alma_len_key")
        alma_offset = st.sidebar.slider("ALMA Offset", 0.0, 1.0, 0.85, 0.05, key="alma_offset_key")
        alma_sigma = st.sidebar.slider("ALMA Sigma", 1.0, 15.0, 6.0, 0.5, key="alma_sigma_key")
        dev_len = st.sidebar.slider("Deviation Length", 5, 100, 34, key="dev_len_key")
        dev_mult = st.sidebar.slider("Trend Confirmation Multiplier", 0.1, 3.0, 0.65, 0.05, key="dev_mult_key")
        slope_len = st.sidebar.slider("Slope Length", 1, 10, 3, key="slope_len_key")
        slope_min = st.sidebar.slider("Minimum Slope", 0.0, 1.0, 0.08, 0.01, key="slope_min_key")
        atr_period = st.sidebar.slider("ATR Length", 5, 30, 14, key="alma_atr_key")
        stop_lookback = st.sidebar.slider("Stop Structure Lookback", 3, 50, 12, key="stop_lb_key")
        min_stop_atr = st.sidebar.slider("Minimum Stop ATR", 0.25, 3.0, 0.75, 0.05, key="min_stop_atr_key")
        max_stop_atr = st.sidebar.slider("Maximum Stop ATR", 1.0, 8.0, 3.0, 0.25, key="max_stop_atr_key")
        max_pyramid_units = st.sidebar.slider("Max Pyramid Units (N)", 1, 5, 4, key="pyramid_units_key")
        pyramid_spacing_r = st.sidebar.slider("Pyramid Spacing (R-Multiple)", 0.25, 1.0, 0.5, 0.05, key="pyramid_space_key")
        exit_style = "Hybrid Scale-Out (Fixed Targets + Trail)"
        target_1_multiplier, target_2_multiplier = 1.5, 3.0
        risk_multiplier = 1.5
    elif scan_strategy == "Channel Yield & Dividend Engine":
        hma_lookback_period = st.sidebar.slider("HMA Lookback Period", 5, 50, 20, key="hma_div_period_key")
        min_mom_threshold = st.sidebar.slider("Min Multi-Horizon Score for Buy", -4, 4, 2, key="div_mom_thresh")
        buy_channel_max = st.sidebar.slider("Max 60D Channel Range for Buy (%)", 5, 35, 15, key="div_buy_chan")
        sell_channel_min = st.sidebar.slider("Min 60D Channel Range for Exit (%)", 40, 90, 50, key="div_sell_chan")
        atr_period = 14
        exit_style = "Hybrid Scale-Out (Fixed Targets + Trail)"
        target_1_multiplier, target_2_multiplier = 1.5, 3.0
        risk_multiplier = 1.5
    else:
        atr_period = st.sidebar.slider("ATR Lookback", 5, 30, 14, key="atr_period_key")

        if scan_strategy == "Universal 4-HMA Trend-Following":
            hma_trigger_mode = st.sidebar.radio(
                "Hull Cross Confirmation Logic:",
                ["Execute on Cross Bar Close", "Require Next-Day Confirmation Close"],
                key="hma_trigger_mode_key",
            )
            hma_stop_mode = st.sidebar.selectbox(
                "HMA Stop-Loss Mode:",
                ["Most Recent Red HMA Low", "2nd Most Recent Red HMA Low", "ATR Multiplier"],
                key="hma_stop_mode_key",
            )
            risk_multiplier = (
                st.sidebar.slider("Risk Envelope Scalar (ATR)", 0.5, 5.0, 1.5, step=0.1, key="risk_multiplier_key")
                if hma_stop_mode == "ATR Multiplier"
                else 1.5
            )
            st.sidebar.write("---")
            exit_style = st.sidebar.radio(
                "Select Exit Methodology:",
                ["Hybrid Scale-Out (Fixed Targets + Trail)", "Pure Trailing Exit (No Fixed Targets)"],
                key="exit_style_key",
            )
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

    def scan_ticker(ticker_symbol):
        try:
            yf_ticker = yf.Ticker(ticker_symbol)
            df = yf_ticker.history(period="250d", auto_adjust=False)
            if df.empty or len(df) < 60:
                return None

            df["SMA_50"] = df["Close"].rolling(window=50).mean()
            df["SMA_200"] = df["Close"].rolling(window=200).mean()
            df["HMA_Open"] = calculate_hma(df["Open"], 20)
            df["HMA_Close"] = calculate_hma(df["Close"], 20)
            df["HMA_High"] = calculate_hma(df["High"], 20)
            df["HMA_Low"] = calculate_hma(df["Low"], 20)
            df["EMA_9"] = df["Close"].ewm(span=9, adjust=False).mean()
            df["EMA_21"] = df["Close"].ewm(span=21, adjust=False).mean()

            delta = df["Close"].diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)
            rs = gain.rolling(14).mean() / (loss.rolling(14).mean() + 1e-10)
            df["RSI"] = 100 - (100 / (1 + rs))

            df["Vol_Avg"] = df["Volume"].rolling(window=10).mean()
            df["Relative_Volume"] = df["Volume"] / (df["Vol_Avg"] + 1e-10)

            high_low = df["High"] - df["Low"]
            high_close = np.abs(df["High"] - df["Close"].shift())
            low_close = np.abs(df["Low"] - df["Close"].shift())
            df["ATR"] = (
                pd.concat([high_low, high_close, low_close], axis=1)
                .max(axis=1)
                .rolling(atr_period)
                .mean()
            )

            latest, prev = df.iloc[-1], df.iloc[-2]
            price = latest["Close"]
            
            if max_price_filter is not None and price > max_price_filter:
                return None

            mhls, score_weight_float, score_weight_pct, ann_vol = (
                calculate_mhls_and_volatility(df)
            )

            atr = latest["ATR"]
            risk_amount = risk_multiplier * atr

            if scan_strategy == "Alma Targets & Turtle Pyramiding":
                df["ALMA"] = calculate_alma(df["Close"], length=alma_len, offset=alma_offset, sigma=alma_sigma)
                df["Dev"] = df["Close"].rolling(window=dev_len).std()
                df["ALMA_Prev"] = df["ALMA"].shift(slope_len)
                df["SlopeScore"] = np.where(df["ATR"] > 0, (df["ALMA"] - df["ALMA_Prev"]) / df["ATR"], 0.0)
                
                df["UpperConfirm"] = df["ALMA"] + df["Dev"] * dev_mult
                df["LowerConfirm"] = df["ALMA"] - df["Dev"] * dev_mult

                latest_alma = df["ALMA"].iloc[-1]
                latest_slope = df["SlopeScore"].iloc[-1]
                latest_upper = df["UpperConfirm"].iloc[-1]
                latest_lower = df["LowerConfirm"].iloc[-1]

                bull_setup = latest_slope > slope_min and price > latest_upper
                bear_setup = latest_slope < -slope_min and price < latest_lower

                if bull_setup:
                    signal = "🟢 BULLISH ALMA SETUP"
                elif bear_setup:
                    signal = "🔴 BEARISH ALMA SETUP"
                else:
                    signal = "🟡 ALMA CONSOLIDATING"

                recent_low = df["Low"].iloc[-stop_lookback:].min()
                recent_high = df["High"].iloc[-stop_lookback:].max()

                raw_risk = price - recent_low if bull_setup or price >= latest_alma else recent_high - price
                min_risk = atr * min_stop_atr
                max_risk = atr * max_stop_atr
                risk_dist = min(max(raw_risk, min_risk), max_risk)

                stop_val = price - risk_dist if (bull_setup or signal != "🔴 BEARISH ALMA SETUP") else price + risk_dist
                
                t1_val = round(price + risk_dist * 1.0, 2)
                t2_val = round(price + risk_dist * 2.0, 2)
                t3_val = round(price + risk_dist * 3.0, 2)
                t4_val = round(price + risk_dist * 4.0, 2)

                return {
                    "Ticker": ticker_symbol,
                    "Price": round(price, 2),
                    "ALMA": round(latest_alma, 2),
                    "Slope Score": round(latest_slope, 3),
                    "ATR ($)": round(atr, 2),
                    "Signal": signal,
                    "Calculated Stop": round(stop_val, 2),
                    "Stop Type": "Structure + ATR Clamp",
                    "Target 1": t1_val,
                    "Target 2": t2_val,
                    "Target 3": t3_val,
                    "Target 4": t4_val,
                    "Risk Dist": round(risk_dist, 2),
                    "MHLS": mhls,
                    "Score Weight": f"{int(score_weight_pct)}%",
                    "Score Weight Raw": score_weight_float,
                    "Ann Volatility %": round(ann_vol * 100, 2),
                    "Ann Volatility Raw": ann_vol,
                    "50 SMA": round(latest["SMA_50"], 2),
                    "200 SMA": round(latest["SMA_200"], 2),
                    "RSI": round(latest["RSI"], 1),
                }

            elif scan_strategy == "Channel Yield & Dividend Engine":
                trailing_div_rate = 0.0
                try:
                    div_history = yf_ticker.dividends
                    if not div_history.empty:
                        one_year_ago = datetime.now() - timedelta(days=365)
                        recent_divs = div_history[div_history.index >= one_year_ago]
                        trailing_div_rate = float(recent_divs.sum())
                except Exception:
                    pass

                if price > 0 and trailing_div_rate > 0:
                    custom_value_score = price / (trailing_div_rate * 10)
                else:
                    custom_value_score = np.nan

                hist_60d = df.tail(60)
                high_60d = hist_60d["High"].max()
                low_60d = hist_60d["Low"].min()
                channel_range_pct = ((price - low_60d) / (high_60d - low_60d)) * 100 if high_60d != low_60d else 50.0

                hma_custom = calculate_hma(df["Close"], length=20)
                is_sloping_up = (hma_custom.iloc[-1] - hma_custom.iloc[-2]) > 0
                hma_slope_indicator = "📈 Sloping UP" if is_sloping_up else "📉 Sloping DOWN"

                if mhls >= min_mom_threshold and channel_range_pct <= buy_channel_max and is_sloping_up:
                    signal = "🟢 BUY / ALLOCATE"
                elif channel_range_pct >= sell_channel_min and not is_sloping_up:
                    signal = "🔴 EXIT / TRIM"
                elif mhls <= -2:
                    signal = "⚠️ STRUCTURAL DOWN"
                else:
                    signal = "🟡 HOLD / WATCH"

                buy_max_p = low_60d + (high_60d - low_60d) * (buy_channel_max / 100.0)
                sell_min_p = low_60d + (high_60d - low_60d) * (sell_channel_min / 100.0)

                return {
                    "Ticker": ticker_symbol,
                    "Last Close Price": round(price, 2),
                    "Dividend Per Share": round(trailing_div_rate, 2),
                    "Custom Value Score": round(custom_value_score, 3) if not np.isnan(custom_value_score) else "N/A",
                    "Buy Range": f"${low_60d:.2f} - ${buy_max_p:.2f}",
                    "Hold Range": f"${buy_max_p:.2f} - ${sell_min_p:.2f}",
                    "Sell Range": f"${sell_min_p:.2f} - ${high_60d:.2f}",
                    "HMA": round(hma_custom.iloc[-1], 2),
                    "HMA Trend": hma_slope_indicator,
                    "MHLS": mhls,
                    "Signal": signal,
                    "Price": round(price, 2),
                    "Score Weight": f"{int(score_weight_pct)}%",
                    "Score Weight Raw": score_weight_float,
                    "Ann Volatility %": round(ann_vol * 100, 2),
                    "Ann Volatility Raw": ann_vol,
                    "Calculated Stop": round(low_60d, 2),
                    "Stop Type": "60D Channel Low",
                    "Target 1": round(buy_max_p, 2),
                    "Target 2": round(high_60d, 2),
                    "50 SMA": round(latest["SMA_50"], 2),
                    "200 SMA": round(latest["SMA_200"], 2),
                    "RSI": round(latest["RSI"], 1),
                }

            ema_pinch = abs(latest["EMA_9"] - latest["EMA_21"]) / latest["EMA_21"]
            vol_spike = latest["Relative_Volume"]
            is_coiling = "CRITICAL SQUEEZE" if (ema_pinch < 0.015 and vol_spike > 1.2) else ("Yes" if ema_pinch < 0.015 else "No")
            bullish_cross = (prev["EMA_9"] <= prev["EMA_21"]) and (latest["EMA_9"] > latest["EMA_21"])
            bearish_cross = (prev["EMA_9"] >= prev["EMA_21"]) and (latest["EMA_9"] < latest["EMA_21"])

            if scan_strategy == "Universal 4-HMA Trend-Following":
                above_smas = (price > latest["SMA_50"]) and (price > latest["SMA_200"])
                recent_cross = (prev["HMA_Close"] <= prev["HMA_Open"]) and (latest["HMA_Close"] > latest["HMA_Open"])
                hma_close_sloping_up = latest["HMA_Close"] > prev["HMA_Close"]
                closed_above_white = price > latest["HMA_Close"]

                stop = price - risk_amount
                stop_type = "ATR Envelope"
                t1_val = round(price + (risk_amount * target_1_multiplier), 2)
                t2_val = round(price + (risk_amount * target_2_multiplier), 2)

                if above_smas and recent_cross and hma_close_sloping_up and closed_above_white:
                    signal = "🟢 BUY ENTRY"
                elif price < stop:
                    signal = "🔴 EXIT TRIGGER"
                else:
                    signal = "🟡 BULLISH TREND"

            elif scan_strategy == "Squeeze / Penny Stock Multiplier":
                stop = price - risk_amount
                stop_type = "ATR Envelope"
                t1_val = round(price + (risk_amount * target_1_multiplier), 2)
                t2_val = round(price + (risk_amount * target_2_multiplier), 2)
                signal = "🟢 EXPANSION TRIGGER" if bullish_cross else "⚪ MONITOR COILING"
            else:
                stop_type = "ATR Envelope"
                if bullish_cross and latest["RSI"] > 40:
                    signal, stop = "🟢 BUY TRIGGER", price - risk_amount
                    t1_val, t2_val = round(price + (risk_amount * target_1_multiplier), 2), round(price + (risk_amount * target_2_multiplier), 2)
                elif bearish_cross:
                    signal, stop = "🔴 SELL TRIGGER", price + risk_amount
                    t1_val, t2_val = round(price - (risk_amount * target_1_multiplier), 2), round(price - (risk_amount * target_2_multiplier), 2)
                else:
                    signal, stop = "🟡 HOLD (Bullish)", price - risk_amount
                    t1_val, t2_val = round(price + (risk_amount * target_1_multiplier), 2), round(price + (risk_amount * target_2_multiplier), 2)

            return {
                "Ticker": ticker_symbol,
                "Price": round(price, 2),
                "MHLS": mhls,
                "Score Weight": f"{int(score_weight_pct)}%",
                "Score Weight Raw": score_weight_float,
                "Ann Volatility %": round(ann_vol * 100, 2),
                "Ann Volatility Raw": ann_vol,
                "Signal": signal,
                "Calculated Stop": round(stop, 2),
                "Stop Type": stop_type,
                "Target 1": t1_val,
                "Target 2": t2_val,
                "50 SMA": round(latest["SMA_50"], 2),
                "200 SMA": round(latest["SMA_200"], 2),
                "RSI": round(latest["RSI"], 1),
                "Compression Status": is_coiling,
            }
        except Exception:
            return None

    if st.button(
        "🔥 Execute System Framework Architecture Scan",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("Processing framework algorithms..."):
            results = [res for t in tickers if (res := scan_ticker(t)) is not None]
            if results:
                st.session_state["scan_data"] = pd.DataFrame(results)
                st.session_state["total_nodes"] = len(tickers)
                st.session_state["run_success"] = True
            else:
                st.error("No valid matrix node data found.")

    if st.session_state.get("run_success"):
        scan_df = st.session_state["scan_data"]
        total_nodes = st.session_state.get("total_nodes", len(scan_df))
        buy_hits = len(scan_df[scan_df["Signal"].str.contains("🟢")])
        exit_hits = len(scan_df[scan_df["Signal"].str.contains("🔴")])
        hold_hits = len(scan_df[scan_df["Signal"].str.contains("🟡")])
        neutral_hits = len(scan_df[scan_df["Signal"].str.contains("⚪|⚠️")])

        st.markdown("### 🔍 **Scan Results Summary**")
        sc_col1, sc_col2, sc_col3, sc_col4, sc_col5 = st.columns(5)
        sc_col1.metric("Nodes Scanned", f"{total_nodes} Tickers")
        sc_col2.metric("🟢 Actionable Buy Signals", f"{buy_hits} Hits")
        sc_col3.metric("🔴 Exit Triggers", f"{exit_hits} Hits")
        sc_col4.metric("🟡 Trend Holds", f"{hold_hits} Hits")
        sc_col5.metric("⚪ Neutral / Cash", f"{neutral_hits} Hits")

        st.write("---")

        if scan_strategy == "Channel Yield & Dividend Engine":
            display_columns = [
                "Ticker", "Last Close Price", "Dividend Per Share", "Custom Value Score",
                "Buy Range", "Hold Range", "Sell Range", "HMA", "HMA Trend", "MHLS", "Signal"
            ]
        elif scan_strategy == "Alma Targets & Turtle Pyramiding":
            display_columns = [
                "Ticker", "Price", "ALMA", "Slope Score", "ATR ($)", 
                "Signal", "Calculated Stop", "Target 1", "Target 2", "Target 3", "Target 4", "MHLS"
            ]
        else:
            display_columns = [
                "Ticker", "Price", "MHLS", "Score Weight", "Ann Volatility %",
                "Signal", "Calculated Stop", "Target 1", "Target 2", "50 SMA", "200 SMA", "RSI"
            ]

        st.dataframe(scan_df[display_columns], use_container_width=True, height=280)
        st.write("---")

        st.subheader("🧮 Advanced Position Sizing & Turtle Pyramiding Execution Suite")

        calc_col1, calc_col2 = st.columns([1, 1.2])

        with calc_col1:
            available_signals = ["Show All Categories"] + sorted(scan_df["Signal"].unique().tolist())
            selected_signal_filter = st.selectbox(
                "Filter Assets by Signal State:",
                available_signals,
                key="signal_filter_key",
            )
            filtered_calc_df = (
                scan_df[scan_df["Signal"] == selected_signal_filter]
                if selected_signal_filter != "Show All Categories"
                else scan_df
            )

            if not filtered_calc_df.empty:
                calc_ticker = st.selectbox(
                    "Select Asset from Scanned List:",
                    filtered_calc_df["Ticker"].tolist(),
                    key="calc_select_key",
                )
                ticker_data = filtered_calc_df[filtered_calc_df["Ticker"] == calc_ticker].iloc[0]

                budget_price_val = float(ticker_data["Price"])
                stop_val = float(ticker_data["Calculated Stop"])

                st.markdown("#### **Turtle Pyramiding & Sizing Parameters**")
                acc_balance = st.number_input("Total Portfolio Value ($)", min_value=100.0, value=100000.0, step=5000.0)
                avail_cash = st.number_input("Available Liquid Cash ($)", min_value=0.0, value=50000.0, step=5000.0)
                turtle_risk_pct = st.slider("Turtle Account Risk Per Unit (%)", 0.5, 3.0, 1.0, 0.25) / 100.0
                pyramid_units = st.slider("Max Pyramid Units (N)", 1, 5, 4, key="pyramid_units_key")
            else:
                calc_ticker = None

        with calc_col2:
            if calc_ticker is not None:
                unit_risk_dollars = acc_balance * turtle_risk_pct
                per_share_risk = max(budget_price_val - stop_val, 0.01)
                shares_per_unit = int(unit_risk_dollars / per_share_risk)
                total_pyramid_shares = shares_per_unit * pyramid_units

                cap_alloc = total_pyramid_shares * budget_price_val
                port_weight = (cap_alloc / acc_balance) * 100 if acc_balance > 0 else 0
                total_risk_dollars = per_share_risk * shares_per_unit

                # SAFE TYPE CHECKING FOR TARGET STRINGS TO PREVENT FORMATTING ERRORS
                t1_str = f"${ticker_data['Target 1']:.2f}" if isinstance(ticker_data.get('Target 1'), (int, float)) else str(ticker_data.get('Target 1', 'N/A'))
                t2_str = f"${ticker_data['Target 2']:.2f}" if isinstance(ticker_data.get('Target 2'), (int, float)) else str(ticker_data.get('Target 2', 'N/A'))
                t3_str = f"${ticker_data['Target 3']:.2f}" if isinstance(ticker_data.get('Target 3'), (int, float)) else str(ticker_data.get('Target 3', 'N/A'))
                t4_str = f"${ticker_data['Target 4']:.2f}" if isinstance(ticker_data.get('Target 4'), (int, float)) else str(ticker_data.get('Target 4', 'N/A'))

                trade_card_html = f"""
                <div style="background-color: {metric_bg}; border: 2px solid {border_color}; border-radius: 12px; padding: 24px; font-family: {font_family}; color: {text_main}; margin-top: 10px;">
                    
                    <div style="text-align: center; border-bottom: 2px solid {border_color}; padding-bottom: 12px; margin-bottom: 16px;">
                        <h1 style="margin: 0; font-size: 38px; font-weight: 800; letter-spacing: 2px;">{calc_ticker} (TURTLE PYRAMID)</h1>
                        <span style="font-size: 13px; font-weight: bold; background: {border_color}; color: #000; padding: 3px 10px; border-radius: 4px; display: inline-block; margin-top: 6px;">{ticker_data['Signal']}</span>
                    </div>

                    <div style="background: rgba(255,255,255,0.05); border-bottom: 2px solid {border_color}; padding: 14px; text-align: center; margin-bottom: 16px; border-radius: 8px;">
                        <div style="font-size: 13px; opacity: 0.75; letter-spacing: 1px; font-weight: bold;">TOTAL PYRAMID SHARES ({pyramid_units} Units)</div>
                        <div style="font-size: 32px; font-weight: 800; color: #F8FAFC;">{total_pyramid_shares:,} <span style="font-size: 14px; font-weight: normal;">({shares_per_unit:,} sh/unit)</span></div>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; border-bottom: 2px solid {border_color}; padding-bottom: 16px; margin-bottom: 16px; text-align: center;">
                        <div style="background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 6px; border: 10px solid #10B981;">
                            <div style="font-size: 11px; opacity: 0.8; font-weight: bold; color: #10B981;">BUY / ENTRY</div>
                            <div style="font-size: 18px; font-weight: bold;">${budget_price_val:.2f}</div>
                        </div>
                        <div style="background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 6px; border: 1px solid #EF4444;">
                            <div style="font-size: 11px; opacity: 0.8; font-weight: bold; color: #EF4444;">STOP LOSS</div>
                            <div style="font-size: 18px; font-weight: bold;">${stop_val:.2f}</div>
                        </div>
                        <div style="background: rgba(59, 130, 246, 0.1); padding: 10px; border-radius: 6px; border: 1px solid #3B82F6;">
                            <div style="font-size: 11px; opacity: 0.8; font-weight: bold; color: #3B82F6;">T1 / T2</div>
                            <div style="font-size: 14px; font-weight: bold;">{t1_str} | {t2_str}</div>
                        </div>
                        <div style="background: rgba(168, 85, 247, 0.1); padding: 10px; border-radius: 6px; border: 1px solid #A855F7;">
                            <div style="font-size: 11px; opacity: 0.8; font-weight: bold; color: #A855F7;">T3 / T4</div>
                            <div style="font-size: 14px; font-weight: bold;">{t3_str} | {t4_str}</div>
                        </div>
                    </div>

                    <div style="padding-top: 6px;">
                        <div style="font-size: 11px; font-weight: bold; opacity: 0.6; margin-bottom: 8px; letter-spacing: 1px;">EXTRA INFO</div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 13px;">
                            <div><b>Capital Alloc:</b> ${cap_alloc:,.2f}</div>
                            <div><b>Portfolio Weight:</b> {port_weight:.1f}%</div>
                            <div><b>Unit Risk ($):</b> <span style="color: #EF4444; font-weight: bold;">${total_risk_dollars:,.2f}</span></div>
                            <div><b>Pyramid Scale Units:</b> {pyramid_units} Units</div>
                        </div>
                    </div>

                </div>
                """
                st.html(trade_card_html)

                st.write("---")
                st.subheader(f"📈 Alma Targets & Price Structure Visualizer: {calc_ticker}")
                
                chart_df = yf.Ticker(calc_ticker).history(period="3mo")
                if not chart_df.empty:
                    chart_df["ALMA"] = calculate_alma(chart_df["Close"], length=34, offset=0.85, sigma=6.0)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=chart_df.index,
                        open=chart_df["Open"], high=chart_df["High"],
                        low=chart_df["Low"], close=chart_df["Close"],
                        name="Price Action"
                    ))
                    fig.add_trace(go.Scatter(
                        x=chart_df.index, y=chart_df["ALMA"],
                        line=dict(color="#00FFFF", width=2),
                        name="ALMA Baseline"
                    ))
                    fig.add_hline(y=budget_price_val, line_dash="solid", line_color="#10B981", annotation_text=f"Entry: ${budget_price_val:.2f}")
                    fig.add_hline(y=stop_val, line_dash="dash", line_color="#EF4444", annotation_text=f"Stop Loss: ${stop_val:.2f}")
                    if 'Target 1' in ticker_data and isinstance(ticker_data['Target 1'], (int, float)):
                        fig.add_hline(y=ticker_data['Target 1'], line_dash="dot", line_color="#3B82F6", annotation_text="T1 (1R)")
                    if 'Target 2' in ticker_data and isinstance(ticker_data['Target 2'], (int, float)):
                        fig.add_hline(y=ticker_data['Target 2'], line_dash="dot", line_color="#3B82F6", annotation_text="T2 (2R)")
                    if 'Target 3' in ticker_data and isinstance(ticker_data['Target 3'], (int, float)):
                        fig.add_hline(y=ticker_data['Target 3'], line_dash="dot", line_color="#A855F7", annotation_text="T3 (3R)")
                    if 'Target 4' in ticker_data and isinstance(ticker_data['Target 4'], (int, float)):
                        fig.add_hline(y=ticker_data['Target 4'], line_dash="dot", line_color="#A855F7", annotation_text="T4 (4R)")

                    fig.update_layout(
                        template="plotly_dark" if theme_choice in ["Quantum Dark Core", "Standard Dark Mode"] else "plotly_white",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        height=450,
                        margin=dict(l=10, r=10, t=30, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)
