def handler(request):
    """
    Vercel Python Runtime ожидает функцию handler(request),
    которая возвращает кортеж:
      (status_code: int, headers: dict[str,str], body: str|bytes)
    """
    status = 200
    headers = {"Content-Type": "text/plain; charset=utf-8"}
    body = "OK"
    return status, headers, body
