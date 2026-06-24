import yfinance as yf
import pandas as pd
import time
import logging

# 設定日誌，方便在 GitHub Actions 的 Log 中排查問題
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_stock_data(ticker_symbol, retries=3, delay=2):
    """
    優化版：具備重試機制的資料獲取
    """
    for attempt in range(retries):
        try:
            # 使用 yf.download 獲取資料
            df = yf.download(ticker_symbol, period="1y", interval="1d", progress=False)
            
            if df.empty:
                return None
            
            # 處理 MultiIndex (確保資料結構扁平化)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            return df
            
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"下載 {ticker_symbol} 失敗 (嘗試 {attempt+1}/{retries})，稍後重試... 錯誤: {e}")
                time.sleep(delay) # 等待 2 秒後重試
            else:
                logging.error(f"下載 {ticker_symbol} 最終失敗: {e}")
                return None
    return None

def calculate_volume_in_lots(df):
    """
    計算成交量 (單位：張)
    """
    try:
        if df is not None and not df.empty and 'Volume' in df.columns:
            # 取得最後一筆成交量 / 1000
            return float(df['Volume'].iloc[-1]) / 1000
    except Exception as e:
        logging.error(f"計算成交量失敗: {e}")
    return 0