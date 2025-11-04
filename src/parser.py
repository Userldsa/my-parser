# src/parser.py
import os
import json
import requests
from datetime import datetime

API = "https://api.mangadex.org"


def _get(url, params=None):
    params = params or {}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def search_manga_by_title(title):
    # Ищем тайтл и берём самый релевантный
    params = {
        "title": title,
        "limit": 1,
        "order[relevance]": "desc",
    }
    data = _get(API + "/manga", params)
    items = data.get("data") or []
    if items:
        first = items[0]
        # в манга-декс id в корне объекта
        return first.get("id")
    return None


def get_latest_chapter_id(manga_id, lang):
    """
    Берём свежую главу С КАРТИНКАМИ:
    - язык = lang
    - без externalUrl
    - pages > 0
    Просматриваем пачку, чтобы отфильтровать «внешние» главы.
    """
    params = {
        "limit": 40,  # побольше, чтобы наверняка нашлась нормальная
        "translatedLanguage[]": lang,
        "order[chapter]": "desc",
        "order[createdAt]": "desc",
        "includes[]": "scanlation_group",
    }
    data = _get(f"{API}/manga/{manga_id}/feed", params)
    items = data.get("data") or []

    for it in items:
        attr = (it.get("attributes") or {}) if isinstance(it, dict) else {}
        # исключаем внешние главы и пустые
        if not attr.get("externalUrl") and (attr.get("pages") or 0) > 0:
            return it.get("id")

    # если вдруг ни одной подходящей — вернём верхнюю (страницы могут отсутствовать)
    return items[0].get("id") if items and isinstance(items[0], dict) else None


def get_chapter_images(chapter_id, use_data_saver=True):
    # Получаем список файлов и собираем абсолютные урлы
    at = _get(f"{API}/at-home/server/{chapter_id}")
    base = at.get("baseUrl")
    ch = at.get("chapter") or {}
    h = ch.get("hash")
    if not base or not h:
        return []
    files = ch.get("dataSaver") if use_data_saver else ch.get("data")
    files = files or []
    kind = "data-saver" if use_data_saver else "data"
    return [f"{base}/{kind}/{h}/{name}" for name in files]


def run_parser():
    """
    Возвращает JSON: { ok, manga_id, chapter_id, lang, pages[], pages_count, ts }
    Управление:
      - env MANGA_TITLE или MANGA_ID
      - env MANGA_LANG (default: en)
      - query '?title=..&lang=..&manga_id=..' пробрасывается через env PARSER_QUERY_JSON
    """
    title = (os.getenv("MANGA_TITLE") or "").strip()
    manga_id = (os.getenv("MANGA_ID") or "").strip()
    lang = (os.getenv("MANGA_LANG") or "en").strip().lower()

    # Оверрайды, пришедшие из api/parse
    q = os.getenv("PARSER_QUERY_JSON")
    if q:
        try:
            override = json.loads(q)
            if isinstance(override, dict):
                title = (override.get("title") or title or "").strip()
                manga_id = (override.get("manga_id") or manga_id or "").strip()
                o_lang = override.get("lang")
                if o_lang:
                    lang = str(o_lang).strip().lower()
        except Exception:
            pass

    try:
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
    except requests.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.response.status_code}", "detail": str(e)}
    except Exception as e:
        return {"ok": False, "error": "unexpected", "detail": str(e)}
