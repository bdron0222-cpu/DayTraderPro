import streamlit as st
import pandas as pd
import json
import os
import datetime

# 設定網頁標題與排版
st.set_page_config(page_title="DayTraderPro", layout="wide")

# --- 側邊欄：資訊管理 ---
st.sidebar.title("🛠 設定與狀態")
if st.sidebar.button("🔄 重新載入最新數據"):
    st.rerun()

# 顯示最後更新時間 (對當沖非常重要，確認數據不是昨天的)
if os.path.exists("candidates.json"):
    mtime = os.path.getmtime("candidates.json")
    last_update = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    st.sidebar.write(f"最後掃描時間: {last_update}")
else:
    st.sidebar.warning("尚未偵測到資料")

st.title("📉 DayTraderPro 當沖做空雷達")

# --- 篩選條件區塊 ---
with st.expander("🔍 查看當沖做空篩選條件"):
    st.markdown("""
    系統採用 **射擊之星 (Shooting Star)** 空方策略：
    * **型態**: 上影線長度 > 實體長度 0.5 倍
    * **壓力位**: 10 日內高點
    * **控盤權**: 收盤 < 開盤 (綠K)
    """)

# --- 讀取並顯示資料 ---
if os.path.exists("candidates.json"):
    with open("candidates.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if data:
                df = pd.DataFrame(data)
                # 重新命名欄位並設定正確格式
                df.columns = ["股票代號", "成交量(張)", "停損參考價", "收盤價", "影線比例"]
                
                # --- 優化：專業儀表板顯示 ---
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "成交量(張)": st.column_config.NumberColumn("成交量(張)", format="%d"),
                        "停損參考價": st.column_config.NumberColumn("停損參考價", format="%.2f"),
                        "收盤價": st.column_config.NumberColumn("收盤價", format="%.2f"),
                        "影線比例": st.column_config.ProgressColumn("影線比例", format="%.2f", min_value=0, max_value=1)
                    }
                )
                
                # --- 優化：一鍵下載結果 ---
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載篩選清單 (CSV)",
                    data=csv,
                    file_name=f"daytrade_candidates_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
                
                st.success(f"目前共篩選出 {len(df)} 檔做空候選標的")
            else:
                st.info("今日無符合做空條件的股票。")
        except Exception as e:
            st.error(f"讀取錯誤: {e}")
else:
    st.warning("請先執行篩選腳本產生 candidates.json")