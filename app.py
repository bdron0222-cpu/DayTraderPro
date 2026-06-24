import streamlit as st
import pandas as pd
import json
import os
import datetime

# 設定網頁標題與排版
st.set_page_config(page_title="DayTraderPro", layout="wide")

# --- 資料讀取函數 ---
@st.cache_data(ttl=600) 
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not data:
                    return None
                df = pd.DataFrame(data)
                
                # 欄位名稱對應轉換
                rename_map = {
                    "symbol": "股票代號",
                    "volume": "成交量(張)",
                    "stop_loss": "停損參考價",
                    "reference_close": "收盤價",
                    "shadow_ratio": "影線比例",
                    "rsi": "RSI(14)"
                }
                df = df.rename(columns=rename_map)
                return df
            except Exception as e:
                st.error(f"讀取 {filename} 時發生錯誤: {e}")
                return None
    return None

# --- 側邊欄：資訊管理 ---
st.sidebar.title("🛠 設定與狀態")

# 1. 策略選擇器
strategy = st.sidebar.radio("選擇掃描策略", ["射擊之星", "均線破位"])

# 檔案對應表
file_map = {
    "射擊之星": "candidates_shooting_star.json",
    "均線破位": "candidates_ma_breakdown.json"
}
target_file = file_map[strategy]

# 2. 強制刷新按鈕
if st.sidebar.button("🔄 強制重新載入最新數據"):
    st.cache_data.clear() # 清除快取
    st.rerun()            # 強制重新執行

# 顯示最後更新時間
if os.path.exists(target_file):
    mtime = os.path.getmtime(target_file)
    last_update = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    st.sidebar.write(f"📂 更新時間: {last_update}")
else:
    st.sidebar.warning(f"尚未偵測到 {target_file}")

st.title(f"📉 DayTraderPro ({strategy})")

# --- 篩選條件說明 (動態顯示) ---
with st.expander("🔍 查看當沖做空篩選條件"):
    if strategy == "射擊之星":
        st.markdown("""
        **策略: 射擊之星 (Shooting Star)**
        * **型態**: 上影線長度 > 實體長度 0.5 倍
        * **壓力位**: 10 日內新高
        * **跳空**: 開盤價 > 昨日收盤
        * **RSI 確認**: **RSI(14) > 70** (超買區)
        * **量價背離**: 今日創新高但成交量萎縮
        """)
    else:
        st.markdown("""
        **策略: 均線破位 (MA Breakdown)**
        * **趨勢**: 股價跌破 20 日移動平均線 (MA20)
        * **動能**: RSI(14) < 50 (空方動能啟動)
        * **特徵**: 跌破關鍵支撐線，且成交量放大
        """)

# --- 讀取並顯示資料 ---
df = load_data(target_file)

if df is not None and not df.empty:
    # 預設排序 (根據策略特性)
    sort_col = "影線比例" if strategy == "射擊之星" else "股票代號"
    df = df.sort_values(by=sort_col, ascending=False)

    # 專業儀表板顯示
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "成交量(張)": st.column_config.NumberColumn("成交量(張)", format="%d"),
            "停損參考價": st.column_config.NumberColumn("停損參考價", format="%.2f"),
            "收盤價": st.column_config.NumberColumn("收盤價", format="%.2f"),
            "影線比例": st.column_config.ProgressColumn("影線比例", format="%.2f", min_value=0, max_value=1),
            "RSI(14)": st.column_config.NumberColumn("RSI(14)", format="%.1f")
        }
    )
    
    # 下載結果
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label=f"📥 下載 {strategy} 清單 (CSV)",
        data=csv,
        file_name=f"daytrade_{strategy}_{datetime.date.today()}.csv",
        mime="text/csv"
    )
    
    st.success(f"目前共篩選出 {len(df)} 檔做空候選標的")
else:
    st.info(f"今日 {strategy} 無符合條件標的或資料尚未產生。")