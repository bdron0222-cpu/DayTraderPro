import json
import pandas as pd
import requests
import io

def generate_stocks_json():
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    print("正在下載資料，請稍候...")
    
    # 1. 使用 requests 下載網頁內容
    response = requests.get(url)
    response.encoding = 'big5'
    
    # 2. 直接使用 pandas 讀取網頁表格
    # 證交所這頁表格結構比較複雜，我們讀取所有表格，然後找包含「有價證券代號」的那一張
    dfs = pd.read_html(io.StringIO(response.text))
    
    # 3. 自動搜尋含有股票資料的正確表格
    target_df = None
    for df in dfs:
        if "有價證券代號及名稱" in df.iloc[0].values:
            target_df = df
            break
            
    if target_df is None:
        print("錯誤：找不到正確的表格，請檢查網址或網頁結構。")
        return

    # 4. 清理表格：設標頭、去除無效行
    target_df.columns = target_df.iloc[0]
    target_df = target_df[1:]
    
    # 5. 提取代號 (將 "2330 臺積電" 切割出 "2330")
    # 先將該欄位轉為字串避免錯誤
    target_df['code'] = target_df['有價證券代號及名稱'].astype(str).str.split().str[0]
    
    # 6. 嚴格篩選
    watchlist = []
    for code in target_df['code']:
        # 排除非數字的項目 (例如標題列)
        if not code.isdigit():
            continue
            
        # 篩選規則：
        # - 長度必須是 4 位數
        # - 不以 00 (ETF), 02 (ETN), 01 (REITs), 9 (TDR) 開頭
        if len(code) == 4 and not code.startswith(('00', '02', '01', '9')):
            watchlist.append(f"{code}.TW")
            
    # 7. 存檔
    with open("stocks.json", "w", encoding="utf-8") as f:
        json.dump({"watchlist": watchlist}, f, ensure_ascii=False, indent=4)
        
    print(f"成功！已產生 stocks.json，共 {len(watchlist)} 檔股票。")

if __name__ == "__main__":
    generate_stocks_json()