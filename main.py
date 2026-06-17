import json
import time
import logging
from tqdm import tqdm
from data_fetcher import get_daily_data, get_daily_volume
from scanner import check_bearish_shooting_star

# 隱藏 yfinance 的警告訊息
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

def main():
    # 1. 讀取 stocks.json 清單
    try:
        with open("stocks.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            stocks = data["watchlist"]
    except FileNotFoundError:
        print("找不到 stocks.json，請先執行 generate_watchlist.py")
        return
    
    print(f"DayTraderPro 啟動！開始掃描 {len(stocks)} 檔股票...")

    candidates = []  # 用來儲存所有找到的潛力股

    # 2. 開始掃描每檔股票
    for symbol in tqdm(stocks, desc="掃描中"):
        try:
            # 檢查成交量
            volume = get_daily_volume(symbol)
            if volume < 1000:
                continue 

            # 抓取日線資料
            df = get_daily_data(symbol)
            
            # 接收 scanner 回傳的詳細數據 (如果是字典則代表符合條件)
            result = check_bearish_shooting_star(df, period=10)
            
            if result:
                # 將這檔股票的資訊整合在一起
                entry = {
                    "symbol": symbol,
                    "volume": round(volume, 0),
                    "stop_loss": result["stop_loss"],
                    "reference_close": result["reference_close"],
                    "shadow_ratio": result["shadow_ratio"]
                }
                candidates.append(entry)
                tqdm.write(f"!!! 發現目標: {symbol} | 停損參考: {result['stop_loss']}")
            
            time.sleep(0.5) 
            
        except Exception:
            continue

    # 3. 將篩選出的股票存成 candidates.json
    with open("candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=4, ensure_ascii=False)
    
    print(f"\n掃描完成！共找到 {len(candidates)} 檔股票符合條件。")
    print("結果已儲存至 candidates.json，請在明日開盤前參考此清單。")

if __name__ == "__main__":
    main()