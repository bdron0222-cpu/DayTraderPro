import pandas as pd

def check_bearish_shooting_star(df, period=10):
    """
    優化版選股邏輯：
    1. 形態濾網：符合射擊之星型態
    2. 成交量濾網：成交量需大於過去 5 日平均 (爆量才具備出貨意義)
    3. 缺口濾網：開盤需高於昨日收盤 (代表主力嘗試做多後失敗)
    """
    # 處理多層索引 (確保資料結構一致)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or len(df) < period + 1:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2] # 昨日收盤價

    # 1. 形態濾網：短期高點 + 綠K + 長上影線
    is_high = last['High'] == df['High'].rolling(window=period).max().iloc[-1]
    is_green = last['Close'] < last['Open']
    
    upper_shadow = last['High'] - max(last['Open'], last['Close'])
    body = abs(last['Open'] - last['Close'])
    # 確保有實體，避免除以 0；上影線 > 實體 0.5 倍
    has_long_shadow = (body > 0) and (upper_shadow > (body * 0.5))

    # --- 【優化 1】：新增成交量濾網 (Volume Spike) ---
    # 爆量才代表有主力在「出貨」，冷門股的射擊之星沒有參考價值
    avg_volume = df['Volume'].rolling(window=5).mean().iloc[-1]
    is_volume_spike = last['Volume'] > (avg_volume * 1.05) # 當日成交量 > 5日平均的 1.05 倍

    # --- 【優化 2】：新增跳空濾網 (Gap Up) ---
    # 若開盤沒高於昨日收盤，不算主力「強勢進攻後失敗」，就不符合射擊之星原意
    is_gap_up = last['Open'] > prev['Close']

    # 綜合判斷 (三個濾網全過才進場)
    if is_high and is_green and has_long_shadow and is_volume_spike and is_gap_up:
        return {
            "stop_loss": round(last['High'], 2),
            "reference_close": round(last['Close'], 2),
            "shadow_ratio": round(upper_shadow / body, 2)
        }
    
    return None