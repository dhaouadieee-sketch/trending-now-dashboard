# ============================================================
# indicators.py — Calculates technical indicators
# These are mathematical formulas applied to stock prices
# that help predict future price movements
# ============================================================

import pandas as pd
import numpy as np

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a raw stock DataFrame and adds technical indicator
    columns to it. Returns the enriched DataFrame.
    """

    # ── MOVING AVERAGES ──────────────────────────────────────
    # Average closing price over the last N days
    # Smooths out noise and shows the general trend direction
    df["MA7"]  = df["Close"].rolling(window=7).mean()   # 1 week
    df["MA21"] = df["Close"].rolling(window=21).mean()  # 1 month

    # ── RSI (Relative Strength Index) ────────────────────────
    # Measures if a stock is overbought (>70) or oversold (<30)
    # Ranges from 0 to 100
    delta = df["Close"].diff()           # daily price changes
    gain  = delta.clip(lower=0)          # keep only positive changes
    loss  = -delta.clip(upper=0)         # keep only negative changes
    avg_gain = gain.rolling(14).mean()   # average gain over 14 days
    avg_loss = loss.rolling(14).mean()   # average loss over 14 days
    rs        = avg_gain / avg_loss      # ratio of gain to loss
    df["RSI"] = 100 - (100 / (1 + rs))  # final RSI formula

    # ── MACD (Moving Average Convergence Divergence) ─────────
    # Shows momentum by comparing two moving averages
    # When MACD crosses above signal line → buy signal
    ema12        = df["Close"].ewm(span=12).mean() # short term trend
    ema26        = df["Close"].ewm(span=26).mean() # long term trend
    df["MACD"]   = ema12 - ema26                   # difference
    df["Signal"] = df["MACD"].ewm(span=9).mean()   # signal line

    # ── BOLLINGER BANDS ──────────────────────────────────────
    # Shows price volatility using upper and lower bands
    # Price touching upper band → possibly overbought
    # Price touching lower band → possibly oversold
    rolling_std      = df["Close"].rolling(20).std()  # price volatility
    df["BB_upper"]   = df["MA21"] + (2 * rolling_std) # upper band
    df["BB_lower"]   = df["MA21"] - (2 * rolling_std) # lower band

    # ── DAILY RETURN ─────────────────────────────────────────
    # Percentage change in price from one day to the next
    # e.g. 0.02 means price went up 2% today
    df["Return"] = df["Close"].pct_change()

    # ── ATR (Average True Range) ─────────────────────────────
    # Measures market volatility — how much price moves daily
    # High ATR = very volatile stock, Low ATR = stable stock
    high_low   = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close  = (df["Low"]  - df["Close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["ATR"]  = true_range.rolling(14).mean()

    # Remove rows with NaN values created by rolling calculations
    df.dropna(inplace=True)

    return df
# ============================================================
# Test block — only runs when file is executed directly
# ============================================================
if __name__ == "__main__":
    from data.fetcher import fetch_stock_data

    # Fetch Apple data and add indicators
    df = fetch_stock_data("AAPL", period="6mo")
    df = add_indicators(df)

    # Print columns to confirm all indicators were added
    print(df.columns.tolist())
    print(df.tail())