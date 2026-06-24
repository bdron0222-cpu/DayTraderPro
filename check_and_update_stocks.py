import os
import json
import datetime
from generate_watchlist import generate_stocks_json

# 設定檔案路徑
META_FILE = "update_metadata.json"
TARGET_FILE = "stocks.json"
UPDATE_INTERVAL_DAYS = 90

def get_last_update_date():
    """從 metadata 檔案讀取上次更新日期"""
    if not os.path.exists(META_FILE):
        return None
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return datetime.datetime.fromisoformat(data["last_update"]).date()
    except (json.JSONDecodeError, KeyError, ValueError):
        return None

def save_update_date():
    """將今日日期寫入 metadata 檔案"""
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_update": datetime.date.today().isoformat()}, f)

def update_stocks_if_needed():
    last_date = get_last_update_date()
    today = datetime.date.today()
    
    # 判斷邏輯
    needs_update = False
    
    # 情境 1: 檔案不存在，或沒有 metadata 紀錄 (首次執行)
    if not os.path.exists(TARGET_FILE) or last_date is None:
        print("查無更新紀錄或股票清單，強制執行首次更新...")
        needs_update = True
    else:
        # 情境 2: 檢查是否超過 90 天
        days_passed = (today - last_date).days
        if days_passed >= UPDATE_INTERVAL_DAYS:
            print(f"清單已超過 {days_passed} 天，執行更新...")
            needs_update = True
        else:
            print(f"清單尚新 ({days_passed} 天)，無需更新。")
    
    # 執行更新
    if needs_update:
        try:
            generate_stocks_json()
            save_update_date()
            print("更新完成並記錄日期。")
        except Exception as e:
            print(f"更新過程中發生錯誤: {e}")

if __name__ == "__main__":
    update_stocks_if_needed()