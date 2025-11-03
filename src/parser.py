import os
from datetime import datetime
import requests
from urllib.parse import urlparse

def run_parser():
    url = os.getenv("TARGET_URL")
    if not url:
        return {"ok": False, "error": "TARGET_URL not set"}

    p = urlparse(url)
    if p.scheme not in {"http", "https"} or not p.netloc:
        return {"ok": False, "error": f"Invalid TARGET_URL: {url}"}

    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        return {
            "ok": 200 <= resp.status_code < 300,  # не бросаем исключение на 4xx/5xx
            "url": url,
            "status": resp.status_code,
            "bytes": len(resp.content),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e), "ts": datetime.utcnow().isoformat() + "Z"}
