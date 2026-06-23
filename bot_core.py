import telebot
import time
import threading
import csv
import os
from datetime import datetime
from binance_client import get_market_snapshot
from llm import run_ai_consilium

TOKEN = "8875893969:AAHUqyg8G3gYO2MJzgAIc0rVoPr4SV9-WTo"
MY_CHAT_ID = "1007661892"
LOG_FILE = "trades_log.csv"

# Инициализация файла логов, если его нет
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Symbol", "Action", "Conf", "Entry", "TP", "SL"])

bot = telebot.TeleBot(TOKEN)
WATCHLIST = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

def log_trade(symbol, d):
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), symbol, d['action'], d['confidence'], d['entry_price'], d['take_profit'], d['stop_loss']])

def get_report(symbol):
    data = get_market_snapshot(symbol=symbol, timeframe="15m")
    res = run_ai_consilium(data)
    d = res['decision']
    # Логируем, если это реальная торговая идея (не HOLD)
    if d['action'] != "HOLD":
        log_trade(symbol, d)
    return (
        f"--- {symbol.replace('/USDT', '')} ---\n"
        f"Вердикт: {d['action']} ({d['confidence']:.0f}%)\n"
        f"Вход: {d['entry_price']} | Тейк: {d['take_profit']} | Стоп: {d['stop_loss']}\n"
        f"Резюме: {d['summary'][:100]}"
    )

def auto_monitor():
    while True:
        try:
            time.sleep(1800)
            for sym in WATCHLIST:
                rep = get_report(sym)
                if "HOLD" not in rep:
                    bot.send_message(chat_id=MY_CHAT_ID, text=f"Авто-отчет:\n{rep}")
        except: time.sleep(60)

@bot.message_handler(func=lambda message: True)
def handle(message):
    sym = f"{message.text.upper().strip()}/USDT"
    if any(coin in sym for coin in ["BTC", "ETH", "SOL"]):
        msg = bot.reply_to(message, "⏳ Анализ...")
        try:
            bot.edit_message_text(get_report(sym), chat_id=message.chat.id, message_id=msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"Ошибка: {str(e)[:50]}", chat_id=message.chat.id, message_id=msg.message_id)

threading.Thread(target=auto_monitor, daemon=True).start()
print("Штаб онлайн. Логирование включено...")
bot.infinity_polling()
