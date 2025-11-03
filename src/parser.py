# src/parser.py
import os
import json
import requests
from datetime import datetime

API = "https://api.mangadex.org"

def _get(url: str, params: dict | None = None):
    resp = requests.get(url, params=params or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def search_manga_by_title(title: str) -> str | None:
    # Mangadex: order[relevance]=desc
    params = {
        "title": title,
        "limit": 1,
        "order[relevance]": "desc",
    }
    data = _get(f"{API}/manga", params)
    items = data.get("data", [])
    return items[0]["id"] if items else None

    def get_latest_chapter_id(manga_id: str, lang: str) -> str | None:
    """
    Берём не первую, а последнюю нормальную главу:
    - нужный язык
    - нет externalUrl
    - pages > 0
    """
    params = {
        "limit": 20,  # возьмём пачку, чтобы было из чего выбирать
        "translatedLanguage[]": lang,
        "order[chapter]": "desc",
        "order[createdAt]": "desc",
        # "includeExternalUrl": "0",  # если бы API принимал такой флаг — но фильтруем на клиенте
    }
    data = _get(f"{API}/manga/{manga_id}/feed", params)
    items = data.get("data", [])
    for it in items:
        attr = it.get("attributes", {}) if isinstance(it, dict) else {}
        # externalUrl отсутствует и есть страницы
        if not attr.get("externalUrl") and (attr.get("pages", 0) or 0) > 0:
            return it.get("id")
    # если не нашли — всё равно вернём самую верхнюю (как было), но это может дать пустые pages
    return items[0]["id"] if items else None

def get_chapter_images(chapter_id: str, use_data_saver: bool = True) -> list[str]:
    at = _get(f"{API}/at-home/server/{chapter_id}")
    base = at["baseUrl"]
    ch = at["chapter"]
    h = ch["hash"]
    files = ch["dataSaver"] if use_data_saver else ch["data"]
    kind = "data-saver" if use_data_saver else "data"
    return [f"{base}/{kind}/{h}/{name}" for name in files]

def run_parser():
    """
    Возвращает JSON: { ok, manga_id, chapter_id, lang, pages[], pages_count, ts }
    Управление:
      - env MANGA_TITLE или MANGA_ID
      - env MANGA_LANG (по умолчанию en)
      - query ?title=...&lang=...&manga_id=... (через api/parse.py)
    """
    title = os.getenv("MANGA_TITLE", "").strip()
    manga_id = os.getenv("MANGA_ID", "").strip()
    lang = os.getenv("MANGA_LANG", "en").strip().lower()

    # Оверрайды из api/parse (кладём в env для простоты связки)
    q = os.getenv("PARSER_QUERY_JSON")
    if q:
        try:
            override = json.loads(q)
            title = override.get("title") or title
            manga_id = override.get("manga_id") or manga_id
            lang = (override.get("lang") or lang).lower()
        except Exception:
            pass

    if not manga_id:
        if not title:
            return {"ok": False, "error": "Provide MANGA_TITLE or MANGA_ID"}
        manga_id = search_manga_by_title(title)
        if not manga_id:
            return {"ok": False, "error": f"No manga found for title: {title}"}

    chapter_id = get_latest_chapter_id(manga_id, lang)
    if not chapter_id:
        return {"ok": False, "error": f"No chapters found for manga={manga_id} lang={lang}"}

    pages = get_chapter_images(chapter_id, use_data_saver=True)
    return {
        "ok": True,
        "manga_id": manga_id,
        "chapter_id": chapter_id,
        "lang": lang,
        "pages": pages,
        "pages_count": len(pages),
        "ts": datetime.utcnow().isoformat() + "Z",
    }
