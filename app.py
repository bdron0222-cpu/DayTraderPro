import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="DayTraderPro Dashboard", layout="wide")
st.title("📈 DayTraderPro 選股雷達")

try:
    # 讀取掃描結果
    with open("candidates.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data:
        df = pd.DataFrame(data)
        # 設定顯示格式
        st.dataframe(df, use_container_width=True)
        st.success(f"目前共篩選出 {len(df)} 檔潛力股")
    else:
        st.info("今日無符合條件的股票。")
        
except FileNotFoundError:
    st.error("找不到 candidates.json，請確認掃描器是否已執行。")

# 執行指令: streamlit run app.py