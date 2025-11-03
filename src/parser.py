import requests
from datetime import datetime

def run_parser():
    # TODO: сюда добавишь настоящую логику парсинга
    # Для проверки вернём заглушку:
    return {"ok": True, "ts": datetime.utcnow().isoformat() + "Z"}
