"""Harvest headlines from the production wire feeds plus their same-outlet section feeds.

Idempotent and append-only: run it as many times as you like. Each pass fetches every feed
concurrently, drops anything already in `data/corpus.jsonl` by URL id or by normalised
title, and appends the rest. Corpus volume therefore grows with the number of passes, which
is how ~5,500 unique headlines are reached from feeds that carry 30-45 items each.

    uv run python -m src.harvest              # one pass
    uv run python -m src.harvest --passes 6 --interval 900

Per-feed failures are logged and skipped, never fatal — this mirrors production, where a
dead feed must not take the ingest tick down with it. Feed bitrot is expected: `wire.ts`
notes 41 of an earlier 21-outlet list went dead, and the surviving list is what remains.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from collections import Counter
from dataclasses import dataclass

import httpx

from src.feeds import ALL_FEEDS, Feed
from src.rss import parse_rss_xml
from src.store import DATA, append_jsonl, example_id, read_jsonl, title_key

USER_AGENT = "Mozilla/5.0 (compatible; SentinelBot/1.0)"  # matches wire.ts:309
CORPUS = DATA / "corpus.jsonl"

# Production uses a 5s timeout because it runs on a cron tick and must not block ingest.
# Corpus building is not latency-sensitive, so slow-but-alive feeds are given room.
TIMEOUT_S = 20.0
CONCURRENCY = 12


@dataclass
class FeedResult:
    feed: Feed
    items: int
    error: str | None = None


async def fetch_feed(client: httpx.AsyncClient, feed: Feed, sem: asyncio.Semaphore) -> tuple[Feed, list, str | None]:
    async with sem:
        try:
            response = await client.get(feed.url, timeout=TIMEOUT_S, follow_redirects=True)
            if response.status_code != 200:
                return feed, [], f"HTTP {response.status_code}"
            return feed, parse_rss_xml(response.text), None
        except Exception as exc:  # noqa: BLE001 — a dead feed must never be fatal
            return feed, [], f"{type(exc).__name__}: {exc}"


async def harvest_once() -> tuple[int, int, list[FeedResult]]:
    """One pass over every feed. Returns (new_rows, seen_rows, per-feed results)."""
    existing = list(read_jsonl(CORPUS))
    known_ids = {row["id"] for row in existing}
    known_titles = {title_key(row["headline"]) for row in existing}

    sem = asyncio.Semaphore(CONCURRENCY)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"}
    async with httpx.AsyncClient(headers=headers) as client:
        gathered = await asyncio.gather(*(fetch_feed(client, f, sem) for f in ALL_FEEDS))

    fresh: list[dict] = []
    results: list[FeedResult] = []
    seen = 0
    for feed, items, error in gathered:
        results.append(FeedResult(feed, len(items), error))
        for item in items:
            seen += 1
            uid = example_id(item.url)
            tkey = title_key(item.title)
            # Dedup within this pass too, not just against the file — several feeds
            # syndicate the same AP or Reuters copy within a single tick.
            if uid in known_ids or tkey in known_titles or not item.title.strip():
                continue
            known_ids.add(uid)
            known_titles.add(tkey)
            fresh.append(
                {
                    "id": uid,
                    "headline": item.title,
                    "outlet": feed.outlet,
                    "url": item.url,
                    "published_at": item.pub_date,
                    "source": feed.url,
                    "section": feed.section,
                }
            )

    append_jsonl(CORPUS, fresh)
    return len(fresh), seen, results


def report(results: list[FeedResult], new_rows: int, seen: int, total: int) -> None:
    dead = [r for r in results if r.error]
    empty = [r for r in results if not r.error and r.items == 0]
    by_section = Counter()
    for r in results:
        by_section[r.feed.section] += r.items

    print(f"  fetched {seen} items from {len(results) - len(dead)}/{len(results)} live feeds")
    print(f"  new after dedup: {new_rows}   corpus total: {total}")
    print("  by section: " + " · ".join(f"{s}={n}" for s, n in sorted(by_section.items())))
    if dead:
        print(f"  {len(dead)} feeds failed:")
        for r in dead:
            print(f"    {r.feed.outlet:<24} {r.error}")
    if empty:
        print(f"  {len(empty)} feeds parsed to 0 items: {', '.join(r.feed.outlet for r in empty)}")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Harvest headlines from the production wire feeds.")
    parser.add_argument("--passes", type=int, default=1, help="number of harvest passes")
    parser.add_argument("--interval", type=int, default=900, help="seconds between passes")
    parser.add_argument("--target", type=int, default=0, help="stop early once the corpus reaches this size")
    args = parser.parse_args()

    for n in range(1, args.passes + 1):
        print(f"[harvest] pass {n}/{args.passes}")
        new_rows, seen, results = await harvest_once()
        total = sum(1 for _ in read_jsonl(CORPUS))
        report(results, new_rows, seen, total)

        if args.target and total >= args.target:
            print(f"[harvest] target {args.target} reached at {total}")
            return 0
        if n < args.passes:
            print(f"[harvest] sleeping {args.interval}s")
            time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
