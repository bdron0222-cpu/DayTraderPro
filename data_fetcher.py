import yfinance as yf

def get_daily_data(ticker_symbol):
    """
    抓取指定股票的日線資料 (下載過去 1 年，確保技術指標計算無誤)
    """
    ticker = yf.Ticker(ticker_symbol)
    # interval='1d' 為日線，period='1y' 抓取一年資料讓指標計算更精確
    df = ticker.history(period="1y", interval="1d")
    return df

def get_daily_volume(ticker_symbol):
    """
    快速抓取當日累積成交量 (單位：張數)
    """
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="1d")
    
    if not df.empty:
        return df['Volume'].iloc[-1] / 1000
    return 0