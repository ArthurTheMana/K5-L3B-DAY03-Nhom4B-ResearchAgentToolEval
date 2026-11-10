from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err


ALLOWED_LANGS = {"en", "vi"}
DEFAULT_LANG = "en"
DEFAULT_LIMIT = 3
MAX_LIMIT = 10
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"


def _strip_html(text: str | None) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def wiki_search(query: str = "", lang: str = DEFAULT_LANG, limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """Search Wikipedia for background knowledge (definitions, concepts, entities).

    Never raises: bad input or API failures come back as an error dict.
    """
    try:
        query = query.strip() if isinstance(query, str) else ""
        if not query:
            return {"tool": "wiki_search", "error": "ValueError", "message": "query must be a non-empty string"}
        lang = lang.strip().lower() if isinstance(lang, str) else ""
        if lang not in ALLOWED_LANGS:
            lang = DEFAULT_LANG
        limit = max(1, min(int(limit or DEFAULT_LIMIT), MAX_LIMIT))

        # Call requests.get (module attribute) so tests can mock it with the fake_http fixture.
        response = requests.get(
            f"https://{lang}.wikipedia.org/w/rest.php/v1/search/page",
            params={"q": query, "limit": limit},
            headers={"User-Agent": USER_AGENT},  # Wikipedia rejects requests without a User-Agent
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        pages = response.json().get("pages") or []
        items = [{
            "title": page.get("title") or page["key"],
            "url": f"https://{lang}.wikipedia.org/wiki/{page['key']}",
            "source": f"{lang}.wikipedia.org",
            "summary": page.get("description") or _strip_html(page.get("excerpt")),
        } for page in pages if page.get("key")]
        return {"tool": "wiki_search", "query": query, "lang": lang, "items": items[:limit]}
    except Exception as exc:
        return err("wiki_search", exc)
