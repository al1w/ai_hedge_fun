import requests
import time
from llm import run_ai_consilium
from binance_client import get_market_snapshot

TELEGRAM_TOKEN = "8875893969:AAHUqyg8G3gYO2MJzgAIc0rVoPr4SV9-WTo"
TELEGRAM_CHAT_ID = "1007661892"

WATCHLIST = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
TIMEFRAME = "15m"

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        res_json = response.json()
        # Если Telegram вернул ошибку, мы выведем её в консоль
        if not res_json.get("ok"):
            print(f"[Критическая Ошибка Telegram API]: {res_json.get('description')}")
        else:
            print("[Telegram]: Сообщение успешно доставлено на телефон директора!")
    except Exception as e:
        print(f"[Ошибка отправки Telegram]: {e}")

def run_market_scanner():
    print(f"[Команда ИИ]: Начинаем консилиум по рынку...")
    
    for symbol in WATCHLIST:
        try:
            raw_data = get_market_snapshot(symbol=symbol, timeframe=TIMEFRAME)
            if "Ошибка" in raw_data:
                print(f"[Биржа]: Не удалось получить данные для {symbol}")
                continue
                
            consilium = run_ai_consilium(raw_data)
            decision = consilium["decision"]
            
            status_emoji = "🟢" if decision["action"] == "BUY" else "🔴" if decision["action"] == "SELL" else "⚪"
            
            report = (
                f"📊 *КОНСИЛИУМ ИИ-КОМАНДЫ [{symbol}]*\n"
                f"===================================\n\n"
                f"📈 *Мнение Квант-Аналитика:* \n{consilium['quant']}\n\n"
                f"🛡️ *Замечания Риск-Менеджера:* \n{consilium['risk']}\n\n"
                f"===================================\n"
                f"💼 *ВЕРДИКТ УПРАВЛЯЮЩЕГО:* \n"
                f"• *Решение:* {status_emoji} {decision['action']}\n"
                f"• *Уверенность:* {decision['confidence']*100:.0f}%\n"
                f"• *Вход:* {decision['entry_price']} | *Тейк:* {decision['take_profit']} | *Стоп:* {decision['stop_loss']}\n\n"
                f"📝 *Резюме:* {decision['summary']}"
            )
            
            send_telegram_message(report)
            time.sleep(20) # Пауза 20 секунд между монетами для обнуления лимитов
            
        except Exception as e:
            print(f"[Ошибка консилиума по {symbol}]: {e}")
            time.sleep(10)
