import sqlite3
from datetime import date, datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AlphaScan Execution Suite",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- 1. PRIVATE APP SECURITY ---
def check_password():
  """Returns True if the user has entered the correct password."""
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

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("📌 Navigation")
app_mode = st.sidebar.radio(
    "Go to Page:",
    [
        "⚡ AlphaScan Engine",
    ],
)

# --- INTERFACE THEME STYLING ---
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


# --- MATHEMATICAL & INDICATOR ENGINE ---
def calculate_wma(series, length):
  weights = np.arange(1, length + 1)
  return series.rolling(length).apply(
      lambda w: np.dot(w, weights) / weights.sum(), raw=True
  )


def calculate_hma(series, length=20):
  """Thinkorswim-aligned Hull Moving Average calculation using rounded integer sqrt."""
  half_length = int(length / 2)
  sqrt_length = int(np.round(np.sqrt(length)))
  wma_half = calculate_wma(series, half_length)
  wma_full = calculate_wma(series, length)
  raw_hma = 2 * wma_half - wma_full
  return calculate_wma(raw_hma, sqrt_length)


def calculate_mhls_and_volatility(df):
  """Calculates Multi-Horizon Lookback Score (MHLS), Score Weight, and 30-day Annualized Volatility."""
  if len(df) < 43:
    return 0, 0.0, 0.0, 0.0

  current_close = df["Close"].iloc[-1]
  lookbacks = [5, 10, 21, 42]  # 1w, 2w, 1m, 2m
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
# PAGE 1: ALPHASCAN ENGINE
# ==========================================
if app_mode == "⚡ AlphaScan Engine":
  st.sidebar.header("🎯 Strategy Mode")
  scan_strategy = st.sidebar.radio(
      "Select Scanning Framework:",
      [
          "Universal 4-HMA Trend-Following",
          "Large Cap Core Matrix",
          "Squeeze / Penny Stock Multiplier",
      ],
      key="strategy_choice",
  )

  # CONSOLIDATED SINGLE-LINE UNIVERSE DEFINITIONS
  FULL_SP500 = [
      "AAPL",
      "MSFT",
      "NVDA",
      "AMZN",
      "META",
      "GOOGL",
      "GOOG",
      "BRK-B",
      "LLY",
      "AVGO",
      "JPM",
      "TSLA",
      "WMT",
      "XOM",
      "UNH",
      "V",
      "PG",
      "MA",
      "ORCL",
      "COST",
      "HD",
      "CVX",
      "BAC",
      "ABBV",
      "NFLX",
      "KO",
      "MRK",
      "AMD",
      "PEP",
      "ADBE",
      "LIN",
      "TMO",
      "WFC",
      "CSCO",
      "ACN",
      "MCD",
      "DIS",
      "ABT",
      "GE",
      "INTU",
      "QCOM",
      "TXN",
      "CAT",
      "AMAT",
      "PM",
      "VZ",
      "AXP",
      "UBER",
      "PFE",
      "IBM",
      "MS",
      "LOW",
      "UNP",
      "AMGN",
      "GS",
      "NOW",
      "SPGI",
      "LRCX",
      "SYK",
      "RTX",
      "HON",
      "BKNG",
      "T",
      "BLK",
      "TJX",
      "C",
      "ADP",
      "SBUX",
      "COP",
      "VRTX",
      "PLTR",
      "MDLZ",
      "BA",
      "BMY",
      "PANW",
      "SCHW",
      "ADI",
      "FI",
      "CB",
      "DE",
      "MMC",
      "LMT",
      "TMUS",
      "ECL",
      "GEV",
      "INTC",
      "SO",
      "GILD",
      "NKE",
      "MU",
      "MO",
      "PGR",
      "UPS",
      "SHW",
      "DUK",
      "TT",
  ]
  DOW_30 = [
      "AAPL",
      "AMZN",
      "AXP",
      "BA",
      "BAC",
      "CAT",
      "CRM",
      "CSCO",
      "CVX",
      "DIS",
      "HD",
      "HON",
      "IBM",
      "INTC",
      "JNJ",
      "JPM",
      "KO",
      "MCD",
      "MMM",
      "MRK",
      "MSFT",
      "NKE",
      "NVDA",
      "PG",
      "SHW",
      "TRV",
      "UNH",
      "V",
      "VZ",
      "WMT",
TOP_ETFS = [
    "BITO",
    "TSLL",
    "SNXX",
    "TQQQ",
    "NVD",
    "MSTU",
    "SQQQ",
    "SOXL",
    "MUU",
    "SOXS",
    "DRAM",
    "SPY",
    "SPDN",
    "QQQ",
    "IBIT",
    "PLTD",
    "TSLG",
    "XLF",
    "XLE",
    "DAMD",
    "HYG",
    "ETHA",
    "EEM",
    "LQD",
    "FXI",
    "KORU",
    "TLT",
    "IWM",
    "KWEB",
    "TSDD",
    "EWZ",
    "TZA",
    "EWY",
    "NOWL",
    "GDX",
    "SCHD",
    "BTCZ",
    "QID",
    "CONL",
    "SGOV",
    "XLU",
    "NVDL",
    "SLV",
    "MSTZ",
    "IONZ",
    "RWM",
    "IGV",
    "RKLZ",
    "MUD",
    "KRE",
    "AMZD",
    "RGTZ",
    "OKLL",
    "IEMG",
    "EFA",
    "SCHX",
    "SPYM",
    "XLK",
    "XLP",
    "SMH",
    "XLB",
    "AVS",
    "VEA",
    "USHY",
    "MULL",
    "XLV",
    "SNDQ",
    "SOXX",
    "BIL",
    "SCHG",
    "RSP",
    "IEFA",
    "SPXU",
    "VXX",
    "AAPD",
    "SCO",
    "LABD",
    "BMNU",
    "XBI",
    "SH",
    "NVDX",
    "PSLV",
    "SCHB",
    "VCIT",
    "BITX",
    "PSQ",
    "VWO",
    "BKLN",
    "AGG",
    "GOVT",
    "TSLQ",
    "MSFU",
    "XLY",
    "UVXY",
    "BND",
    "VOO",
    "IVV",
    "SCHF",
    "UNG",
]

  ]
  DEFAULT_SPECULATIVE = [
      "SOUN",
      "BBAI",
      "LCID",
      "GRND",
      "NKLA",
      "NIO",
      "OPEN",
      "SOFI",
      "PTON",
      "MARA",
      "RIOT",
      "CLSK",
      "HUT",
      "CLOV",
      "MQ",
      "NXDR",
  ]

  if scan_strategy == "Squeeze / Penny Stock Multiplier":
    st.sidebar.header("📁 Squeeze Asset Array")
    penny_input = st.sidebar.text_area(
        "Speculative Screener Nodes:",
        ", ".join(DEFAULT_SPECULATIVE),
        key="penny_input_key",
    )
    tickers = list(
        dict.fromkeys(
            [t.strip().upper() for t in penny_input.split(",") if t.strip()]
        )
    )
    max_price_filter = 15.00
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
      default_watchlist = (
          "GDX, AAPL, TSLA, MSFT, NVDA, AMD, AMZN, META, GOOGL, LLY, JPM"
      )
      watchlist_input = st.sidebar.text_area(
          "Edit Watchlist Arrays:", default_watchlist, key="watchlist_input_key"
      )
      tickers = list(
          dict.fromkeys(
              [
                  t.strip().upper()
                  for t in watchlist_input.split(",")
                  if t.strip()
              ]
          )
      )
    elif source_type == "Top ETFs Array":
      raw_etfs = list(dict.fromkeys(TOP_ETFS))
      max_scan = st.sidebar.slider(
          "ETF Scan Depth:", 5, len(raw_etfs), len(raw_etfs), key="etf_depth"
      )
      tickers = raw_etfs[:max_scan]
    elif source_type == "Full S&P 500 Index":
      raw_tickers = list(dict.fromkeys(FULL_SP500))
      max_scan = st.sidebar.slider(
          "S&P 500 Scan Depth:",
          10,
          len(raw_tickers),
          50,
          step=5,
          key="sp_depth",
      )
      tickers = raw_tickers[:max_scan]
    else:
      tickers = list(dict.fromkeys(DOW_30))
    max_price_filter = 99999.0

  st.sidebar.write("---")
  st.sidebar.header("⚙️ Risk Parameters")
  atr_period = st.sidebar.slider("ATR Lookback", 5, 30, 14, key="atr_period_key")

  if scan_strategy == "Universal 4-HMA Trend-Following":
    hma_stop_mode = st.sidebar.selectbox(
        "HMA Stop-Loss Mode:",
        [
            "Most Recent Red HMA Low",
            "2nd Most Recent Red HMA Low",
            "ATR Multiplier",
        ],
        key="hma_stop_mode_key",
    )
    risk_multiplier = (
        st.sidebar.slider(
            "Risk Envelope Scalar (ATR)",
            0.5,
            5.0,
            1.5,
            step=0.1,
            key="risk_multiplier_key",
        )
        if hma_stop_mode == "ATR Multiplier"
        else 1.5
    )
    st.sidebar.write("---")
    exit_style = st.sidebar.radio(
        "Select Exit Methodology:",
        [
            "Hybrid Scale-Out (Fixed Targets + Trail)",
            "Pure Trailing Exit (No Fixed Targets)",
        ],
        key="exit_style_key",
    )
    if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)":
      target_1_multiplier = st.sidebar.slider(
          "Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1, key="t1_mult_key"
      )
      target_2_multiplier = st.sidebar.slider(
          "Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1, key="t2_mult_key"
      )
    else:
      target_1_multiplier, target_2_multiplier = None, None
  else:
    exit_style = "Hybrid Scale-Out (Fixed Targets + Trail)"
    risk_multiplier = st.sidebar.slider(
        "Risk Envelope Scalar (Stops)",
        1.0,
        4.0,
        1.5,
        step=0.1,
        key="risk_multiplier_key",
    )
    st.sidebar.write("---")
    target_1_multiplier = st.sidebar.slider(
        "Alpha Target 1 (R:R)", 0.5, 5.0, 1.5, step=0.1, key="t1_mult_key"
    )
    target_2_multiplier = st.sidebar.slider(
        "Alpha Target 2 (R:R)", 1.0, 10.0, 3.0, step=0.1, key="t2_mult_key"
    )

  def scan_ticker(ticker_symbol):
    try:
      df = yf.Ticker(ticker_symbol).history(period="250d", auto_adjust=False)
      if df.empty or len(df) < 200:
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

      latest, prev, prev_2 = df.iloc[-1], df.iloc[-2], df.iloc[-3]
      price = latest["Close"]
      if price > max_price_filter:
        return None

      mhls, score_weight_float, score_weight_pct, ann_vol = (
          calculate_mhls_and_volatility(df)
      )

      atr = latest["ATR"]
      risk_amount = risk_multiplier * atr
      ema_pinch = abs(latest["EMA_9"] - latest["EMA_21"]) / latest["EMA_21"]
      vol_spike = latest["Relative_Volume"]
      is_coiling = (
          "CRITICAL SQUEEZE"
          if (ema_pinch < 0.015 and vol_spike > 1.2)
          else ("Yes" if ema_pinch < 0.015 else "No")
      )
      bullish_cross = (prev["EMA_9"] <= prev["EMA_21"]) and (
          latest["EMA_9"] > latest["EMA_21"]
      )
      bearish_cross = (prev["EMA_9"] >= prev["EMA_21"]) and (
          latest["EMA_9"] < latest["EMA_21"]
      )

      if scan_strategy == "Universal 4-HMA Trend-Following":
        above_smas = (price > latest["SMA_50"]) and (price > latest["SMA_200"])
        recent_cross = (
            (prev["HMA_Close"] <= prev["HMA_Open"])
            and (latest["HMA_Close"] > latest["HMA_Open"])
        ) or (
            (prev_2["HMA_Close"] <= prev_2["HMA_Open"])
            and (prev["HMA_Close"] > prev["HMA_Open"])
        )
        hma_close_sloping_up = latest["HMA_Close"] > prev["HMA_Close"]
        hma_open_sloping_up = latest["HMA_Open"] > prev["HMA_Open"]
        closed_above_white = price > latest["HMA_Close"]
        hma_high, hma_low = max(latest["HMA_High"], latest["HMA_Low"]), min(
            latest["HMA_High"], latest["HMA_Low"]
        )
        is_inside_hma_channel = (price >= hma_low) and (price <= hma_high)

        red_hma_df = df[df["HMA_Close"] < df["HMA_Open"]]
        if hma_stop_mode == "Most Recent Red HMA Low":
          stop = (
              red_hma_df.iloc[-1]["HMA_Low"]
              if not red_hma_df.empty
              else latest["HMA_Low"]
          )
          stop_type = "Most Recent Red HMA Low"
        elif hma_stop_mode == "2nd Most Recent Red HMA Low":
          stop = (
              red_hma_df.iloc[-2]["HMA_Low"]
              if len(red_hma_df) >= 2
              else (
                  red_hma_df.iloc[-1]["HMA_Low"]
                  if not red_hma_df.empty
                  else latest["HMA_Low"]
              )
          )
          stop_type = "2nd Most Recent Red HMA Low"
        else:
          stop = price - risk_amount
          stop_type = f"ATR Multiplier ({risk_multiplier}x)"

        risk_per_share = max(price - stop, 0.01)
        t1_val = (
            round(price + (risk_per_share * target_1_multiplier), 2)
            if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)"
            else "PURE TRAIL"
        )
        t2_val = (
            round(price + (risk_per_share * target_2_multiplier), 2)
            if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)"
            else "PURE TRAIL"
        )

        if (
            above_smas
            and recent_cross
            and hma_close_sloping_up
            and hma_open_sloping_up
            and closed_above_white
        ):
          signal = "🟢 BUY ENTRY"
        elif price < stop:
          signal = "🔴 EXIT TRIGGER"
        elif is_inside_hma_channel:
          signal = "🟡 HOLD (Consolidating)"
        elif latest["HMA_Close"] > latest["HMA_Open"] and above_smas:
          signal = "🟡 BULLISH TREND"
        else:
          signal = "⚪ NEUTRAL / WAIT"

      elif scan_strategy == "Squeeze / Penny Stock Multiplier":
        stop = price - risk_amount
        stop_type = "ATR Envelope"
        t1_val = round(price + (risk_amount * target_1_multiplier), 2)
        t2_val = round(price + (risk_amount * target_2_multiplier), 2)
        signal = (
            "🟢 EXPANSION TRIGGER"
            if (
                bullish_cross
                or (
                    is_coiling == "CRITICAL SQUEEZE"
                    and latest["Close"] > latest["EMA_9"]
                )
            )
            else "⚪ MONITOR COILING"
        )
      else:
        stop_type = "ATR Envelope"
        if bullish_cross and latest["RSI"] > 40:
          signal, stop = "🟢 BUY TRIGGER", price - risk_amount
          t1_val, t2_val = round(
              price + (risk_amount * target_1_multiplier), 2
          ), round(price + (risk_amount * target_2_multiplier), 2)
        elif bearish_cross or (
            latest["RSI"] > 70 and latest["EMA_9"] < latest["EMA_21"]
        ):
          signal, stop = "🔴 SELL TRIGGER", price + risk_amount
          t1_val, t2_val = round(
              price - (risk_amount * target_1_multiplier), 2
          ), round(price - (risk_amount * target_2_multiplier), 2)
        elif latest["EMA_9"] > latest["EMA_21"]:
          signal, stop = "🟡 HOLD (Bullish)", price - risk_amount
          t1_val, t2_val = round(
              price + (risk_amount * target_1_multiplier), 2
          ), round(price + (risk_amount * target_2_multiplier), 2)
        else:
          signal, stop = "⚪ HOLD (Cash)", price + risk_amount
          t1_val, t2_val = round(
              price - (risk_amount * target_1_multiplier), 2
          ), round(price - (risk_amount * target_2_multiplier), 2)

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
    neutral_hits = len(scan_df[scan_df["Signal"].str.contains("⚪")])

    st.markdown("### 🔍 **Scan Results Summary**")
    sc_col1, sc_col2, sc_col3, sc_col4, sc_col5 = st.columns(5)
    sc_col1.metric("Nodes Scanned", f"{total_nodes} Tickers")
    sc_col2.metric("🟢 Actionable Buy Signals", f"{buy_hits} Hits")
    sc_col3.metric("🔴 Exit Triggers", f"{exit_hits} Hits")
    sc_col4.metric("🟡 Trend Holds", f"{hold_hits} Hits")
    sc_col5.metric("⚪ Neutral / Cash", f"{neutral_hits} Hits")

    st.write("---")
    display_columns = [
        "Ticker",
        "Price",
        "MHLS",
        "Score Weight",
        "Ann Volatility %",
        "Signal",
        "Calculated Stop",
        "Target 1",
        "Target 2",
        "50 SMA",
        "200 SMA",
        "RSI",
    ]
    st.dataframe(
        scan_df[display_columns], use_container_width=True, height=280
    )
    st.write("---")

    st.subheader("🧮 Advanced Position Sizing Calculator")

    calc_col1, calc_col2 = st.columns([1, 1.2])

    with calc_col1:
      available_signals = ["Show All Categories"] + sorted(
          scan_df["Signal"].unique().tolist()
      )
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
        ticker_data = filtered_calc_df[
            filtered_calc_df["Ticker"] == calc_ticker
        ].iloc[0]

        budget_price_val = float(ticker_data["Price"])
        stop_val = float(ticker_data["Calculated Stop"])
        score_weight = float(ticker_data["Score Weight Raw"])
        ann_vol = float(ticker_data["Ann Volatility Raw"])

        st.markdown("#### **Sizing Options**")
        sizing_method = st.radio(
            "Select Position Sizing Model:",
            ["Volumetric (MHLS + Volatility)", "Standard Fixed Risk (ATR)"],
            key="sizing_method_choice",
        )

        acc_balance = st.number_input(
            "Total Portfolio Value ($)",
            min_value=100.0,
            value=10000.0,
            step=500.0,
        )
        avail_cash = st.number_input(
            "Available Liquid Cash ($)",
            min_value=0.0,
            value=5000.0,
            step=500.0,
        )
        target_risk_pct = (
            st.slider(
                "Target Risk %",
                0.25,
                10.0,
                2.0,
                0.25,
                help="Target portfolio risk percentage",
            )
            / 100.0
        )
      else:
        calc_ticker = None

    with calc_col2:
      if calc_ticker is not None:
        if sizing_method == "Volumetric (MHLS + Volatility)":
          if ann_vol > 0:
            target_position_value = (
                score_weight * (target_risk_pct / ann_vol) * acc_balance
            )
            final_shares = max(
                0,
                min(
                    int(target_position_value / budget_price_val),
                    int(avail_cash / budget_price_val),
                ),
            )
          else:
            final_shares = 0

          st.markdown("### **Volumetric Position Model Output**")
          st.write(f"**MHLS:** `{ticker_data['MHLS']}`")
          st.write(f"**Score Weight:** `{ticker_data['Score Weight']}`")
          st.write(
              f"**Annualized Volatility:** `{ticker_data['Ann Volatility %']}%`"
          )
          st.metric("Recommended Share Count", f"{final_shares:,} Shares")
          st.metric(
              "Total Capital Allocation",
              f"${final_shares * budget_price_val:,.2f}",
              delta=(
                  f"{(final_shares * budget_price_val / acc_balance)*100:.1f}%"
                  " of Portfolio"
              ),
          )

        else:
          risk_per_share = max(budget_price_val - stop_val, 0.01)
          dollar_risk_allowed = acc_balance * target_risk_pct
          shares_by_risk = int(dollar_risk_allowed / risk_per_share)
          shares_by_cash = int(avail_cash / budget_price_val)
          final_shares = max(0, min(shares_by_risk, shares_by_cash))

          st.markdown("### **Fixed Risk (ATR) Model Output**")
          st.metric("Recommended Share Count", f"{final_shares:,} Shares")
          st.metric(
              "Budget Capital Required",
              f"${final_shares * budget_price_val:,.2f}",
          )
