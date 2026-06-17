import streamlit as st
import pandas as pd
import json
import os

# 設定網頁標題與排版
st.set_page_config(page_title="DayTraderPro", layout="wide")
st.title("📉 DayTraderPro 當沖做空雷達")

# --- 修改：顯示篩選條件區塊 (改為做空導向) ---
with st.expander("🔍 查看當沖做空篩選條件"):
    st.markdown("""
    系統目前使用以下條件進行掃描 (空方射擊之星策略)：
    * **策略方向**: 當沖做空 (Short Selling)
    * **型態**: 射擊之星 (Shooting Star) - 代表多方攻勢遇阻，賣壓湧現
    * **短期高點**: 當前最高價為過去 **10 天內最高** (主力測試壓力位)
    * **K 線形態**: 收盤價 < 開盤價 (綠柱，空方取得控盤權)
    * **影線要求**: 上影線長度 > 實體長度的 **0.5 倍** (上影線越長，壓力越強)
    * **趨勢過濾**: 目前無強制過濾 (掃描全市場，建議優先挑選整體漲幅過大標的)
    """)

# --- 讀取資料並顯示 ---
if os.path.exists("candidates.json"):
    with open("candidates.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if data:
                df = pd.DataFrame(data)
                
                # 調整欄位名稱
                df.columns = ["股票代號", "成交量(張)", "停損參考價", "收盤價", "影線比例"]
                
                # 顯示表格
                st.dataframe(df, use_container_width=True)
                st.success(f"目前共篩選出 {len(df)} 檔做空候選標的")
            else:
                st.info("今日無符合做空條件的股票。")
        except json.JSONDecodeError:
            st.error("讀取資料格式有誤，請檢查檔案內容。")
else:
    st.warning("掃描結果檔案尚未準備好，請稍候 GitHub Actions 更新。")