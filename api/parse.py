# api/parse.py — минимальный пинг с явным лог-маркером
import json, os, sys, time

MARKER = f"[PING-{int(time.time())}] api/parse invoked"

def _tuple(payload: dict):
    return 200, {"Content-Type": "application/json"}, json.dumps(payload, ensure_ascii=False)

def handler(request, response=None):
    # ЯВНО пишем в stdout — это должно попасть в Runtime Logs
    try:
        print(MARKER)
    except Exception:
        pass

    payload = {
        "ok": True,
        "stage": "ping-marker",
        "marker": MARKER,
    }

    # Новый формат (есть response-объект)
    if response is not None:
        try:
            if hasattr(response, "set_header"):
                response.set_header("Content-Type", "application/json")
            if hasattr(response, "status"):
                response.status(200)
            body = json.dumps(payload, ensure_ascii=False)
            if hasattr(response, "send"):
                return response.send(body)
            if hasattr(response, "end"):
                return response.end(body)
        except Exception:
            return _tuple(payload)

    # Старый формат — вернуть кортеж
    return _tuple(payload)
