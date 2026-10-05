"""Brella public API client: speakers and sponsors, keyless.

The API is JSON:API style. Endpoints used (verified live, no auth):

    GET https://api.brella.io/api/public/events/{joinCode}/speakers?page[size]=N
    GET https://api.brella.io/api/public/events/{joinCode}/sponsors?page[size]=N

Headers: accept: application/vnd.brella.v4+json (plain application/json also
answers). Speaker attributes: first-name, last-name, job-title, company-name,
photo-url, bio (draft-js blocks or plain string). Sponsor attributes carry
company name/website/linkedin/industry/description.
"""
from __future__ import annotations

import re
import time

BASE = "https://api.brella.io/api/public/events"
HEADERS = {"accept": "application/vnd.brella.v4+json",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126"}

_PAGE = re.compile(r"page\[size\]=(\d+)")


def _bio_text(bio) -> str:
    """Bio is either a plain string or draft-js blocks ({blocks:[{text}]})."""
    if not bio:
        return ""
    if isinstance(bio, str):
        return bio.strip()
    if isinstance(bio, dict):
        blocks = bio.get("blocks") or []
        return "\n".join(b.get("text", "") for b in blocks).strip()
    return ""


def _attr(item: dict) -> dict:
    a = item.get("attributes") or {}
    return a if isinstance(a, dict) else {}


def _fetch_page(session, url: str):
    r = session.get(url, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        return None
    try:
        return r.json()
    except (ValueError, TypeError):
        return None


def event_exists(session, join_code: str) -> bool:
    r = session.get(f"{BASE}/{join_code}", headers=HEADERS, timeout=20)
    return r.status_code == 200


def speakers(session, join_code: str, max_items: int = 500, log=print) -> list[dict]:
    """All speakers: {name, first, last, title, company, bio, photo}."""
    out, seen = [], set()
    page_size = min(100, max_items)
    url = f"{BASE}/{join_code}/speakers?page%5Bsize%5D={page_size}"
    meta = {"links": {"next": url}}
    while url and len(out) < max_items:
        data = _fetch_page(session, url)
        if data is None:
            log(f"  speakers page failed: {url[:70]}")
            break
        for item in data.get("data") or []:
            a = _attr(item)
            first, last = a.get("first-name", ""), a.get("last-name", "")
            name = f"{first} {last}".strip()
            key = (name, a.get("company-name", ""))
            if not name or key in seen:
                continue
            seen.add(key)
            out.append({
                "name": name, "first": first, "last": last,
                "title": a.get("job-title", "") or "",
                "company": a.get("company-name", "") or "",
                "bio": _bio_text(a.get("bio")),
                "photo": a.get("photo-url", "") or "",
            })
        url = ((data.get("links") or {}).get("next") or "")
        if url and "page%5Bsize%5D" not in url and "page[size]" not in url:
            sep = "&" if "?" in url else "?"
            size = _PAGE.search(url)
            url = url + (f"{sep}page%5Bsize%5D={page_size}" if not size else "")
        time.sleep(0.4)
    return out[:max_items]


def sponsors(session, join_code: str, max_items: int = 500, log=print) -> list[dict]:
    """All sponsors: {name, website, linkedin, industry, description}."""
    out, seen = [], set()
    page_size = min(100, max_items)
    url = f"{BASE}/{join_code}/sponsors?page%5Bsize%5D={page_size}"
    while url and len(out) < max_items:
        data = _fetch_page(session, url)
        if data is None:
            log(f"  sponsors page failed: {url[:70]}")
            break
        for item in data.get("data") or []:
            a = _attr(item)
            name = a.get("name") or a.get("company-name") or ""
            if not name or name in seen:
                continue
            seen.add(name)
            out.append({
                "name": name,
                "website": a.get("website", "") or a.get("website-url", "") or "",
                "linkedin": a.get("linkedin", "") or a.get("linkedin-url", "") or "",
                "industry": a.get("industry", "") or "",
                "description": _bio_text(a.get("description") or a.get("bio")),
            })
        url = ((data.get("links") or {}).get("next") or "")
        if url and "page%5Bsize%5D" not in url and "page[size]" not in url:
            sep = "&" if "?" in url else "?"
            url = url + f"{sep}page%5Bsize%5D={page_size}"
        time.sleep(0.4)
    return out[:max_items]


def event_meta(session, join_code: str) -> dict:
    data = _fetch_page(session, f"{BASE}/{join_code}")
    if not data:
        return {}
    a = data.get("data", {}).get("attributes", {})
    return {k: a.get(k) for k in ("name", "starts-at", "ends-at", "location", "timezone") if k in a}
