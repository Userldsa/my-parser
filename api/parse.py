# api/parse.py — минимальный sanity-check
def handler(request):
    # Возвращаем валидный ответ без импорта чего-либо
    body = '{"ok": true, "stage": "ping"}'
    return 200, {"Content-Type": "application/json"}, body
