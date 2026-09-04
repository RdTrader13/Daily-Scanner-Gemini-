import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Quantitative Swing & Momentum Scanner",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ Quantitative Swing & Momentum Scanner")
st.caption(
    "Multi-Universe Technical Scanner, MHLS Dynamic Sizer & Visualizer"
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
st.sidebar.header("🕹️ Global Parameters")

account_capital = st.sidebar.number_input(
    "Total Portfolio Capital ($)", value=25000, step=1000
)
max_risk_pct = (
    st.sidebar.slider("Max Account Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.25)
    / 100.0
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Scanner Settings")

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
    "Target 1 R-Multiple", value=1.5, step=0.5
)
target_2_multiplier = st.sidebar.number_input(
    "Target 2 R-Multiple", value=3.0, step=0.5
)
max_price_filter = st.sidebar.number_input(
    "Max Asset Price Filter ($)", value=2000.0
)
atr_period = st.sidebar.number_input("ATR Period", value=14)


# ==========================================
# TECHNICAL & MHLS MATH FUNCTIONS
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
  return diff.rolling(window=sqrt_period).apply(
      lambda x: np.dot(x, np.arange(1, sqrt_period + 1))
      / np.arange(1, sqrt_period + 1).sum(),
      raw=True,
  )


def calculate_mhls_and_volatility(df):
  """Calculates Multi-Horizon Lookback Score using log returns across 21d, 63d, 126d, 252d windows, and normalizes it against annualized log volatility."""
  close_prices = df["Close"]
  lookbacks = [21, 63, 126, 252]
  log_returns = []

  for lb in lookbacks:
    if len(close_prices) >= lb:
      # Log return calculation: ln(P_t / P_{t-k})
      l_ret = np.log(close_prices.iloc[-1] / close_prices.iloc[-lb])
      log_returns.append(l_ret)

  mhls = np.mean(log_returns) if log_returns else 0.0

  # Annualized volatility via log returns
  daily_log_returns = np.log(close_prices / close_prices.shift(1)).dropna()
  ann_vol = (
      daily_log_returns.std() * np.sqrt(252)
      if len(daily_log_returns) > 20
      else 0.20
  )

  # MHLS Volatility Weight Ratio
  raw_weight = (mhls / ann_vol) if ann_vol > 0 else 0.0
  score_weight_pct = np.clip(raw_weight * 100, 0.0, 100.0)

  return round(float(mhls), 4), raw_weight, score_weight_pct, float(ann_vol)


def get_df_with_indicators(ticker_symbol):
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

  return df


# ==========================================
# SCANNER ENGINE
# ==========================================
def scan_ticker(ticker_symbol):
  try:
    df = get_df_with_indicators(ticker_symbol)
    if df is None:
      return None

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
      closed_above_white = price > latest["HMA_Close"]
      is_inside_hma_channel = (
          price >= min(latest["HMA_High"], latest["HMA_Low"])
      ) and (price <= max(latest["HMA_High"], latest["HMA_Low"]))

      red_hma_df = df[df["HMA_Close"] < df["HMA_Open"]]
      if hma_stop_mode == "Most Recent Red HMA Low":
        stop = (
            red_hma_df.iloc[-1]["HMA_Low"]
            if not red_hma_df.empty
            else latest["HMA_Low"]
        )
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
      else:
        stop = price - risk_amount

      t1_val = (
          round(price + ((price - stop) * target_1_multiplier), 2)
          if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)"
          else "PURE TRAIL"
      )
      t2_val = (
          round(price + ((price - stop) * target_2_multiplier), 2)
          if exit_style == "Hybrid Scale-Out (Fixed Targets + Trail)"
          else "PURE TRAIL"
      )

      if above_smas and recent_cross and closed_above_white:
        signal = "🟢 BUY ENTRY"
      elif price < stop:
        signal = "🔴 EXIT TRIGGER"
      elif is_inside_hma_channel:
        signal = "🟡 HOLD (Consolidating)"
      elif latest["HMA_Close"] > latest["HMA_Open"] and above_smas:
        signal = "🟡 BULLISH TREND"
      else:
        signal = "⚪ NEUTRAL / WAIT"

    else:
      stop = price - risk_amount
      t1_val = round(price + (risk_amount * target_1_multiplier), 2)
      t2_val = round(price + (risk_amount * target_2_multiplier), 2)
      signal = "🟢 BUY TRIGGER" if bullish_cross else "⚪ NEUTRAL"

    # ATR Sizing
    dollar_risk = account_capital * max_risk_pct
    risk_per_share_calc = max(price - stop, 0.01) if price > stop else 0.01
    suggested_shares_atr = int(dollar_risk / risk_per_share_calc)

    # MHLS Volatility Sizing
    mhls_allocation = account_capital * (score_weight_pct / 100.0)
    suggested_shares_mhls = int(mhls_allocation / price)

    return {
        "Ticker": ticker_symbol,
        "Price": round(price, 2),
        "Signal": signal,
        "Stop Loss": round(stop, 2),
        "Target 1": t1_val,
        "Target 2": t2_val,
        "ATR Shares": suggested_shares_atr,
        "MHLS Shares": suggested_shares_mhls,
        "MHLS Score": mhls,
        "MHLS Weight": f"{round(score_weight_pct, 1)}%",
        "Ann Volatility": f"{round(ann_vol * 100, 1)}%",
        "50 SMA": round(latest["SMA_50"], 2),
        "200 SMA": round(latest["SMA_200"], 2),
        "RSI": round(latest["RSI"], 1),
        "Squeeze": is_coiling,
    }
  except Exception:
    return None


# ==========================================
# MAIN APPLICATION INTERFACE (TABS)
# ==========================================
tab_scanner, tab_calculator, tab_charts = st.tabs(
    ["📡 Market Scanner", "🧮 Position Sizer Calculator", "📈 Interactive Charting"]
)

# ------------------------------------------
# TAB 1: MARKET SCANNER
# ------------------------------------------
with tab_scanner:
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

      csv_data = filtered_df.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Download Scan Results (CSV)",
          data=csv_data,
          file_name="market_scan_results.csv",
          mime="text/csv",
      )
    else:
      st.error("No valid matrix node data found for selected tickers.")

# ------------------------------------------
# TAB 2: POSITION SIZER CALCULATOR
# ------------------------------------------
with tab_calculator:
  st.subheader("🎯 Institutional Risk & Dynamic MHLS Position Sizer")

  sizing_mode = st.radio(
      "Select Position Sizing Model",
      [
          "ATR Risk-Based Sizing (% Account Risk)",
          "MHLS Volatility-Weighted Sizing (Institutional Momentum Target)",
      ],
      horizontal=True,
  )

  calc_col1, calc_col2 = st.columns(2)

  with calc_col1:
    calc_ticker = (
        st.text_input("Ticker Symbol for Auto-Fetch", "NVDA")
        .strip()
        .upper()
    )
    calc_capital = st.number_input(
        "Account Capital ($)",
        value=float(account_capital),
        step=1000.0,
        key="calc_cap",
    )
    calc_risk_pct = (
        st.number_input(
            "Max Account Risk (%)",
            value=float(max_risk_pct * 100),
            step=0.25,
            key="calc_risk",
        )
        / 100.0
    )

    fetched_df = get_df_with_indicators(calc_ticker)
    if fetched_df is not None:
      live_price = float(fetched_df["Close"].iloc[-1])
      mhls_val, raw_w, weight_pct, ann_v = calculate_mhls_and_volatility(
          fetched_df
      )
      live_atr = float(fetched_df["ATR"].iloc[-1])
      st.success(
          f"Loaded {calc_ticker}: Price = ${live_price:.2f} | MHLS ="
          f" {mhls_val:.4f} | Vol = {ann_v*100:.1f}%"
      )
    else:
      live_price, mhls_val, weight_pct, ann_v, live_atr = (
          100.0,
          0.1500,
          25.0,
          0.30,
          2.50,
      )
      st.warning(
          f"Could not load live metrics for {calc_ticker}. Using default"
          " placeholder inputs."
      )

    calc_entry = st.number_input(
        "Entry Price ($)", value=live_price, step=0.50, key="calc_entry"
    )
    calc_stop = st.number_input(
        "Stop Loss Price ($)",
        value=round(live_price - (2.0 * live_atr), 2),
        step=0.50,
        key="calc_stop",
    )

  with calc_col2:
    calc_t1 = st.number_input(
        "Target 1 Price ($)",
        value=round(calc_entry + 1.5 * (calc_entry - calc_stop), 2),
        step=0.50,
        key="calc_t1",
    )
    calc_t2 = st.number_input(
        "Target 2 Price ($)",
        value=round(calc_entry + 3.0 * (calc_entry - calc_stop), 2),
        step=0.50,
        key="calc_t2",
    )

    st.markdown("---")
    st.markdown("### 🧬 MHLS Live Parameters")
    target_vol = (
        st.slider("Target Portfolio Volatility Limit (%)", 5.0, 30.0, 15.0, 1.0)
        / 100.0
    )

  risk_per_share = calc_entry - calc_stop

  if risk_per_share <= 0:
    st.error("Entry price must be greater than Stop Loss price for long setups.")
  else:
    if "ATR Risk-Based" in sizing_mode:
      dollar_risk = calc_capital * calc_risk_pct
      shares = int(dollar_risk / risk_per_share)
      total_cost = shares * calc_entry
      allocation_pct = (total_cost / calc_capital) * 100
      mode_desc = f"Based on risking {calc_risk_pct*100:.2f}% of portfolio."
    else:
      # MHLS Sizing Logic
      vol_scaling_factor = target_vol / (ann_v + 1e-5)
      adjusted_weight_pct = np.clip(
          weight_pct * vol_scaling_factor, 0.0, 100.0
      )
      total_cost = calc_capital * (adjusted_weight_pct / 100.0)
      shares = int(total_cost / calc_entry)
      dollar_risk = shares * risk_per_share
      allocation_pct = adjusted_weight_pct
      mode_desc = (
          f"Based on MHLS Score ({mhls_val:.4f}) and Target Volatility"
          f" ({target_vol*100:.1f}%)."
      )

    st.markdown("---")
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("Calculated Shares", f"{shares:,}")
    res_col2.metric("Total Capital Allocated", f"${total_cost:,.2f}")
    res_col3.metric("Portfolio Allocation", f"{allocation_pct:.1f}%")
    res_col4.metric("Actual Dollar Risk at Stop", f"${dollar_risk:,.2f}")

    st.caption(f"**Strategy Note:** {mode_desc}")

    st.markdown("---")
    st.markdown("### 📊 Trade Scale-Out Matrix")
    m_col1, m_col2, m_col3 = st.columns(3)
    r1 = (calc_t1 - calc_entry) / risk_per_share
    r2 = (calc_t2 - calc_entry) / risk_per_share

    t1_profit = shares * 0.5 * (calc_t1 - calc_entry)
    t2_profit = shares * 0.5 * (calc_t2 - calc_entry)

    m_col1.metric("Risk Per Share", f"${risk_per_share:.2f}")
    m_col2.metric("Target 1 Multiplier", f"{r1:.2f} R")
    m_col3.metric("Target 2 Multiplier", f"{r2:.2f} R")

    st.info(
        f"**Expected Outcome:** T1 Scale Out (50% @ ${calc_t1:.2f}) ="
        f" **${t1_profit:,.2f}**. T2 Scale Out (50% @ ${calc_t2:.2f}) ="
        f" **${t2_profit:,.2f}**. Combined Potential Profit:"
        f" **${(t1_profit + t2_profit):,.2f}**."
    )

# ------------------------------------------
# TAB 3: INTERACTIVE CHARTING
# ------------------------------------------
with tab_charts:
  st.subheader("📈 Interactive Multi-Indicator Plotter")

  chart_ticker = (
      st.text_input("Enter Ticker Symbol to Plot", "NVDA").strip().upper()
  )

  if chart_ticker:
    df_chart = get_df_with_indicators(chart_ticker)

    if df_chart is not None and not df_chart.empty:
      fig = make_subplots(
          rows=2,
          cols=1,
          shared_xaxes=True,
          vertical_spacing=0.03,
          row_heights=[0.75, 0.25],
      )

      fig.add_trace(
          go.Candlestick(
              x=df_chart.index,
              open=df_chart["Open"],
              high=df_chart["High"],
              low=df_chart["Low"],
              close=df_chart["Close"],
              name="OHLC",
          ),
          row=1,
          col=1,
      )

      fig.add_trace(
          go.Scatter(
              x=df_chart.index,
              y=df_chart["HMA_Close"],
              line=dict(color="white", width=1.5),
              name="HMA Close",
          ),
          row=1,
          col=1,
      )
      fig.add_trace(
          go.Scatter(
              x=df_chart.index,
              y=df_chart["HMA_Open"],
              line=dict(color="orange", width=1.5),
              name="HMA Open",
          ),
          row=1,
          col=1,
      )

      fig.add_trace(
          go.Scatter(
              x=df_chart.index,
              y=df_chart["EMA_9"],
              line=dict(color="blue", width=1),
              name="9 EMA",
          ),
          row=1,
          col=1,
      )
      fig.add_trace(
          go.Scatter(
              x=df_chart.index,
              y=df_chart["EMA_21"],
              line=dict(color="purple", width=1),
              name="21 EMA",
          ),
          row=1,
          col=1,
      )

      colors = [
          "green" if c >= o else "red"
          for c, o in zip(df_chart["Close"], df_chart["Open"])
      ]
      fig.add_trace(
          go.Bar(
              x=df_chart.index,
              y=df_chart["Volume"],
              marker_color=colors,
              name="Volume",
          ),
          row=2,
          col=1,
      )

      fig.update_layout(
          title=f"{chart_ticker} Technical Chart (4-HMA, EMAs & Volume)",
          template="plotly_dark",
          xaxis_rangeslider_visible=False,
          height=650,
      )

      st.plotly_chart(fig, use_container_width=True)
    else:
      st.warning(f"Could not load market data for {chart_ticker}.")
