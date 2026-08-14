"""charts/class_distribution.png — what the corpus actually looks like.

The brief calls for a class-imbalance chart because it pre-empts the first question any
reviewer asks. This one carries a second, sharper message: the left panel is what the
production regex *thinks* the corpus is, and its `general` bar is the single biggest thing
on the chart. That bar is the project's premise made visible — `general` is where the
incumbent puts everything it cannot recognise.

The right panel is the editorial section each headline was harvested from, which is
independent of the regex and shows the corpus is genuinely broad. Reading the two together
is the point: the corpus has real sports and entertainment coverage that the regex is
collapsing into `general`.

Neither panel is ground truth. Teacher labels arrive in S4 and this chart is regenerated
beside them.

    uv run python -m src.chart_corpus
"""

from __future__ import annotations

import sys
from collections import Counter

import matplotlib.pyplot as plt

from src import charts
from src.regex_baseline import classify_wire_item
from src.schema import TOPIC_CLASSES
from src.store import DATA, read_jsonl

CORPUS = DATA / "corpus.jsonl"


def main() -> int:
    rows = list(read_jsonl(CORPUS))
    if not rows:
        print("[chart] no corpus — run src.harvest first", file=sys.stderr)
        return 1

    regex_counts = Counter(classify_wire_item(row["headline"]) for row in rows)
    section_counts = Counter(row["section"] for row in rows)
    outlets = {row["outlet"] for row in rows}

    charts.apply_theme()
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"wspace": 0.32})

    # ── Left: what the incumbent sees ────────────────────────────────────────────────
    labels = list(TOPIC_CLASSES)
    values = [regex_counts.get(label, 0) for label in labels]
    order = sorted(range(len(labels)), key=lambda i: -values[i])
    labels = [labels[i] for i in order]
    values = [values[i] for i in order]

    bars = left.barh(
        labels[::-1],
        values[::-1],
        color=[charts.CLASS_COLOURS[label] for label in labels[::-1]],
        height=0.68,
    )
    left.set_title("What the production regex sees", loc="left", pad=14)
    left.set_xlabel("headlines")
    charts.style_axes(left)
    left.grid(axis="x", color=charts.BORDER, linewidth=charts.HAIRLINE)
    left.grid(axis="y", visible=False)

    span = max(values) if values else 1
    for bar, value in zip(bars, values[::-1], strict=True):
        left.text(
            bar.get_width() + span * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,}  {value / len(rows):.0%}",
            va="center",
            fontsize=8.5,
            fontfamily=charts.MONO,
            color=charts.TEXT_SECONDARY,
        )
    left.set_xlim(0, span * 1.28)

    # ── Right: where the headlines came from ─────────────────────────────────────────
    sections = sorted(section_counts, key=lambda s: -section_counts[s])
    section_values = [section_counts[s] for s in sections]
    right.barh(sections[::-1], section_values[::-1], color=charts.TEXT_QUATERNARY, height=0.68)
    right.set_title("Where they were harvested from", loc="left", pad=14)
    right.set_xlabel("headlines")
    charts.style_axes(right)
    right.grid(axis="x", color=charts.BORDER, linewidth=charts.HAIRLINE)
    right.grid(axis="y", visible=False)

    span_r = max(section_values)
    for index, value in enumerate(section_values[::-1]):
        right.text(
            value + span_r * 0.02,
            index,
            f"{value:,}",
            va="center",
            fontsize=8.5,
            fontfamily=charts.MONO,
            color=charts.TEXT_SECONDARY,
        )
    right.set_xlim(0, span_r * 1.22)

    for axis in (left, right):
        charts.mono_ticks(axis, "x")

    fig.suptitle(
        f"{len(rows):,} headlines · {len(outlets)} outlets · harvested from public RSS",
        x=0.0,
        y=1.04,
        ha="left",
        fontsize=11,
        color=charts.TEXT,
        fontweight="semibold",
    )
    charts.caption(
        fig,
        "Left panel is the incumbent keyword regex, not ground truth — it is the thing being replaced. "
        "Teacher labels arrive in S4.",
    )

    path = charts.save(fig, "class_distribution.png")
    print(f"[chart] wrote {path}")
    print(f"[chart] regex sends {regex_counts['general'] / len(rows):.1%} of the corpus to `general`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
