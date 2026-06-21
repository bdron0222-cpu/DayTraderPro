import json
import pandas as pd
from data_fetcher import get_stock_data  # 已修正導入名稱
from scanner import check_bearish_shooting_star

def run_backtest(ticker, days_to_hold=3):
    """
    對單一股票進行歷史回測
    策略：出現訊號隔日開盤放空，持有 N 天後平倉
    """
    # 使用修正後的函數名稱
    df = get_stock_data(ticker) 
    if df is None or len(df) < 30: return None
    
    # 處理 MultiIndex (確保回測不報錯)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    results = []
    
    # 從第 20 天開始模擬 (確保均線指標足夠)
    for i in range(20, len(df) - days_to_hold - 1):
        # 模擬當下時間點
        df_slice = df.iloc[:i+1]
        
        # 檢查該天是否有訊號
        signal = check_bearish_shooting_star(df_slice, period=10)
        
        if signal:
            entry_price = df.iloc[i+1]['Open'] # 隔日開盤進場
            exit_idx = min(i + 1 + days_to_hold, len(df) - 1)
            exit_price = df.iloc[exit_idx]['Close'] # 持有 N 天後收盤平倉
            
            # 放空獲利計算: (進場 - 出場) / 進場
            pnl = (entry_price - exit_price) / entry_price
            
            # 扣除交易成本 (稅 0.3% + 手續費 0.1425%*2*打折 -> 約 0.6%)
            cost = 0.006
            results.append(pnl - cost)
            
    return results

# --- 主程式 ---
if __name__ == "__main__":
    with open("candidates.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)
    
    # 測試前 5 檔
    test_list = [c['symbol'] for c in candidates[:5]]
    print(f"開始回測: {test_list}")
    
    for symbol in test_list:
        pnl_list = run_backtest(symbol)
        if pnl_list:
            win_rate = len([x for x in pnl_list if x > 0]) / len(pnl_list)
            avg_pnl = sum(pnl_list) / len(pnl_list)
            print(f"[{symbol}] 觸發 {len(pnl_list)} 次 | 勝率: {win_rate:.2%} | 平均獲利: {avg_pnl:.2%}")
        else:
            print(f"[{symbol}] 無訊號觸發")