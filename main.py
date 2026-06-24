import json
import logging
import argparse
import concurrent.futures
from tqdm import tqdm
from data_fetcher import get_stock_data, calculate_volume_in_lots
from scanner import scan_stock  # 確保 scanner.py 已經更新為有 scan_stock 的版本

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_stock(symbol, strategy):
    """
    單一股票處理函式
    """
    try:
        # 1. 下載資料
        df = get_stock_data(symbol)
        if df is None or df.empty:
            return None

        # 2. 計算成交量
        volume = calculate_volume_in_lots(df)
        if volume < 1000:
            return None

        # 3. 呼叫策略分派器 (傳入策略名稱)
        result = scan_stock(df, strategy)
        
        # 4. 回傳結果
        if result:
            return {
                "symbol": symbol,
                "volume": round(volume, 0),
                "stop_loss": result["stop_loss"],
                "reference_close": result["reference_close"],
                "shadow_ratio": result["shadow_ratio"],
                "rsi": result["rsi"]
            }
    except Exception:
        return None
    return None

def main():
    # 設定參數解析器
    parser = argparse.ArgumentParser(description="DayTraderPro Scanner")
    parser.add_argument("--strategy", choices=["shooting_star", "ma_breakdown"], required=True, help="選擇要執行的策略")
    parser.add_argument("--output", required=True, help="指定輸出的 JSON 檔名")
    args = parser.parse_args()

    # 讀取清單
    try:
        with open("stocks.json", "r", encoding="utf-8") as f:
            stocks = json.load(f)["watchlist"]
    except Exception as e:
        logging.error(f"讀取 stocks.json 失敗: {e}")
        return
    
    print(f"🚀 DayTraderPro 啟動！")
    print(f"模式: {args.strategy} | 輸出: {args.output} | 掃描 {len(stocks)} 檔股票...")

    candidates = []

    # 使用執行緒池
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        # 傳入 strategy 參數
        future_to_symbol = {executor.submit(process_stock, s, args.strategy): s for s in stocks}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_symbol), total=len(stocks), desc="掃描中"):
            res = future.result()
            if res:
                candidates.append(res)
                tqdm.write(f"!!! 發現目標: {res['symbol']} | RSI: {res['rsi']} | 停損: {res['stop_loss']}")

    # 存檔保護機制：有結果才寫入，避免檔案被清空
    if len(candidates) > 0:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=4, ensure_ascii=False)
        print(f"\n🎉 掃描完成！共找到 {len(candidates)} 檔，已儲存至 {args.output}")
    else:
        logging.warning(f"\n⚠️ 本次掃描未發現標的，保留舊有 {args.output} 檔案。")

if __name__ == "__main__":
    main()