import json
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1beta'})

class FinalDecision(BaseModel):
    action: str = Field(description="Must be 'BUY', 'SELL', or 'HOLD'. If confidence < 60, force 'HOLD'")
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    summary: str

STABLE_MODELS = ['gemini-3.1-flash-lite', 'gemini-3.1-flash', 'gemini-3.5-flash', 'gemini-3-flash']

def request_agent(system_instruction: str, context: str, is_json: bool = False) -> str:
    for model in STABLE_MODELS:
        try:
            time.sleep(1)
            # Инструкция для агентов: строго без Markdown
            instr = f"{system_instruction} Пиши строго без спецсимволов, звездочек и Markdown. Только чистый текст."
            config = {"system_instruction": instr}
            if is_json:
                config.update({"response_mime_type": "application/json", "response_schema": FinalDecision})
            
            resp = client.models.generate_content(model=model, contents=context, config=types.GenerateContentConfig(**config))
            return resp.text
        except: continue
    raise RuntimeError("Все модели заняты")

def run_ai_consilium(data: str) -> dict:
    quant = request_agent("Ты Квант. Дай только цифры и направление тренда.", data)
    risk = request_agent("Ты Риск-Менеджер. Дай критические уровни. Без звездочек.", f"Рынок: {data}\nКвант: {quant}")
    # Управляющий теперь обязан соблюдать фильтр уверенности
    manager = request_agent("Ты Директор. Если уверенность ниже 60, ставь HOLD.", f"Анализ: {quant}\nРиск: {risk}", is_json=True)
    return {"quant": quant, "risk": risk, "decision": json.loads(manager)}
