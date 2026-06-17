# scanner.py

def check_bearish_shooting_star(df, period=10):
    """
    選股邏輯：
    1. 趨勢條件：收盤價 < 20日均線
    2. 型態條件：射擊之星 (短期高點 + 長上影線 + 綠柱)
    回傳：
        - 符合條件：回傳包含停損點與細節的字典
        - 不符合：回傳 None
    """
    # 安全檢查：若資料不足 20 天，無法計算均線，直接返回 None
    if df.empty or len(df) < 20:
        return None

    last = df.iloc[-1]
    
    # 1. 計算 20 日均線 (MA20)
    ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    # 2. 定義各項判斷條件
    is_down_trend = last['Close'] < ma20
    is_high = last['High'] == df['High'].rolling(window=period).max().iloc[-1]
    is_green = last['Close'] < last['Open']
    
    # 3. 計算上影線比例
    upper_shadow = last['High'] - max(last['Open'], last['Close'])
    body = abs(last['Open'] - last['Close'])
    # 檢查是否有實體，避免除以 0
    has_long_shadow = (body > 0) and (upper_shadow > (body * 1.5))
    
    # 如果條件全中，回傳關鍵交易數據
    if is_high and is_green and has_long_shadow and is_down_trend:
        return {
            "stop_loss": round(last['High'], 2),        # 停損參考價 (射擊之星最高點)
            "reference_close": round(last['Close'], 2), # 今日收盤價
            "shadow_ratio": round(upper_shadow / body, 2) # 上影線/實體比例
        }
    
    # 如果不符合條件，回傳 None
    return None