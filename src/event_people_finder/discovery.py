"""Event discovery: find Brella-powered events keylessly.

Brella is a white-label event networking platform; every event gets a public
page at next.brella.io/events/{joinCode}, and the joinCode is simply the URL
slug. Discovery therefore needs no fingerprinting: search engines surface the
event pages, the slugs ARE the codes. (Site HTML grep for widget.brella.io +
joinCode works too for conference sites that embed the widget, but the slug
route needs zero extra requests against the target.)
"""
from __future__ import annotations

import re
import time
from urllib.parse import quote

_ENGINES = (
    lambda q: f"https://lite.duckduckgo.com/lite/?q={q}",
    lambda q: f"https://html.duckduckgo.com/html/?q={q}",
)


def _harvest(html: str) -> list[str]:
    out: list[str] = []
    for m in re.findall(r'uddg=([^&"]+)', html):
        u = unquote(m).rstrip("/")
        if "next.brella.io/events/" in u:
            code = u.rstrip("/").split("/events/")[-1].split("/")[0]
            if code and code not in out:
                out.append(code)
    return out


def unquote(s: str) -> str:
    from urllib.parse import unquote as _u
    return _u(s)


def discover_events(session, query: str = "event", max_results: int = 20,
                    retries: int = 2, delay: float = 4.0, log=print) -> list[str]:
    """Return Brella joinCodes (event slugs) matching a query. The query is
    augmented with site:next.brella.io so every hit is a Brella event page."""
    q = quote(f"site:next.brella.io/events {query}", safe="")
    found: list[str] = []
    for attempt in range(retries + 1):
        for engine in _ENGINES:
            try:
                r = session.get(engine(q), timeout=30)
                if r.status_code != 200:
                    continue
                for code in _harvest(r.text):
                    if code.lower() not in ("home", "welcome", "login", "signup") and code not in found:
                        found.append(code)
                        if len(found) >= max_results:
                            return found
            except Exception as exc:
                log(f"  [{query}] {type(exc).__name__}")
        if found or attempt == retries:
            break
        time.sleep(delay)
    return found
