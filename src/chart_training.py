"""charts/training_curve.png — parsed from the mlx-lm training log.

The brief calls a missing loss curve the first thing a reviewer notices, so this is a
deliverable rather than a diagnostic.

It is parsed from the log rather than instrumented into the trainer because mlx-lm's CLI is
what actually ran, and a curve reconstructed from the real run's stdout is harder to
accidentally misreport than one written by a wrapper that might not have been the code path
taken.

Any `nan` report is plotted as a visible gap and annotated rather than dropped. A silent
hole in a loss curve is the kind of thing that should be impossible to miss.

    uv run python -m src.chart_training --log /tmp/train.log
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from src import charts

TRAIN_RE = re.compile(r"^Iter (\d+): Train loss (nan|[\d.]+)", re.MULTILINE)
VAL_RE = re.compile(r"^Iter (\d+): Val loss (nan|[\d.]+)", re.MULTILINE)


def parse(text: str, pattern: re.Pattern[str]) -> list[tuple[int, float]]:
    points = []
    for match in pattern.finditer(text):
        value = match.group(2)
        points.append((int(match.group(1)), math.nan if value == "nan" else float(value)))
    return points


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot the training curve from an mlx-lm log.")
    parser.add_argument("--log", type=Path, default=Path("/tmp/train.log"))
    parser.add_argument("--out", default="training_curve.png")
    args = parser.parse_args()

    if not args.log.exists():
        print(f"[chart] no log at {args.log}", file=sys.stderr)
        return 1
    text = args.log.read_text(errors="replace")
    train = parse(text, TRAIN_RE)
    val = parse(text, VAL_RE)
    if not train:
        print("[chart] no training points found in the log", file=sys.stderr)
        return 1

    nans = [i for i, v in train if math.isnan(v)]

    charts.apply_theme()
    fig, ax = plt.subplots(figsize=(8.4, 4.4))

    ax.plot(
        [i for i, _ in train],
        [v for _, v in train],
        color=charts.ACCENT_GREEN,
        linewidth=1.6,
        label="train",
    )
    if val:
        ax.plot(
            [i for i, _ in val],
            [v for _, v in val],
            color=charts.TEXT_SECONDARY,
            linewidth=1.4,
            linestyle="--",
            marker="o",
            markersize=3.2,
            label="validation",
        )

    for iteration in nans:
        ax.axvline(iteration, color=charts.ACCENT_YELLOW, linewidth=charts.HAIRLINE, alpha=0.9)
        ax.annotate(
            "nan",
            xy=(iteration, ax.get_ylim()[1]),
            xytext=(0, -10),
            textcoords="offset points",
            ha="center",
            fontsize=7.5,
            fontfamily=charts.MONO,
            color=charts.ACCENT_YELLOW,
        )

    ax.set_yscale("log")
    ax.set_xlabel("iteration")
    ax.set_ylabel("loss (log scale)")
    ax.legend(loc="upper right", fontsize=9)
    charts.style_axes(ax)
    charts.mono_ticks(ax, "x")
    charts.mono_ticks(ax, "y")

    final_train = next((v for _, v in reversed(train) if not math.isnan(v)), float("nan"))
    final_val = next((v for _, v in reversed(val) if not math.isnan(v)), None) if val else None
    subtitle = f"final train {final_train:.4f}"
    if final_val is not None:
        subtitle += f" · final val {final_val:.4f}"
    if nans:
        subtitle += f" · {len(nans)} nan report window(s), marked"

    fig.suptitle(
        "Qwen3.5-4B · LoRA r=16 · bf16",
        x=0.0,
        y=1.06,
        ha="left",
        fontsize=11,
        color=charts.TEXT,
        fontweight="semibold",
    )
    fig.text(0.0, 1.005, subtitle, ha="left", fontsize=8.5, color=charts.TEXT_TERTIARY, fontfamily=charts.MONO)
    charts.caption(fig, "Parsed from the mlx-lm run log. Loss is masked to the answer tokens only (--mask-prompt).")

    path = charts.save(fig, args.out)
    print(f"[chart] wrote {path}")
    print(f"[chart] {len(train)} train points, {len(val)} val points, {len(nans)} nan(s) at {nans}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
