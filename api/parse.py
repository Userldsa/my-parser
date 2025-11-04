# api/parse.py  — СМОУК-ТЕСТ
import json
from datetime import datetime

def _json(status: int, payload: dict):
    return status, {"Content-Type": "application/json"}, json.dumps(payload, ensure_ascii=False)

def handler(request):
    return _json(200, {
        "ok": True,
        "msg": "parse endpoint is alive",
        "ts": datetime.utcnow().isoformat() + "Z"
    })