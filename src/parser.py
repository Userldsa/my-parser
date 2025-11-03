# src/parser.py
import os
import json
import requests
from datetime import datetime
from urllib.parse import urlencode

API = "https://api.mangadex.org"

def _get(url, **params):
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def search_manga_by_title(title: str):
    # берем самый релевантный результат
    data = _get(f"{API}/manga", title=title, limit=1, order__relevance="desc")
    results = data.get("data", [])
    return results[0]["id"] if results else None

def get_latest_chapter_id(manga_id: str, lang: str):
    # сортируем по убыванию номера главы; берём первую подходящую
    feed = _get(
        f"{API}/manga/{manga_id}/feed",
        limit=1,
        translatedLanguage[]=lang,
        order__chapter="desc",
        order__createdAt="desc",
        includes[]="scanlation_group"
    )
    items = feed.get("data", [])
    return items[0]["id"] if items else None

def get_chapter_images(chapter_id: str, use_data_saver: bool = True):
    # at-home сервер для выдачи картинок
    at = _get(f"{API}/at-home/server/{chapter_id}")
    base = at["baseUrl"]
    ch = at["chapter"]
    h = ch["hash"]
    files = ch["dataSaver"] if use_data_saver else ch["data"]
    prefix = "data-saver" if use_data_saver else "data"
    urls = [f"{base}/{prefix}/{h}/{name}" for name in files]
    return urls

def run_parser():
    """
    Возвращает JSON с метаданными манги, номером главы и ссылками на страницы.
    Настройки:
      - MANGA_TITLE (например: "Solo Leveling") ИЛИ MANGA_ID (mangadex id)
      - MANGA_LANG (например: "ru" или "en"), по умолчанию "en"
    Поддержка оверрайдов через query (?title=..., ?lang=...) реализована в api/parse.py.
    """
    title = os.getenv("MANGA_TITLE", "").strip()
    manga_id = os.getenv("MANGA_ID", "").strip()
    lang = os.getenv("MANGA_LANG", "en").strip().lower()

    # Если api/parse передал query-оверрайды, подхватим их
    # (api/parse положит их в переменную окружения PARSER_QUERY_JSON)
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

    chapter_id = get_latest_chapter_id(manga_id, lang=lang)
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
