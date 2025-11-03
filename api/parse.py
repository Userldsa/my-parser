import json
from http.server import BaseHTTPRequestHandler
from src.parser import run_parser

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            result = run_parser()                      # твоя логика парсера
            status = 200 if result.get("ok") else 500
        except Exception as e:
            # Временная отладка: покажем ошибку в ответе
            result = {"ok": False, "error": str(e)}
            status = 500

        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
