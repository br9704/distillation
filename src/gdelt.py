"""Supplementary historical backfill via the GDELT DOC 2.0 API, filtered to the outlets
already in the feed catalog.

**GDELT throttles far harder than it documents.** Its error body asks for one request every
five seconds; measured behaviour is stricter than that — a single request succeeds and the
next two return 429 even at 20-second spacing. It also under-delivers: a request for 250
records over a 7-day window on techcrunch.com returned 52.

So this is a trickle, not a pipeline. `DELAY_S` is set to a minute, well beyond the
published limit, because the alternative is being throttled into returning nothing. A
sweep across every outlet therefore takes about an hour, runs unattended, and is resumable.
The corpus does not depend on it — `src/harvest.py` carries the load.

    uv run python -m src.gdelt --timespan 7d
    uv run python -m src.gdelt --timespan 3m --delay 90

Politeness is a sleep, not a retry-on-429. Hammering a free public service until it relents
is not something this repo does.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

from src.feeds import ALL_FEEDS
from src.store import DATA, append_jsonl, example_id, read_jsonl, title_key

CORPUS = DATA / "corpus.jsonl"
ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"
USER_AGENT = "Mozilla/5.0 (compatible; SentinelBot/1.0)"

# Documented limit is 1 req / 5s. Measured behaviour is much stricter, so this is
# deliberately an order of magnitude more conservative.
DELAY_S = 60.0
MAX_RECORDS = 250


def outlet_sections() -> dict[str, str]:
    """Map each outlet to its section, preferring the production catalog's own grouping."""
    mapping: dict[str, str] = {}
    for feed in ALL_FEEDS:
        mapping.setdefault(feed.outlet, feed.section)
    return mapping


def fetch_domain(domain: str, timespan: str) -> tuple[list[dict], str | None]:
    query = urllib.parse.urlencode(
        {
            "query": f"domain:{domain} sourcelang:english",
            "mode": "artlist",
            "maxrecords": MAX_RECORDS,
            "format": "json",
            "timespan": timespan,
        }
    )
    request = urllib.request.Request(f"{ENDPOINT}?{query}", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 — a supplementary source must never be fatal
        return [], f"{type(exc).__name__}: {exc}"

    if not body.lstrip().startswith("{"):
        # GDELT returns its throttle notice as plain text with HTTP 200.
        return [], body.strip()[:90]
    try:
        return json.loads(body).get("articles", []), None
    except json.JSONDecodeError as exc:
        return [], f"bad JSON: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill the corpus from GDELT.")
    parser.add_argument("--timespan", default="7d", help="GDELT timespan, e.g. 3d, 7d, 1m, 3m")
    parser.add_argument("--delay", type=float, default=DELAY_S, help="seconds between requests")
    parser.add_argument("--limit", type=int, default=0, help="stop after this many outlets")
    args = parser.parse_args()

    existing = list(read_jsonl(CORPUS))
    known_ids = {row["id"] for row in existing}
    known_titles = {title_key(row["headline"]) for row in existing}

    sections = outlet_sections()
    domains = sorted(sections)
    if args.limit:
        domains = domains[: args.limit]

    total_new = 0
    throttled = 0
    for index, domain in enumerate(domains, start=1):
        articles, error = fetch_domain(domain, args.timespan)
        if error:
            throttled += 1
            print(f"[gdelt] {index}/{len(domains)} {domain:<26} — {error}")
        else:
            fresh = []
            for article in articles:
                url, title = article.get("url"), (article.get("title") or "").strip()
                if not url or not title:
                    continue
                uid, tkey = example_id(url), title_key(title)
                if uid in known_ids or tkey in known_titles:
                    continue
                known_ids.add(uid)
                known_titles.add(tkey)
                fresh.append(
                    {
                        "id": uid,
                        "headline": title,
                        "outlet": article.get("domain", domain),
                        "url": url,
                        "published_at": article.get("seendate"),
                        "source": "gdelt",
                        "section": sections.get(article.get("domain", domain), sections[domain]),
                    }
                )
            append_jsonl(CORPUS, fresh)
            total_new += len(fresh)
            print(f"[gdelt] {index}/{len(domains)} {domain:<26} {len(articles):>4} returned, {len(fresh):>4} new")

        if index < len(domains):
            time.sleep(args.delay)

    print(f"[gdelt] done — {total_new} new rows, {throttled}/{len(domains)} requests throttled or failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
