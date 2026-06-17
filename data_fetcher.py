import yfinance as yf
import pandas as pd

def get_stock_data(ticker_symbol):
    """
    優化版：一次下載，同時提供完整資料與成交量
    這樣做可以減少 50% 的網路請求次數
    """
    try:
        # 使用 yf.download 比 yf.Ticker 更快且適合批次處理
        # progress=False 關閉進度條，保持終端機乾淨
        df = yf.download(ticker_symbol, period="1y", interval="1d", progress=False)
        
        if df.empty:
            return None
        
        # 確保資料結構扁平化 (處理 MultiIndex 問題)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        # 靜默處理錯誤，記錄一下錯誤即可
        return None

def calculate_volume_in_lots(df):
    """
    直接從已下載的 DataFrame 計算成交量 (單位：張)
    不需要再呼叫 API
    """
    if df is not None and not df.empty and 'Volume' in df.columns:
        # 取得最後一筆成交量 / 1000
        return df['Volume'].iloc[-1] / 1000
    return 0