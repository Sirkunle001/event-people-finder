# event-people-finder

**Keyless event-people extraction: speakers and sponsors of any Brella-powered
conference, with names, titles, companies and websites.**

No LinkedIn account. No cookies. No API key. No browser. Event platforms publish
their event data for their own widgets and mobile apps; this tool reads that
same public surface and hands you a clean CSV: every speaker and sponsor of a
conference, with names, job titles, companies, and websites.

## How it works

1. **Discover**: search engines surface Brella-powered event pages at
   `next.brella.io/events/{code}`; the URL slug IS the event's join code.
2. **Read**: Brella's public event API answers keyless per event: full speaker
   roster (name, title, company, bio, photo) and the sponsor list (name,
   website, LinkedIn, industry, description).
3. **Export**: deduped CSVs, one row per speaker and per sponsor.

## Quick start

```bash
pip install -e .
event-people-finder discover "fintech summit"     # find Brella event codes
event-people-finder check FJ26                    # confirm an event is Brella-powered
event-people-finder list FJ26                     # FJ26_speakers.csv + FJ26_sponsors.csv
event-people-finder list https://next.brella.io/events/FJ26/home
```

Speakers CSV columns: `event`, `name`, `first`, `last`, `title`, `company`,
`bio`, `photo`. Sponsors CSV: `event`, `name`, `website`, `linkedin`,
`industry`, `description`.

## Why event rosters

A conference speaker list is the highest-signal people list that exists: every
name is public, titled, company-attributed, and contextually warm (they spoke
on exactly the topic your product sits next to). Sponsors are companies with
budget, self-selected by category. Both are delivered with the event as
provenance.

## Platform catalog

| Platform | Keyless read | Speakers | Sponsors | Status |
|---|---|---|---|---|
| Brella (`next.brella.io/{code}`) | yes | yes | yes | **supported (verified)** |
| Sessionize (`sessionize.com/api/v2/{id}/view/Speakers/All`) | per-event open JSON | yes | no | candidate (ids need discovery) |
| Luma (`lu.ma/{slug}`) | public pages, JS-rendered | partial | no | probed, unverified |
| Slido / Whova / Swapcard / Eventbrite | unprobed | ? | ? | backlog |

Each row becomes supported the same way Brella did: probe the public surface
live, write the parser, test against a real event.

## Honest limits, stated plainly

- **Brella-powered events only** in this version. Not every conference uses
  Brella; the `discover` command finds the ones that do.
- Speaker bios and sponsor descriptions are self-declared; treat them as
  claims, not facts.
- Event data persists after events end, but organizers can delete events at
  any time.
- Run politely: the tool paces requests and caps page sizes.

## The managed version

Custom event-signal pipelines (every conference in your vertical, speaker and
sponsor lists enriched with emails, delivered on a schedule) are what Gafar
builds as a service. [Describe the list you need](https://www.linkedin.com/in/gafar/).

## Requirements

- Python 3.11+
- Nothing else. No accounts, no keys, no browser, no Docker.

## Scope

This tool reads public web surfaces and provides software components, not
data. Operators are responsible for complying with applicable terms and law.

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

Tests are offline (fixtures from real API responses; no network).

## License

MIT. See [LICENSE](LICENSE).
