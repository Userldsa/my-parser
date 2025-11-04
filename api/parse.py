# api/parse.py
import os
import sys
import json
import traceback
from datetime import datetime

# 1) Добавим корень репозитория в sys.path (api/.. -> корень)
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT and ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def _json(status: int, payload: dict):
    return status, {"Content-Type": "application/json"}, json.dumps(payload, ensure_ascii=False)

def handler(request):
    try:
        # 2) Импорт внутри try — чтобы ImportError/SyntaxError попали в ответ и логи
        from src.parser import run_parser

        # 3) Достаём query-параметры (поддержка разных форматов запроса)
        q = {}
        if isinstance(request, dict):
            q = request.get("query") or request.get("args") or {}
        title = (q.get("title") or "").strip() or "Solo Leveling"
        lang  = (q.get("lang")  or "").strip() or "en"

        # 4) Запускаем парсер
        result = run_parser(title=title, lang=lang)
        if not isinstance(result, dict):
            result = {"result": result}

        result.update({"ok": True, "ts": datetime.utcnow().isoformat() + "Z"})
        return _json(200, result)

    except Exception:
        tb = traceback.format_exc()
        # Полный трейc попадёт в Runtime Logs Vercel
        print(tb, flush=True)
        return _json(500, {"ok": False, "error": "exception", "traceback": tb})
