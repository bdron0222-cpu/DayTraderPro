import json
import pandas as pd
import requests
import io

def generate_stocks_json():
    # 上市 (2) 與 上櫃 (4) 的網址
    targets = [
        {"url": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", "suffix": ".TW"},
        {"url": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4", "suffix": ".TWO"}
    ]
    
    all_watchlist = []
    
    print("正在下載上市與上櫃股票清單...")
    
    for target in targets:
        response = requests.get(target['url'])
        response.encoding = 'big5'
        
        dfs = pd.read_html(io.StringIO(response.text))
        
        # 尋找目標表格
        target_df = None
        for df in dfs:
            if "有價證券代號及名稱" in df.iloc[0].values:
                target_df = df
                break
        
        if target_df is None:
            continue
            
        target_df.columns = target_df.iloc[0]
        target_df = target_df[1:]
        
        # 提取代號
        target_df['code'] = target_df['有價證券代號及名稱'].astype(str).str.split().str[0]
        
        for code in target_df['code']:
            if not code.isdigit(): continue
            
            # 篩選邏輯：長度4位，排除 ETF/權證/REITs
            if len(code) == 4 and not code.startswith(('00', '02', '01', '9')):
                all_watchlist.append(f"{code}{target['suffix']}")
            
    # 存檔
    with open("stocks.json", "w", encoding="utf-8") as f:
        json.dump({"watchlist": all_watchlist}, f, ensure_ascii=False, indent=4)
        
    print(f"優化完成！已合併上市與上櫃，共 {len(all_watchlist)} 檔。")

if __name__ == "__main__":
    generate_stocks_json()