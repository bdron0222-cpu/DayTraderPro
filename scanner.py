import pandas as pd

# --- 通用指標計算 ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    avg_gain = (delta.where(delta > 0, 0)).ewm(com=period - 1, min_periods=period).mean()
    avg_loss = (-delta.where(delta < 0, 0)).ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# --- 策略：射擊之星 ---
def check_bearish_shooting_star(df):
    if df.empty or len(df) < 30: return None
    last, prev = df.iloc[-1], df.iloc[-2]
    
    is_high = last['High'] == df['High'].rolling(window=10).max().iloc[-1]
    is_green = last['Close'] < last['Open']
    upper_shadow = last['High'] - max(last['Open'], last['Close'])
    body = abs(last['Open'] - last['Close'])
    
    is_gap_up = last['Open'] > prev['Close']
    rsi = calculate_rsi(df['Close'], 14).iloc[-1]
    vol_max = df['Volume'].rolling(window=10).max().iloc[-2]
    
    if is_high and is_green and (upper_shadow > body * 0.5) and is_gap_up and (rsi > 70) and (last['Volume'] < vol_max):
        return {"stop_loss": round(last['High'], 2), "reference_close": round(last['Close'], 2), "shadow_ratio": round(upper_shadow/body, 2), "rsi": round(rsi, 2)}
    return None

# --- 策略：均線破位 (MA Breakdown) ---
def check_ma_breakdown(df):
    if df.empty or len(df) < 25: return None
    
    ma20 = df['Close'].rolling(window=20).mean()
    last_close = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    
    # 跌破 20 日均線
    is_breaking_ma20 = (prev_close > ma20.iloc[-2]) and (last_close < ma20.iloc[-1])
    # RSI 動能轉弱
    rsi = calculate_rsi(df['Close'], 14).iloc[-1]
    
    if is_breaking_ma20 and rsi < 50:
        return {"stop_loss": round(ma20.iloc[-1], 2), "reference_close": round(last_close, 2), "shadow_ratio": 0, "rsi": round(rsi, 2)}
    return None

# --- 策略分派器 (Main Entry Point) ---
def scan_stock(df, strategy):
    if strategy == "shooting_star":
        return check_bearish_shooting_star(df)
    elif strategy == "ma_breakdown":
        return check_ma_breakdown(df)
    return None