"""CSV export: speakers + sponsors, deduped."""
from __future__ import annotations

import csv
import re

SPEAKER_COLS = ["event", "name", "first", "last", "title", "company", "bio", "photo"]
SPONSOR_COLS = ["event", "name", "website", "linkedin", "industry", "description"]


def _clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def write_speakers(rows: list[dict], path: str, event: str) -> int:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=SPEAKER_COLS)
        w.writeheader()
        for r in rows:
            row = {k: _clean(r.get(k)) for k in SPEAKER_COLS if k != "event"}
            w.writerow({"event": event, **row})
    return len(rows)


def write_sponsors(rows: list[dict], path: str, event: str) -> int:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=SPONSOR_COLS)
        w.writeheader()
        for r in rows:
            row = {k: _clean(r.get(k)) for k in SPONSOR_COLS if k != "event"}
            w.writerow({"event": event, **row})
    return len(rows)


def dedupe(rows: list[dict], key_fields: tuple[str, ...]) -> tuple[list[dict], int]:
    seen, out = set(), []
    for r in rows:
        key = "|".join(str(r.get(k, "")).lower() for k in key_fields)
        if not key.strip("|"):
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out, len(rows) - len(out)
