# scanner.py

def check_bearish_shooting_star(df, period=10):
    """
    選股邏輯 (鬆綁版)：
    1. 短期高點：當前最高價是過去 N 天的最高點
    2. 綠柱形態：收盤價 < 開盤價
    3. 長上影線：上影線長度 > 實體長度的 0.5 倍 (鬆綁門檻)
    回傳：
        - 符合條件：回傳包含停損點與細節的字典
        - 不符合：回傳 None
    """
    # 安全檢查：若資料不足，無法判定趨勢或高點，直接返回 None
    if df.empty or len(df) < period:
        return None

    last = df.iloc[-1]
    
    # 1. 短期高點 (過去 period 天內最高)
    is_high = last['High'] == df['High'].rolling(window=period).max().iloc[-1]
    
    # 2. 綠柱 (收盤 < 開盤)
    is_green = last['Close'] < last['Open']
    
    # 3. 計算上影線比例 (鬆綁為 0.5 倍)
    upper_shadow = last['High'] - max(last['Open'], last['Close'])
    body = abs(last['Open'] - last['Close'])
    
    # 檢查是否有實體，避免除以 0
    # 將倍數從 1.5 改為 0.5，讓更多射擊之星型態能被抓到
    has_long_shadow = (body > 0) and (upper_shadow > (body * 0.5))
    
    # 只要滿足上述三條件即回傳
    if is_high and is_green and has_long_shadow:
        return {
            "stop_loss": round(last['High'], 2),        # 停損參考價
            "reference_close": round(last['Close'], 2), # 今日收盤價
            "shadow_ratio": round(upper_shadow / body, 2) # 上影線比例
        }
    
    return None