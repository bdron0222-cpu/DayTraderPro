import streamlit as st
import pandas as pd
import json
import os

# 設定網頁標題與排版
st.set_page_config(page_title="DayTraderPro", layout="wide")
st.title("📈 DayTraderPro 選股雷達")

# --- 新增：顯示篩選條件區塊 ---
with st.expander("🔍 查看目前的篩選條件"):
    st.markdown("""
    系統目前使用以下條件進行掃描 (射擊之星策略)：
    * **型態**: 射擊之星 (Shooting Star)
    * **短期高點**: 當前最高價為過去 **10 天內最高**
    * **K 線形態**: 收盤價 < 開盤價 (綠柱)
    * **影線要求**: 上影線長度 > 實體長度的 **0.5 倍** (已放寬)
    * **趨勢過濾**: 目前無強制過濾 (掃描全市場)
    """)

# --- 讀取資料並顯示 ---
# 確認 candidates.json 是否存在
if os.path.exists("candidates.json"):
    with open("candidates.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if data:
                # 將 JSON 資料轉為表格
                df = pd.DataFrame(data)
                
                # 調整欄位名稱，讓表格顯示中文標題
                df.columns = ["股票代號", "成交量(張)", "停損參考價", "收盤價", "影線比例"]
                
                # 顯示表格
                st.dataframe(df, use_container_width=True)
                st.success(f"目前共篩選出 {len(df)} 檔潛力股")
            else:
                st.info("今日無符合條件的股票。")
        except json.JSONDecodeError:
            st.error("讀取資料格式有誤，請檢查檔案內容。")
else:
    st.warning("掃描結果檔案尚未準備好，請稍候 GitHub Actions 更新。")