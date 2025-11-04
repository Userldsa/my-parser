# src/parser.py — минимальная заглушка
from datetime import datetime

def run_parser(title: str = "Solo Leveling", lang: str = "en"):
    # просто вернём что-то, чтобы проверить импорт и вызов
    return {
        "received_title": title,
        "received_lang": lang,
        "note": "stub run_parser ok",
        "now": datetime.utcnow().isoformat() + "Z",
    }
