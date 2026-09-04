import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Institutional Swing & Momentum Scanner",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ Quantitative Swing & Momentum Scanner")
st.caption(
    "Multi-Universe Technical Scanner & Volatility Sizing Engine | Private Build"
)

# ==========================================
# UNIVERSE PRESETS
# ==========================================
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

MEGA_CAP_TECH = [
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "AVGO",
    "AMD",
    "PLTR",
]

DIVIDEND_ARISTOCRATS = [
    "NOBL",
    "JNJ",
    "PG",
    "KO",
    "PEP",
    "ABBV",
    "MMM",
    "TGT",
    "LOW",
    "EMR",
]

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("🕹️ Scanner Settings")

universe_choice = st.sidebar.selectbox(
    "Select Ticker Universe",
    [
        "Top Active ETFs (100)",
        "Mega-Cap Tech & Growth",
        "Dividend Aristocrats",
        "Custom List",
    ],
)

if universe_choice == "Top Active ETFs (100)":
  selected_tickers = TOP_ETFS
elif universe_choice == "Mega-Cap Tech & Growth":
  selected_tickers = MEGA_CAP_TECH
elif universe_choice == "Dividend Aristocrats":
  selected_tickers = DIVIDEND_ARISTOCRATS
else:
  custom_input = st.sidebar.text_area(
      "Enter Custom Tickers (comma separated)", "SPY, QQQ, NVDA, IBIT, TQQQ"
  )
  selected_tickers = [
      t.strip().upper() for t in custom_input.split(",") if t.strip()
  ]

scan_strategy = st.sidebar.selectbox(
    "Scan Logic / Strategy",
    [
        "Universal 4-HMA Trend-Following",
        "Squeeze / Penny Stock Multiplier",
        "EMA Cross + RSI Momentum",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Risk & Filter Parameters")

account_capital = st.sidebar.number_input(
    "Total Portfolio Capital ($)", value=25000, step=1000
)
max_risk_pct = (
    st.sidebar.slider("Max Account Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.25)
    / 100.0
)
risk_multiplier = st.sidebar.slider(
    "ATR Risk Multiplier (Stop Distance)", 1.0, 4.0, 2.0, 0.5
)

if scan_strategy == "Universal 4-HMA Trend-Following":
  hma_stop_mode = st.sidebar.selectbox(
      "HMA Stop Placement",
      [
          "ATR Multiplier",
          "Most Recent Red HMA Low",
          "2nd Most Recent Red HMA Low",
      ],
  )
  exit_style = st.sidebar.selectbox(
      "Exit Style",
      [
          "Hybrid Scale-Out (Fixed Targets + Trail)",
          "Pure Trail (No Fixed Target)",
      ],
  )
else:
  hma_stop_mode = "ATR Multiplier"
  exit_style = "Hybrid Scale-Out (Fixed Targets + Trail)"

target_1_multiplier = st.sidebar.number_input(
    "Target 1 R-Multiple (e.g. 1.5 R)", value=1.5, step=0.5
)
target_2_multiplier = st.sidebar.number_input(
    "Target 2 R-Multiple (e.g. 3.0 R)", value=3.0, step=0.5
)

max_price_filter = (
    15.0
    if scan_strategy == "Squeeze / Penny Stock Multiplier"
    else st.sidebar.number_input("Max Asset Price Filter ($)", value=2000.0)
)
atr_period = st.sidebar.number_input("ATR Calculation Period", value=14)


# ==========================================
# HELPER MATHEMATICAL FUNCTIONS
# ==========================================
def calculate_hma(series, period):
  wma_half = (
      series.rolling(window=int(period / 2))
      .apply(
          lambda x: np.dot(x, np.arange(1, int(period / 2) + 1))
          / np.arange(1, int(period / 2) + 1).sum(),
          raw=True,
      )
  )
  wma_full = series.rolling(window=period).apply(
      lambda x: np.dot(x, np.arange(1, period + 1)) / np.arange(1, period + 1).sum(),
      raw=True,
  )
  diff = 2 * wma_half - wma_full
  sqrt_period = int(np.sqrt(period))
  hma = diff.rolling(window=sqrt_period).apply(
      lambda x: np.dot(x, np.arange(1, sqrt_period + 1))
      / np.arange(1, sqrt_period + 1).sum(),
      raw=True,
  )
  return hma


def calculate_mhls_and_volatility(df):
  lookbacks = [21, 63, 126, 252]
  scores = []
  for lb in lookbacks:
    if len(df) >= lb:
      ret = (df["Close"].iloc[-1] - df["Close"].iloc[-lb]) / df["Close"].iloc[
          -lb
      ]
      scores.append(ret)
  mhls = np.mean(scores) if scores else 0.0

  daily_returns = df["Close"].pct_change().dropna()
  ann_vol = (
      daily_returns.std() * np.sqrt(252) if len(daily_returns) > 20 else 0.20
  )

  raw_weight = (mhls / (ann_vol + 1e-5)) if ann_vol > 0 else 0.0
  score_weight_pct = np.clip(raw_weight * 100, 0, 100)

  return round(mhls, 4), raw_weight, score_weight_pct, ann_vol


# ==========================================
# SCANNER ENGINE
# ==========================================
def scan_ticker(ticker_symbol):
  try:
    df = yf.Ticker(ticker_symbol).history(period="1y", auto_adjust=False)
    if df.empty or len(df) < 50:
      return None

    df["SMA_50"] = df["Close"].rolling(window=min(50, len(df))).mean()
    df["SMA_200"] = (
        df["Close"].rolling(window=200).mean()
        if len(df) >= 200
        else df["SMA_50"]
    )
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
        .rolling(int(atr_period))
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

    # Position Sizing Calculation
    dollar_risk = account_capital * max_risk_pct
    risk_per_share_calc = max(price - stop, 0.01) if price > stop else 0.01
    suggested_shares = int(dollar_risk / risk_per_share_calc)
    position_value = suggested_shares * price

    return {
        "Ticker": ticker_symbol,
        "Price": round(price, 2),
        "Signal": signal,
        "Stop Loss": round(stop, 2),
        "Stop Type": stop_type,
        "Target 1": t1_val,
        "Target 2": t2_val,
        "Suggested Shares": suggested_shares,
        "Position Size ($)": round(position_value, 2),
        "MHLS Score": mhls,
        "Vol Weight Score": f"{int(score_weight_pct)}%",
        "Ann Volatility": f"{round(ann_vol * 100, 1)}%",
        "50 SMA": round(latest["SMA_50"], 2),
        "200 SMA": round(latest["SMA_200"], 2),
        "RSI": round(latest["RSI"], 1),
        "Squeeze Status": is_coiling,
    }
  except Exception:
    return None


# ==========================================
# MAIN INTERFACE & SCAN RUNNER
# ==========================================
col1, col2 = st.columns([3, 1])
with col1:
  st.subheader(f"Scanning Universe: {universe_choice}")
  st.write(f"**Total Tickers in Scope:** {len(selected_tickers)}")
with col2:
  run_scan = st.button("🚀 Execute Market Scan", use_container_width=True)

if run_scan:
  progress_bar = st.progress(0)
  status_text = st.empty()
  results = []

  for idx, ticker in enumerate(selected_tickers):
    status_text.text(
        f"Scanning {ticker} ({idx+1}/{len(selected_tickers)})..."
    )
    res = scan_ticker(ticker)
    if res:
      results.append(res)
    progress_bar.progress((idx + 1) / len(selected_tickers))

  status_text.empty()
  progress_bar.empty()

  if results:
    results_df = pd.DataFrame(results)

    # Filter controls
    st.markdown("---")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
      signal_filter = st.multiselect(
          "Filter by Signal",
          options=list(results_df["Signal"].unique()),
          default=list(results_df["Signal"].unique()),
      )
    with filter_col2:
      min_mhls = st.slider(
          "Minimum MHLS Momentum Score",
          float(results_df["MHLS Score"].min()),
          float(results_df["MHLS Score"].max()),
          float(results_df["MHLS Score"].min()),
      )

    filtered_df = results_df[
        (results_df["Signal"].isin(signal_filter))
        & (results_df["MHLS Score"] >= min_mhls)
    ]

    st.subheader(f"Scan Results ({len(filtered_df)} Hits)")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # CSV Download
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Scan Results (CSV)",
        data=csv_data,
        file_name="market_scan_results.csv",
        mime="text/csv",
    )
  else:
    st.error("No valid matrix node data found for selected tickers.")
