"""Command line interface.

  event-people-finder discover "fintech summit"        # find Brella event codes
  event-people-finder check FJ26                       # is this event Brella-powered?
  event-people-finder list FJ26                        # speakers.csv + sponsors.csv
  event-people-finder list https://next.brella.io/events/FJ26/home
"""
from __future__ import annotations

import argparse
import sys

from curl_cffi import requests as cr

from .brella import event_exists, event_meta, speakers, sponsors
from .discovery import discover_events
from .export import dedupe, write_speakers, write_sponsors


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="event-people-finder",
        description="Keyless event-people extraction: speakers and sponsors of any "
        "Brella-powered conference, with names, titles, companies and websites. "
        "No account, no cookies, no API key.",
    )
    p.add_argument("command", nargs="?", default="",
                   help="discover | check | list | (a post URL for single-post read)")
    p.add_argument("target", nargs="?", default="",
                   help="query (discover), joinCode/event-URL (check/list)")
    p.add_argument("--out", default="", help="output CSV base name (default: the event code)")
    p.add_argument("--max", type=int, default=500, help="max speakers/sponsors per event")
    p.add_argument("--sponsors-only", action="store_true")
    p.add_argument("--speakers-only", action="store_true")
    p.add_argument("--query", default="event", help="discovery query (with discover)")
    p.add_argument("--max-results", type=int, default=20, help="max event codes from discovery")
    p.add_argument("--retries", type=int, default=2, help="discovery retries")
    return p


def _code_from_target(target: str) -> str:
    t = target.strip().rstrip("/")
    if "brella.io/events/" in t:
        return t.split("/events/")[-1].split("/")[0]
    if t.startswith("http"):
        return t.rstrip("/").split("/")[-1]
    return t


def cmd_discover(args) -> int:
    session = cr.Session(impersonate="chrome")
    codes = discover_events(session, args.query or "event",
                            max_results=args.max_results, retries=args.retries)
    print(f"{len(codes)} Brella events found:")
    for c in codes:
        print(" ", c)
    return 0


def cmd_check(args) -> int:
    session = cr.Session(impersonate="chrome")
    code = _code_from_target(args.target)
    if not code:
        print("give an event code or URL")
        return 1
    meta = event_meta(session, code)
    ok = bool(meta) or event_exists(session, code)
    print(f"{code}: {'Brella-powered' if ok else 'not found / not Brella'}")
    if meta:
        for k, v in meta.items():
            if v:
                print(f"  {k}: {v}")
    return 0 if ok else 1


def cmd_list(args) -> int:
    session = cr.Session(impersonate="chrome")
    code = _code_from_target(args.target)
    if not code:
        print("give an event code or URL")
        return 1
    meta = event_meta(session, code)
    name = (meta.get("name") or code)
    print(f"event: {name} (code: {code})", file=sys.stderr)
    out_base = args.out or code

    speakers_rows, sponsors_rows = [], []
    if not args.sponsors_only:
        speakers_rows = speakers(session, code, max_items=args.max)
        speakers_rows, dd = dedupe(speakers_rows, ("name", "company"))
        spath = f"{out_base}_speakers.csv"
        n = write_speakers(speakers_rows, spath, code)
        print(f"speakers: {n} (dupes removed {dd}) -> {spath}", file=sys.stderr)
    if not args.speakers_only:
        sponsors_rows = sponsors(session, code, max_items=args.max)
        sponsors_rows, dd = dedupe(sponsors_rows, ("name",))
        upath = f"{out_base}_sponsors.csv"
        m = write_sponsors(sponsors_rows, upath, code)
        print(f"sponsors: {m} (dupes removed {dd}) -> {upath}", file=sys.stderr)

    for r in speakers_rows[:8]:
        print(f"  {r['name']} | {r['title'][:40]} | {r['company'][:40]}")
    for r in sponsors_rows[:5]:
        print(f"  [sponsor] {r['name']} | {r['website'][:40]}")
    return 0


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = build_arg_parser().parse_args(argv)
    cmd = (args.command or "").lower()
    if cmd == "discover":
        return cmd_discover(args)
    if cmd == "check":
        return cmd_check(args)
    if cmd == "list":
        return cmd_list(args)
    if args.target and args.target.startswith("http"):
        # README-style: a bare event URL means `list`
        args.target = args.target
        return cmd_list(args)
    print(__doc__)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
