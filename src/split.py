"""Split the corpus into a 500-example held-out set and a training pool.

**This runs before any labelling.** That ordering is the whole point: if the split happened
after labels existed, any decision about which examples to hold out could be informed by
them, and the held-out set would no longer be held out. The brief requires it and so does
the masterplan's acceptance block.

Sampling is **proportional within section**, not balanced across classes. Balancing would
guarantee a full complement of every class, but it would also make the held-out set
unrepresentative of what the product's ingest actually sees, and every number measured on
it would then describe a distribution that does not exist. Macro-F1 already weights the
classes equally; buying tail coverage by distorting the sample would be paying twice for
the same thing and lying about the traffic in the process.

The consequence is accepted openly: if a class lands with thin support, that is reported in
the limitations section rather than papered over by synthesising or over-sampling examples.

Deterministic given the same corpus file: seeded RNG, and rows sorted by id before
sampling so file order cannot influence the outcome.
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import Counter, defaultdict

from src.regex_baseline import classify_wire_item
from src.schema import TOPIC_CLASSES
from src.store import DATA, read_jsonl, write_jsonl

CORPUS = DATA / "corpus.jsonl"
HELDOUT = DATA / "heldout.jsonl"
TRAIN_POOL = DATA / "train_pool.jsonl"

SEED = 20260814
HELDOUT_N = 500


def stratified_sample(rows: list[dict], n: int, seed: int) -> tuple[list[dict], list[dict]]:
    """Proportional allocation across sections, largest-remainder rounding."""
    rng = random.Random(seed)
    by_section: dict[str, list[dict]] = defaultdict(list)
    for row in sorted(rows, key=lambda r: r["id"]):
        by_section[row["section"]].append(row)

    total = len(rows)
    exact = {s: len(members) * n / total for s, members in by_section.items()}
    quota = {s: int(v) for s, v in exact.items()}

    # Largest-remainder: hand out the rounding shortfall to the biggest fractional parts.
    shortfall = n - sum(quota.values())
    for section, _ in sorted(exact.items(), key=lambda kv: -(kv[1] - int(kv[1])))[:shortfall]:
        quota[section] += 1

    picked: list[dict] = []
    for section, members in by_section.items():
        take = min(quota.get(section, 0), len(members))
        picked.extend(rng.sample(members, take))

    picked_ids = {row["id"] for row in picked}
    remainder = [row for row in rows if row["id"] not in picked_ids]
    return picked, remainder


def main() -> int:
    parser = argparse.ArgumentParser(description="Split the corpus. Must run before labelling.")
    parser.add_argument("--n", type=int, default=HELDOUT_N, help="held-out size")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    rows = list(read_jsonl(CORPUS))
    if len(rows) < args.n * 2:
        print(f"[split] refusing: corpus has {len(rows)} rows, need at least {args.n * 2}", file=sys.stderr)
        return 1

    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        print(f"[split] refusing: corpus contains duplicate ids ({len(ids) - len(set(ids))})", file=sys.stderr)
        return 1

    # ── Once held out, always held out ────────────────────────────────────────────────
    # Harvest keeps running after the split, so this must be safe to re-run. If a held-out
    # set already exists its membership is FROZEN and everything new goes to the training
    # pool. Growing the training pool can never leak into the held-out set; re-drawing the
    # held-out set after labelling had begun absolutely could, and this makes that
    # impossible by construction rather than by remembering not to.
    frozen = [row for row in read_jsonl(HELDOUT)]
    if frozen:
        frozen_ids = {row["id"] for row in frozen}
        by_id = {row["id"]: row for row in rows}
        missing = frozen_ids - set(by_id)
        if missing:
            print(f"[split] refusing: {len(missing)} held-out ids are absent from the corpus", file=sys.stderr)
            return 1
        heldout = [by_id[i] for i in sorted(frozen_ids)]
        train_pool = [row for row in rows if row["id"] not in frozen_ids]
        print(f"[split] existing held-out set found — membership frozen ({len(heldout)} ids)")
    else:
        heldout, train_pool = stratified_sample(rows, args.n, args.seed)

    for row in heldout:
        row["split"] = "heldout"
    for row in train_pool:
        row["split"] = "train"

    # ── The assertions that make "held out" mean something ────────────────────────────
    heldout_ids = {row["id"] for row in heldout}
    train_ids = {row["id"] for row in train_pool}
    assert not (heldout_ids & train_ids), "LEAKAGE: an id appears in both splits"
    assert len(heldout_ids) == args.n, f"held-out is {len(heldout_ids)}, expected {args.n}"
    assert len(heldout_ids) + len(train_ids) == len(rows), "rows were lost in the split"
    assert len({r["headline"] for r in heldout} & {r["headline"] for r in train_pool}) == 0, (
        "LEAKAGE: an identical headline appears in both splits under different URLs"
    )

    write_jsonl(HELDOUT, heldout)
    write_jsonl(TRAIN_POOL, train_pool)

    # ── Report ────────────────────────────────────────────────────────────────────────
    regex_labels = Counter(classify_wire_item(row["headline"]) for row in heldout)
    sections = Counter(row["section"] for row in heldout)
    outlets = Counter(row["outlet"] for row in heldout)

    print(f"[split] corpus {len(rows)} → held-out {len(heldout)}, train pool {len(train_pool)}")
    print(f"[split] disjoint: OK   seed: {args.seed}")
    print("[split] held-out by section: " + " · ".join(f"{s}={n}" for s, n in sorted(sections.items())))
    print(f"[split] held-out spans {len(outlets)} outlets")
    print("[split] held-out by regex label (a sampling diagnostic, NOT the gold labels):")
    missing = []
    for label in TOPIC_CLASSES:
        count = regex_labels.get(label, 0)
        flag = "  ← thin, flag in limitations" if count < 20 else ""
        if count == 0:
            missing.append(label)
        print(f"           {label:<15} {count:>4}{flag}")
    if missing:
        print(f"[split] WARNING: regex assigns no held-out example to: {', '.join(missing)}")
        print("        The teacher may still label examples into those classes — the regex")
        print("        is a weak proxy, not the gold set. Re-check after S4 labelling.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
