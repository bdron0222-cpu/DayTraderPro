import json
import logging
import concurrent.futures
from tqdm import tqdm
from data_fetcher import get_stock_data, calculate_volume_in_lots
from scanner import check_bearish_shooting_star

# 設定日誌，方便除錯
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_stock(symbol):
    """
    單一股票處理函式 (供多執行緒使用)
    """
    try:
        # 1. 下載資料 (這是優化後的 data_fetcher.py)
        df = get_stock_data(symbol)
        if df is None or df.empty:
            return None

        # 2. 計算成交量 (改從記憶體抓取，不耗網路)
        volume = calculate_volume_in_lots(df)
        if volume < 1000:
            return None

        # 3. 掃描條件
        result = check_bearish_shooting_star(df, period=10)
        
        if result:
            return {
                "symbol": symbol,
                "volume": round(volume, 0),
                "stop_loss": result["stop_loss"],
                "reference_close": result["reference_close"],
                "shadow_ratio": result["shadow_ratio"]
            }
    except Exception:
        return None
    return None

def main():
    # 讀取清單
    try:
        with open("stocks.json", "r", encoding="utf-8") as f:
            stocks = json.load(f)["watchlist"]
    except Exception as e:
        logging.error(f"讀取 stocks.json 失敗: {e}")
        return
    
    print(f"🚀 DayTraderPro 啟動！正在啟動多執行緒掃描 {len(stocks)} 檔股票...")

    candidates = []

    # 使用 ThreadPoolExecutor 同時處理多檔股票 (max_workers 建議設 10-20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        # 將任務提交給執行緒池
        future_to_symbol = {executor.submit(process_stock, symbol): symbol for symbol in stocks}
        
        # 使用 tqdm 監控進度
        for future in tqdm(concurrent.futures.as_completed(future_to_symbol), total=len(stocks), desc="掃描中"):
            res = future.result()
            if res:
                candidates.append(res)
                tqdm.write(f"!!! 發現目標: {res['symbol']} | 停損參考: {res['stop_loss']}")

    # 存檔
    with open("candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=4, ensure_ascii=False)
    
    print(f"\n🎉 掃描完成！共找到 {len(candidates)} 檔符合條件。")

if __name__ == "__main__":
    main()