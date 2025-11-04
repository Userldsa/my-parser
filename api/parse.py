# api/parse.py
import os
import sys
import json
from datetime import datetime

# добавить корень проекта в sys.path, чтобы импортировался src/
ROOT = os.path.dirname(os.path.dirname(__file__))  # .. от api -> корень
if ROOT and ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.parser import run_parser

def handler(request, response):
    try:
        # Собираем query-параметры (если есть) и пробрасываем в env,
        # чтобы src.parser.run_parser мог их прочитать
        q = {}
        try:
            # в Vercel Python request.args может отличаться, но есть fallback:
            if hasattr(request, "args") and request.args:
                for k in request.args:
                    q[k] = request.args.get(k)
            else:
                # на всякий случай разбор из URL
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(request.url)
                qs = parse_qs(parsed.query)
                for k, v in qs.items():
                    q[k] = v[0] if v else None
        except Exception:
            pass

        os.environ["PARSER_QUERY_JSON"] = json.dumps(q, ensure_ascii=False)

        from src.parser import run_parser
        payload = run_parser()
        # Если парсер вернул ok=False — отдадим 400/404, но НЕ уроним функцию
        if isinstance(payload, dict) and not payload.get("ok", False):
            body = json.dumps(payload, ensure_ascii=False)
            return response.status(400).header("Content-Type", "application/json").send(body)

        body = json.dumps(payload, ensure_ascii=False)
        return response.status(200).header("Content-Type", "application/json").send(body)
    except Exception as e:
        body = json.dumps(
            {"ok": False, "error": "handler_failed", "detail": str(e), "ts": datetime.utcnow().isoformat() + "Z"},
            ensure_ascii=False,
        )
        return response.status(500).header("Content-Type", "application/json").send(body)
