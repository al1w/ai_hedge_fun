import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from binance_client import get_market_snapshot
from llm import run_ai_consilium
from telegram_bot import run_market_scanner

async def start_scheduled_scanner():
    while True:
        try:
            run_market_scanner()
        except Exception as e:
            print(f"[Критическая ошибка]: {e}")
        await asyncio.sleep(15 * 60) # Скан каждые 15 минут

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_scheduled_scanner())
    yield

app = FastAPI(title="AI Hedge Fund - Multi-Agent Core", version="4.0.0", lifespan=lifespan)

@app.post("/api/analyze/binance")
def analyze_binance(symbol: str = "BTC/USDT", timeframe: str = "15m"):
    try:
        raw_market_data = get_market_snapshot(symbol=symbol, timeframe=timeframe)
        if "Ошибка" in raw_market_data:
            raise HTTPException(status_code=400, detail=raw_market_data)
            
        # Запускаем мультиагентный спор
        team_result = run_ai_consilium(raw_market_data)
        return {"success": True, "team_discussion": team_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка мультиагентного ядра: {str(e)}")

@app.post("/api/scanner/force_run")
def force_run_scanner(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_market_scanner)
    return {"status": "Дискуссия агентов по всему вочлисту запущена!"}

from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running'

if __name__ == '__main__':
    app.run()
