import json
from datetime import datetime
from src.parser import run_parser

def handler(request):
    try:
        result = run_parser()
        payload = {
            "ok": bool(result.get("ok")),
            "ts": datetime.utcnow().isoformat() + "Z",
            "result": result,
        }
        body = json.dumps(payload, ensure_ascii=False)
        return (200, {"Content-Type": "application/json"}, body)
    except Exception as e:
        body = json.dumps(
            {"ok": False, "error": str(e), "ts": datetime.utcnow().isoformat() + "Z"},
            ensure_ascii=False,
        )
        return (500, {"Content-Type": "application/json"}, body)
