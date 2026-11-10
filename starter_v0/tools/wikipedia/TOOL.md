---
name: wikipedia
track: core
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [query, lang, limit]
outputs: [items]
side_effect: false
---
# wikipedia

Searches Wikipedia for background knowledge: definitions, concepts, people,
organizations, history. Returns `items` with `title`, `url`, `source`, `summary`,
the same shape as `lookup`/`fetch`, so results can be passed to `format`.

- No API key needed. Requests send a `User-Agent` header, which Wikipedia requires.
- `lang`: `en` (default) or `vi`. Any other value falls back to `en`.
- `limit`: clamped to 1–10 (default 3). Numeric strings such as `"5"` are accepted.
- Empty or non-string `query` returns an error dict without making a request.
- HTTP errors and timeouts return an error dict; the tool never raises.

Not for current news (`lookup` with `topic=news`), social posts
(`timeline`/`social_search`), a specific URL (`fetch`), or academic papers (`papers`).
