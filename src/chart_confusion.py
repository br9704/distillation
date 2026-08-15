"""charts/confusion_<arm>.png — one confusion matrix per scored arm.

S7 requires committed confusion matrices. They are drawn from `results/predictions.jsonl`, so
the chart and `results/summary.json` cannot disagree — both read the same predictions.

Design notes, all inherited rather than invented (see `src/charts.py`):

- The heat ramp runs from the field colour to **`--accent-green #34C759`**, the brand accent.
  A conventional matplotlib colormap would drag in colours the token file does not own —
  including amber, which is reserved for collision alerts and must not appear in this repo.
- The diagonal is what a reader looks for first, so it is outlined rather than merely shaded.
- Cell counts use Geist Mono. Numerals in a table are the one place mono is correct.
- Rows are normalised per gold class, because the classes are wildly unbalanced and a raw
  count matrix would just redraw the class distribution. Raw counts are printed inside the
  cells so nothing is hidden by the normalisation.

Gold is the teacher's label, so this is an *agreement* matrix for the student and regex arms.
The caption says so on every chart rather than leaving it to the README.

    uv run python -m src.chart_confusion
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

from src import charts
from src.schema import TOPIC_CLASSES, UNPARSEABLE
from src.store import read_jsonl

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# field -> green. Built from tokens, so no external colormap can smuggle in a reserved colour.
RAMP = LinearSegmentedColormap.from_list(
    "aethereum_green", [charts.BG, "#0f2a18", "#1c5a30", "#2a8f43", charts.ACCENT_GREEN], N=256
)


def matrix(predictions: list[dict]) -> tuple[list[list[int]], list[str]]:
    """Rows are gold, columns are predicted. UNPARSEABLE gets its own column when present."""
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in predictions:
        counts[(row["gold"], row["pred"])] += 1

    columns = list(TOPIC_CLASSES)
    if any(row["pred"] == UNPARSEABLE for row in predictions):
        # Never folded into a class. Silently coercing unparseable output to `general` is the
        # exact bias CLAUDE.md forbids, and it would be invisible in a matrix.
        columns.append(UNPARSEABLE)

    grid = [[counts.get((gold, pred), 0) for pred in columns] for gold in TOPIC_CLASSES]
    return grid, columns


def draw(arm: str, grid: list[list[int]], columns: list[str], out: str) -> Path:
    charts.apply_theme()
    fig, ax = plt.subplots(figsize=(1.0 + 0.72 * len(columns), 0.72 * len(TOPIC_CLASSES) + 1.6))

    normalised = []
    for row in grid:
        total = sum(row)
        normalised.append([(value / total if total else 0.0) for value in row])

    ax.imshow(normalised, cmap=RAMP, vmin=0.0, vmax=1.0, aspect="auto", interpolation="nearest")

    for r, gold in enumerate(TOPIC_CLASSES):
        for c, pred in enumerate(columns):
            value = grid[r][c]
            if not value:
                continue
            share = normalised[r][c]
            # White on a saturated cell, secondary text on a dark one — legibility, not decoration.
            colour = charts.BG if share > 0.55 else charts.TEXT_SECONDARY
            ax.text(c, r, str(value), ha="center", va="center",
                    fontsize=8.5, fontfamily=charts.MONO, color=colour)
            if gold == pred:
                ax.add_patch(
                    Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                              edgecolor=charts.ACCENT_GREEN, linewidth=1.0)
                )

    ax.set_xticks(range(len(columns)))
    ax.set_yticks(range(len(TOPIC_CLASSES)))
    ax.set_xticklabels(columns, rotation=40, ha="right", fontsize=8.5)
    ax.set_yticklabels(TOPIC_CLASSES, fontsize=8.5)
    ax.set_xlabel("predicted")
    ax.set_ylabel("gold (teacher label)")
    ax.grid(False)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)

    total = sum(sum(row) for row in grid)
    agreed = sum(grid[r][columns.index(cls)] for r, cls in enumerate(TOPIC_CLASSES) if cls in columns)
    fig.suptitle(f"{arm} · confusion", x=0.0, y=1.04, ha="left", fontsize=11,
                 color=charts.TEXT, fontweight="semibold")
    fig.text(0.0, 0.995, f"{agreed}/{total} on the diagonal · cells are counts, shading is row-normalised",
             ha="left", fontsize=8.5, color=charts.TEXT_TERTIARY, fontfamily=charts.MONO)
    charts.caption(
        fig,
        "Gold is the teacher's label, so this is agreement, not correctness. "
        "Teacher-vs-human agreement was 84% (results/audit_50.md).",
    )
    return charts.save(fig, out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw a confusion matrix per arm.")
    parser.add_argument("--predictions", type=Path, default=RESULTS / "predictions.jsonl")
    parser.add_argument("--arm", default=None, help="only this arm (default: every scored arm)")
    args = parser.parse_args()

    if not args.predictions.exists():
        print(f"[confusion] no predictions at {args.predictions} — run src.evaluate first", file=sys.stderr)
        return 1

    by_arm: dict[str, list[dict]] = defaultdict(list)
    for row in read_jsonl(args.predictions):
        by_arm[row["arm"]].append(row)
    if args.arm:
        by_arm = {args.arm: by_arm.get(args.arm, [])}

    wrote = 0
    for arm, rows in sorted(by_arm.items()):
        if not rows:
            print(f"[confusion] no rows for arm {arm}", file=sys.stderr)
            continue
        grid, columns = matrix(rows)
        path = draw(arm, grid, columns, f"confusion_{arm}.png")
        print(f"[confusion] {arm:<8} {len(rows):>4} rows -> {path.relative_to(ROOT)}")
        wrote += 1
    return 0 if wrote else 1


if __name__ == "__main__":
    sys.exit(main())
