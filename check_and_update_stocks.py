import os
import time
from generate_watchlist import generate_stocks_json # 假設你的產生函數在這裡

def update_stocks_if_needed():
    file_path = "stocks.json"
    
    # 如果檔案不存在，直接更新
    if not os.path.exists(file_path):
        print("清單不存在，正在下載...")
        generate_stocks_json()
        return

    # 檢查檔案最後修改時間
    last_mod = os.path.getmtime(file_path)
    days_passed = (time.time() - last_mod) / (60 * 60 * 24)
    
    # 90 天檢查
    if days_passed > 90:
        print(f"清單已超過 {int(days_passed)} 天，執行更新...")
        generate_stocks_json()
    else:
        print(f"清單尚新 ({int(days_passed)} 天)，無需更新。")

if __name__ == "__main__":
    update_stocks_if_needed()