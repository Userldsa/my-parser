# api/parse.py — сверх-диагностический хендлер
import os, sys, json, traceback, importlib
from datetime import datetime

# 1) гарантируем, что корень репозитория в sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))  # api/.. -> корень
if ROOT and ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def _json(status: int, payload: dict):
    body = json.dumps(payload, ensure_ascii=False)
    # Vercel нормально ест str, но на всякий печатаем в логи ещё и короче
    print(f"[RESP {status}] {body[:3000]}", flush=True)
    return status, {"Content-Type": "application/json"}, body

def _crash(tag: str, exc: BaseException):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    # печатаем в stdout и stderr, чтобы точно попало в Logs
    print(f"{tag}:\n{tb}", flush=True)
    sys.stderr.write(f"{tag} (stderr):\n{tb}\n")
    return _json(500, {"ok": False, "error": tag, "traceback": tb})

def handler(request):
    try:
        # — безопасная загрузка src.parser —
        try:
            parser_mod = importlib.import_module("src.parser")
        except Exception as e:
            return _crash("IMPORT_ERROR src.parser", e)

        if not hasattr(parser_mod, "run_parser"):
            return _json(500, {"ok": False, "error": "run_parser not found in src.parser"})

        run_parser = getattr(parser_mod, "run_parser")

        # — достаём query (Vercel Python кладёт их в request.get('query') / request.get('args')) —
        q = {}
        try:
            if isinstance(request, dict):
                q = request.get("query") or request.get("args") or {}
        except Exception:
            pass

        title = (q.get("title") or "").strip() or "Solo Leveling"
        lang  = (q.get("lang")  or "").strip() or "en"

        print(f"[CALL] run_parser(title={title!r}, lang={lang!r})", flush=True)

        try:
            result = run_parser(title=title, lang=lang)
        except Exception as e:
            return _crash("RUN_PARSER_ERROR", e)

        if not isinstance(result, dict):
            result = {"result": result}

        result.update({"ok": True, "ts": datetime.utcnow().isoformat() + "Z"})
        return _json(200, result)

    except Exception as e:
        return _crash("TOP_LEVEL_ERROR", e)
