"""RSS/Atom parsing, ported from Sentinel's production backend:
  ~/Desktop/AI REPORTING APP MVP/supabase/functions/_shared/wire.ts:213-299

Regex-based, like production — and for the same reason recorded in its source comments:
the previous DOM implementation parsed feeds as `text/html`, where `<link>` is a void
element, so every item's URL came back empty and every feed returned zero items. A
tolerant regex pass over the raw XML avoids that whole class of failure.

**Two deliberate deviations from production**, both about corpus volume rather than
behaviour:

1. `max_items` defaults to unlimited here; production caps at `RSS_MAX_ITEMS = 10` per
   fetch. Taking 30-45 items instead of 10 from the same feed samples the same population
   more deeply — it does not change which outlets or what kind of story we see.
2. Entity decoding uses Python's `html.unescape`, which handles a superset of production's
   40-entity table. Strictly better text; a headline is never made worse by decoding
   `&#8217;` correctly. This is corpus construction, not the incumbent arm, so fidelity to
   production's limitations buys nothing here.
"""

from __future__ import annotations

import html
import re
from typing import NamedTuple


class RSSItem(NamedTuple):
    title: str
    url: str
    pub_date: str | None


_CDATA_RE = re.compile(r"^\s*<!\[CDATA\[([\s\S]*?)\]\]>\s*$")
_ITEM_RE = re.compile(r"<item\b[^>]*>([\s\S]*?)</item>", re.IGNORECASE)
_ENTRY_RE = re.compile(r"<entry\b[^>]*>([\s\S]*?)</entry>", re.IGNORECASE)
_LINK_HREF_RE = re.compile(r'<link\b[^>]*href="([^"]+)"', re.IGNORECASE)
_WS_RE = re.compile(r"\s+")


def _strip_cdata(s: str) -> str:
    return _CDATA_RE.sub(r"\1", s).strip()


def _extract_tag(block: str, tag: str) -> str | None:
    """Match `<tag ...>content</tag>` case-insensitively, allowing namespaces."""
    escaped = re.escape(tag)
    match = re.search(rf"<{escaped}\b[^>]*>([\s\S]*?)</{escaped}>", block, re.IGNORECASE)
    return _strip_cdata(match.group(1)) if match else None


def clean_headline(raw: str) -> str:
    """Decode entities and collapse whitespace — production's cleanHeadline()."""
    return _WS_RE.sub(" ", html.unescape(raw)).strip()


def parse_rss_xml(xml: str, max_items: int | None = None) -> list[RSSItem]:
    """Parse RSS 2.0 `<item>` first, falling back to Atom `<entry>`.

    Mirrors production's progressive parse: Atom is only attempted when the RSS pass
    yields nothing, so a feed carrying both does not produce duplicates.
    """
    items: list[RSSItem] = []

    for match in _ITEM_RE.finditer(xml):
        if max_items is not None and len(items) >= max_items:
            break
        block = match.group(1)
        title = _extract_tag(block, "title")
        link = _extract_tag(block, "link")
        if not link:
            # Some feeds use Atom-style <link href="..."/> inside <item>.
            href = _LINK_HREF_RE.search(block)
            link = href.group(1) if href else None
        pub_date = _extract_tag(block, "pubDate") or _extract_tag(block, "dc:date")
        if title and link:
            items.append(RSSItem(clean_headline(title), link.strip(), pub_date))

    if items:
        return items

    for match in _ENTRY_RE.finditer(xml):
        if max_items is not None and len(items) >= max_items:
            break
        block = match.group(1)
        title = _extract_tag(block, "title")
        href = _LINK_HREF_RE.search(block)
        link = href.group(1) if href else _extract_tag(block, "link")
        pub_date = _extract_tag(block, "published") or _extract_tag(block, "updated")
        if title and link:
            items.append(RSSItem(clean_headline(title), link.strip(), pub_date))

    return items
