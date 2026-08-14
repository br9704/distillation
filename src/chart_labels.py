"""charts/label_distribution.png — the incumbent's error profile, on the held-out 500.

Two panels.

**Left** is the direct comparison: what the regex assigns versus what the teacher assigns, on
exactly the same 500 headlines. The `general` bars are the story — one arm's largest class is
the other's fourth.

**Right** is the one that actually explains it. It takes only the headlines the regex called
`general` and shows what the teacher called them. If the regex's catch-all were doing its job
this bar would be almost entirely `general` too. It is not, and the shape of what spills out
is the specification for what the student has to learn.

    uv run python -m src.chart_labels
"""

from __future__ import annotations

import sys
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from src import charts
from src.regex_baseline import classify_wire_item
from src.schema import TOPIC_CLASSES, UNPARSEABLE
from src.store import DATA, read_jsonl


def main() -> int:
    examples = {row["id"]: row for row in read_jsonl(DATA / "heldout.jsonl")}
    labels = [row for row in read_jsonl(DATA / "heldout_labels.jsonl") if row["label"] != UNPARSEABLE]
    if not labels:
        print("[chart] no teacher labels yet — run src.teacher first", file=sys.stderr)
        return 1

    pairs = [(classify_wire_item(examples[row["id"]]["headline"]), row["label"]) for row in labels]
    regex_counts = Counter(regex for regex, _ in pairs)
    teacher_counts = Counter(teacher for _, teacher in pairs)
    spill = Counter(teacher for regex, teacher in pairs if regex == "general")
    n = len(pairs)

    charts.apply_theme()
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.6, 4.8), gridspec_kw={"wspace": 0.34})

    # ── Left: regex vs teacher on the same 500 ───────────────────────────────────────
    order = sorted(TOPIC_CLASSES, key=lambda c: -teacher_counts.get(c, 0))
    y = np.arange(len(order))
    height = 0.38

    left.barh(
        y + height / 2,
        [teacher_counts.get(c, 0) for c in order],
        height=height,
        color=charts.ARM_COLOURS["teacher"],
        label="teacher (Qwen3.5-35B-A3B)",
    )
    left.barh(
        y - height / 2,
        [regex_counts.get(c, 0) for c in order],
        height=height,
        color=charts.ARM_COLOURS["regex"],
        label="regex (incumbent)",
    )
    left.set_yticks(y, order)
    left.invert_yaxis()
    left.set_xlabel("headlines")
    left.set_title(f"Same {n} held-out headlines, two labellers", loc="left", pad=14)
    left.legend(loc="lower right", fontsize=8.5)
    charts.style_axes(left)
    left.grid(axis="x", color=charts.BORDER, linewidth=charts.HAIRLINE)
    left.grid(axis="y", visible=False)

    widest = max(max(regex_counts.values()), max(teacher_counts.values()))
    for index, name in enumerate(order):
        for offset, counts in ((height / 2, teacher_counts), (-height / 2, regex_counts)):
            value = counts.get(name, 0)
            left.text(
                value + widest * 0.015,
                index + offset,
                str(value),
                va="center",
                fontsize=7.5,
                fontfamily=charts.MONO,
                color=charts.TEXT_TERTIARY,
            )
    left.set_xlim(0, widest * 1.14)

    # ── Right: where the regex's `general` pile actually belongs ─────────────────────
    total_spill = sum(spill.values())
    spill_order = sorted(TOPIC_CLASSES, key=lambda c: -spill.get(c, 0))
    spill_values = [spill.get(c, 0) for c in spill_order]

    bars = right.barh(
        spill_order[::-1],
        spill_values[::-1],
        color=[charts.CLASS_COLOURS[c] for c in spill_order[::-1]],
        height=0.68,
    )
    right.set_xlabel("headlines")
    right.set_title(
        f"The {total_spill} the regex called `general`,\nas labelled by the teacher",
        loc="left",
        pad=14,
        fontsize=11,
    )
    charts.style_axes(right)
    right.grid(axis="x", color=charts.BORDER, linewidth=charts.HAIRLINE)
    right.grid(axis="y", visible=False)

    span = max(spill_values) if spill_values else 1
    for bar, value in zip(bars, spill_values[::-1], strict=True):
        if value:
            right.text(
                bar.get_width() + span * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{value}  {value / total_spill:.0%}",
                va="center",
                fontsize=8.5,
                fontfamily=charts.MONO,
                color=charts.TEXT_SECONDARY,
            )
    right.set_xlim(0, span * 1.3)

    for axis in (left, right):
        charts.mono_ticks(axis, "x")

    misrouted = total_spill - spill.get("general", 0)
    fig.suptitle(
        f"The incumbent sends {regex_counts.get('general', 0) / n:.0%} of headlines to `general`. "
        f"The teacher agrees with {spill.get('general', 0) / total_spill:.0%} of that pile.",
        x=0.0,
        y=1.05,
        ha="left",
        fontsize=11,
        color=charts.TEXT,
        fontweight="semibold",
    )
    charts.caption(
        fig,
        f"Held-out set, n={n}, never trained on. Teacher labels are a model's opinion, not truth — "
        f"hand audit puts agreement at 84% (results/audit_50.md).",
    )

    path = charts.save(fig, "label_distribution.png")
    print(f"[chart] wrote {path}")
    print(f"[chart] regex `general`: {regex_counts.get('general', 0)}/{n} ({regex_counts.get('general', 0) / n:.1%})")
    print(f"[chart] teacher `general`: {teacher_counts.get('general', 0)}/{n} ({teacher_counts.get('general', 0) / n:.1%})")
    print(f"[chart] of the regex `general` pile, the teacher reassigns {misrouted}/{total_spill} ({misrouted / total_spill:.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
