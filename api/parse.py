# api/parse.py
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
from src.parser import run_parser

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # читаем query и передаём в парсер через env (простая связка)
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            override = {
                "title": qs.get("title", [None])[0],
                "lang": qs.get("lang", [None])[0],
                "manga_id": qs.get("manga_id", [None])[0],
            }
            os.environ["PARSER_QUERY_JSON"] = json.dumps({k:v for k,v in override.items() if v})

            result = run_parser()
            status = 200 if result.get("ok") else 500
        except Exception as e:
            result = {"ok": False, "error": str(e)}
            status = 500

        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
