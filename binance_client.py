import ccxt
import pandas as pd

# Инициализируем клиент Binance. 
# Для публичных данных (получение свечей и RSI) API-ключи не требуются.
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future', # Работаем с фьючерсным рынком (можно поменять на 'spot')
    }
})

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Рассчитывает технический индикатор RSI"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def get_market_snapshot(symbol: str = 'BTC/USDT', timeframe: str = '15m') -> str:
    """Собирает рыночные данные и упаковывает в сырой текст для ИИ"""
    try:
        # Получаем последние 50 свечей
        bars = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
        
        # Формируем DataFrame
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Считаем RSI
        df = calculate_rsi(df)
        
        # Берем данные последней закрытой свечи
        last_bar = df.iloc[-1]
        prev_bar = df.iloc[-2]
        
        # Считаем изменение цены в процентах за последнюю свечу
        price_change = ((last_bar['close'] - prev_bar['close']) / prev_bar['close']) * 100
        
        # Формируем структурированную строку данных для отправки в Gemini
        market_data_text = (
            f"Инструмент: {symbol}\n"
            f"Таймфрейм: {timeframe}\n"
            f"Текущая цена закрытия: {last_bar['close']}\n"
            f"Изменение цены за свечу: {price_change:.2f}%\n"
            f"Объем торгов: {last_bar['volume']:.2f}\n"
            f"Индикатор RSI (14): {last_bar['rsi']:.2f}"
        )
        return market_data_text

    except Exception as e:
        return f"Ошибка при сборе данных с Binance: {str(e)}"
