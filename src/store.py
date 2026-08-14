"""JSONL persistence. Every dataset in this repo is append-only JSONL keyed by `id`, so a
harvest pass can be re-run any number of times without duplicating rows and a labelling run
can resume after a crash.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Iterator

DATA = Path(__file__).resolve().parent.parent / "data"

# Tracking parameters that make two links to the same article look different. Stripped
# before hashing so dedup is about the article, not about how it was syndicated.
_TRACKING_PARAMS = re.compile(
    r"^(utm_[a-z_]+|fbclid|gclid|mc_cid|mc_eid|ref|ref_src|cmpid|smid|partner|__twitter_impression|guccounter|at_medium|at_campaign)$",
    re.IGNORECASE,
)
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalise_url(url: str) -> str:
    """Lowercase scheme+host, drop `www.`, strip tracking params and fragments."""
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return url.strip()
    netloc = parts.netloc.lower().removeprefix("www.")
    query = urlencode(
        [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not _TRACKING_PARAMS.match(k)]
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), netloc, path, query, ""))


def example_id(url: str) -> str:
    """Stable id: sha256 of the normalised URL, first 16 hex chars.

    This is the key S2's disjointness assertion runs on, so it must be a pure function of
    the article — never of harvest order or timestamp.
    """
    return hashlib.sha256(normalise_url(url).encode("utf-8")).hexdigest()[:16]


def title_key(headline: str) -> str:
    """Normalised headline, for catching the same story syndicated under different URLs."""
    return _WS_RE.sub(" ", _PUNCT_RE.sub(" ", headline.lower())).strip()


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count
