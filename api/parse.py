# api/parse.py — проверочный хендлер без импортов
def handler(request, response=None):
    body = "OK"
    headers = {"Content-Type": "text/plain; charset=utf-8"}

    # Если рантайм Vercel даёт объект response — попробуем им воспользоваться
    if response is not None:
        try:
            if hasattr(response, "set_header"):
                response.set_header("Content-Type", headers["Content-Type"])
            if hasattr(response, "status"):
                response.status(200)
            if hasattr(response, "send"):
                return response.send(body)
            if hasattr(response, "end"):
                return response.end(body)
        except Exception:
            pass

    # Универсальный возврат (подходит и для Vercel Python runtime)
    return 200, headers, body
