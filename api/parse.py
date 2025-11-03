from datetime import datetime

def handler(request):
    body = f'{{"ok": true, "ts": "{datetime.utcnow().isoformat()}Z"}}'
    return (200, {"Content-Type": "application/json"}, body)
