"""S2 guards: feed-catalog integrity, RSS parsing, dedup keys, and the split's
disjointness promise.

The split test is the important one. "Held out" is a claim about leakage, and a claim about
leakage that is only made in prose is not a guarantee — so it is asserted here on the same
code path the real split uses.
"""

from __future__ import annotations

import pytest

from src.feeds import ALL_FEEDS, EXPANSION_FEEDS, FEEDS, SECTIONS
from src.rss import clean_headline, parse_rss_xml
from src.split import stratified_sample
from src.store import example_id, normalise_url, title_key


# ── Feed catalog ─────────────────────────────────────────────────────────────────────
def test_no_duplicate_feed_urls():
    urls = [f.url for f in ALL_FEEDS]
    assert len(urls) == len(set(urls))


def test_every_section_is_known():
    assert {f.section for f in ALL_FEEDS} <= set(SECTIONS)


def test_expansion_never_introduces_a_new_outlet():
    """Outlet fidelity. The expansion may add sections; it may not add newsrooms.

    This is what keeps the rebuilt corpus a rebuild rather than a different corpus —
    one working candidate (skysports.com) was dropped solely because it failed this.
    """
    assert {f.outlet for f in EXPANSION_FEEDS} <= {f.outlet for f in FEEDS}


def test_production_catalog_is_transcribed_completely():
    assert len(FEEDS) == 63, "the production catalog in wire.ts has 63 feeds"


# ── RSS parsing ──────────────────────────────────────────────────────────────────────
RSS = """<?xml version="1.0"?><rss version="2.0"><channel>
  <item><title>Fed holds rates &amp; signals a pause</title>
        <link>https://example.com/a?utm_source=rss</link>
        <pubDate>Thu, 14 Aug 2026 10:00:00 GMT</pubDate></item>
  <item><title><![CDATA[Chip maker beats earnings]]></title>
        <link>https://example.com/b</link></item>
  <item><title>No link here</title></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
  <entry><title>Starship reaches orbit</title>
         <link href="https://example.com/c"/>
         <published>2026-08-14T10:00:00Z</published></entry>
</feed>"""


def test_parses_rss_and_drops_items_without_a_link():
    items = parse_rss_xml(RSS)
    assert len(items) == 2
    assert items[0].title == "Fed holds rates & signals a pause"  # entity decoded
    assert items[1].title == "Chip maker beats earnings"  # CDATA stripped
    assert items[1].pub_date is None


def test_parses_atom_when_there_are_no_rss_items():
    items = parse_rss_xml(ATOM)
    assert len(items) == 1
    assert items[0].url == "https://example.com/c"


def test_atom_is_only_a_fallback_so_hybrid_feeds_do_not_duplicate():
    """Mirrors production's progressive parse: a feed carrying both must not yield twice."""
    hybrid = RSS.replace("</channel></rss>", "</channel></rss>") + ATOM
    assert len(parse_rss_xml(hybrid)) == 2  # the RSS items only


def test_max_items_caps_output():
    assert len(parse_rss_xml(RSS, max_items=1)) == 1


def test_clean_headline_collapses_whitespace_and_decodes():
    assert clean_headline("  A  &amp;  B\n\tC ") == "A & B C"


# ── Dedup keys ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("https://www.bbc.com/news/1", "https://bbc.com/news/1"),
        ("https://bbc.com/news/1", "https://bbc.com/news/1/"),
        ("https://bbc.com/news/1", "https://bbc.com/news/1#top"),
        ("https://bbc.com/news/1", "https://bbc.com/news/1?utm_source=rss&utm_medium=feed"),
        ("https://BBC.com/news/1", "https://bbc.com/news/1"),
    ],
)
def test_the_same_article_gets_one_id_however_it_was_syndicated(a, b):
    assert example_id(a) == example_id(b), f"{normalise_url(a)} != {normalise_url(b)}"


def test_meaningfully_different_urls_keep_different_ids():
    assert example_id("https://bbc.com/news/1") != example_id("https://bbc.com/news/2")
    # A non-tracking query parameter is part of the article's identity.
    assert example_id("https://x.com/a?id=1") != example_id("https://x.com/a?id=2")


def test_title_key_catches_the_same_story_under_different_urls():
    assert title_key("Fed Holds Rates — Steady!") == title_key("fed holds rates  steady")
    assert title_key("Fed holds rates") != title_key("Fed cuts rates")


# ── The split ────────────────────────────────────────────────────────────────────────
def _corpus(n: int = 2000) -> list[dict]:
    sections = ["general", "markets", "tech", "science", "sports", "entertainment"]
    return [
        {"id": f"{i:016x}", "headline": f"headline {i}", "section": sections[i % len(sections)]}
        for i in range(n)
    ]


def test_split_is_exactly_disjoint_and_loses_nothing():
    rows = _corpus()
    heldout, train = stratified_sample(rows, 500, seed=1)
    held_ids = {r["id"] for r in heldout}
    train_ids = {r["id"] for r in train}
    assert len(heldout) == 500
    assert not (held_ids & train_ids), "LEAKAGE"
    assert len(held_ids) + len(train_ids) == len(rows)
    assert held_ids | train_ids == {r["id"] for r in rows}


def test_split_is_deterministic_for_a_given_seed():
    rows = _corpus()
    first, _ = stratified_sample(rows, 500, seed=7)
    second, _ = stratified_sample(rows, 500, seed=7)
    assert [r["id"] for r in first] == [r["id"] for r in second]


def test_split_is_insensitive_to_corpus_file_order():
    """Rows are sorted by id before sampling, so appending in a different order — which
    harvest does on every pass — cannot change which examples are held out."""
    rows = _corpus()
    forward, _ = stratified_sample(rows, 500, seed=7)
    backward, _ = stratified_sample(list(reversed(rows)), 500, seed=7)
    assert {r["id"] for r in forward} == {r["id"] for r in backward}


def test_split_allocates_proportionally_across_sections():
    rows = _corpus(1200)  # 200 per section, 6 sections
    heldout, _ = stratified_sample(rows, 600, seed=3)
    counts = {}
    for row in heldout:
        counts[row["section"]] = counts.get(row["section"], 0) + 1
    assert all(abs(v - 100) <= 1 for v in counts.values()), counts


def test_split_handles_a_section_smaller_than_its_quota():
    rows = _corpus(600) + [{"id": "ffff", "headline": "rare", "section": "public"}]
    heldout, train = stratified_sample(rows, 300, seed=5)
    assert len({r["id"] for r in heldout} & {r["id"] for r in train}) == 0
    assert len(heldout) <= 300
