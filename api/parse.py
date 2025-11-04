# api/parse.py — минимальный, двуядерный (dual) хендлер
import json

def _send_tuple(payload: dict):
    return 200, {"Content-Type": "application/json"}, json.dumps(payload, ensure_ascii=False)

def handler(request, response=None):
    """
    Совместим с двумя вариантами рантайма:
    - старый: handler(request) -> (status, headers, body)
    - новый: handler(request, response); нужно вызывать методы response
    """
    payload = {"ok": True, "stage": "ping-dual"}

    # Если Vercel передал response-объект — используем его API
    if response is not None:
        # Попытка работать с разными вариантами API
        try:
            # вариант 1: у response есть методы set_header / status / send
            if hasattr(response, "set_header"):
                response.set_header("Content-Type", "application/json")
            if hasattr(response, "status"):
                response.status(200)
            # send / end — у разных билдов по-разному называются
            if hasattr(response, "send"):
                return response.send(json.dumps(payload, ensure_ascii=False))
            if hasattr(response, "end"):
                return response.end(json.dumps(payload, ensure_ascii=False))
        except Exception:
            # fallback в кортеж
            return _send_tuple(payload)

    # Старый формат — возвращаем кортеж
    return _send_tuple(payload)
