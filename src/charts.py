"""Matplotlib theme inherited from the Aethereum design system.

Source of truth: `~/Desktop/hive/apps/web/styles/tokens.css`. Nothing here is invented —
every value is a token from that file, transcribed. Per CLAUDE.md, Bruno designs nothing
for this project.

Three rules carried over verbatim from the tokens file:

  1. **Premium dark, never flat.** The canvas is a deep tinted field with a single light
     source, not pure grey on black.
  2. **Mono is for code and numerals.** Geist for labels and titles, Geist Mono only for
     tick numbers and tabular figures — never for headings or body.
  3. **Amber `#FF9500` is RESERVED for collision alerts.** It must not appear in any chart
     in this repo. `--accent-yellow #FFD60A` is the warning colour; `--accent-red #FF3B30`
     is for errors. A test asserts this.

The categorical palette is `--id-ring-1..8`, the agent-identity ring colours. They are the
right choice for the eight topic classes for the reason the tokens file gives: they are
designed to be mutually distinguishable, and they deliberately exclude green and amber,
which are load-bearing signal colours. Eight tokens, eight classes — no invention needed.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
from matplotlib import font_manager

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from src.schema import TOPIC_CLASSES  # noqa: E402

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
CHARTS = Path(__file__).resolve().parent.parent / "charts"

# ── Tokens, transcribed from tokens.css ──────────────────────────────────────────────
BG = "#000000"  # --bg, the composite floor
FIELD_TOP = "#101014"  # --bg-field-top, the lightest stop
SURFACE = "#18181b"  # --surface at full opacity
TEXT = "#ffffff"  # --text
TEXT_SECONDARY = "#b8b8b8"  # --text-secondary, rgba(255,255,255,0.72) over the field
TEXT_TERTIARY = "#9e9e9e"  # --text-tertiary, rgba(255,255,255,0.62)
TEXT_QUATERNARY = "#4d4d4d"  # --text-quaternary, chrome only — never copy
BORDER = "#232326"  # --border, rgba(255,255,255,0.08)
BORDER_STRONG = "#2b2b30"  # --border-strong, rgba(255,255,255,0.15)

ACCENT_GREEN = "#34c759"  # --accent-live / --accent-brand
ACCENT_BLUE = "#007aff"  # --accent-blue
ACCENT_YELLOW = "#ffd60a"  # --accent-yellow — warnings. Reach for this, NOT amber.
ACCENT_RED = "#ff3b30"  # --accent-red — errors
ACCENT_AMBER = "#ff9500"  # --accent-alert — RESERVED. Never used in a chart. Named only
#                            so the guard test has something to assert against.

# --id-ring-1..8, in token order.
ID_RINGS: tuple[str, ...] = (
    "#5e9bff",  # blue
    "#bf7bff",  # violet
    "#ff7ab6",  # pink
    "#32d7e0",  # cyan
    "#f5c451",  # gold
    "#4fd1c5",  # teal
    "#ff8a5e",  # coral
    "#a0aab8",  # slate
)

CLASS_COLOURS: dict[str, str] = dict(zip(TOPIC_CLASSES, ID_RINGS, strict=True))

# Arm colours. The student is the brand green because it is the thing being argued for;
# the teacher is neutral slate because it is the ceiling, not the claim; the incumbent is
# quaternary because it is the thing being replaced.
ARM_COLOURS: dict[str, str] = {
    "regex": TEXT_QUATERNARY,
    "teacher": "#a0aab8",
    "student": ACCENT_GREEN,
}

HAIRLINE = 0.5  # --hairline-w


def _register_fonts() -> tuple[str, str]:
    """Register the vendored Geist faces. Falls back to system fonts if absent."""
    sans, mono = "Helvetica Neue", "Menlo"
    if ASSETS.is_dir():
        for path in sorted(ASSETS.glob("*.ttf")):
            try:
                font_manager.fontManager.addfont(str(path))
            except Exception:  # noqa: BLE001 — a missing font must never break a run
                continue
        names = {f.name for f in font_manager.fontManager.ttflist}
        if "Geist" in names:
            sans = "Geist"
        if "Geist Mono" in names:
            mono = "Geist Mono"
    return sans, mono


SANS, MONO = _register_fonts()


def apply_theme() -> None:
    """Install the theme globally. Call once before plotting."""
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "figure.edgecolor": BG,
            "savefig.facecolor": BG,
            "savefig.edgecolor": BG,
            "axes.facecolor": BG,
            "axes.edgecolor": BORDER,
            "axes.linewidth": HAIRLINE,
            "axes.labelcolor": TEXT_SECONDARY,
            "axes.titlecolor": TEXT,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": BORDER,
            "grid.linewidth": HAIRLINE,
            "grid.alpha": 1.0,
            "text.color": TEXT,
            "xtick.color": TEXT_TERTIARY,
            "ytick.color": TEXT_TERTIARY,
            "xtick.labelcolor": TEXT_TERTIARY,
            "ytick.labelcolor": TEXT_TERTIARY,
            "xtick.major.width": HAIRLINE,
            "ytick.major.width": HAIRLINE,
            "font.family": [SANS],
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.titleweight": "semibold",
            "axes.labelsize": 10,
            "legend.frameon": False,
            "legend.labelcolor": TEXT_SECONDARY,
            "figure.dpi": 160,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.3,
        }
    )


def style_axes(ax) -> None:
    """Strip chart junk: no top or right spine, hairline elsewhere, horizontal grid only."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(HAIRLINE)
        ax.spines[side].set_color(BORDER_STRONG)
    ax.grid(axis="y", color=BORDER, linewidth=HAIRLINE)
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)


def mono_ticks(ax, axis: str = "y") -> None:
    """Tabular figures on the numeric axis — the one place mono is correct."""
    labels = ax.get_yticklabels() if axis == "y" else ax.get_xticklabels()
    for label in labels:
        label.set_fontfamily(MONO)


def caption(fig, text: str) -> None:
    """A provenance line under the chart. Every chart in this repo carries one."""
    fig.text(0.0, -0.02, text, color=TEXT_QUATERNARY, fontsize=7.5, fontfamily=MONO, ha="left", va="top")


def save(fig, name: str) -> Path:
    CHARTS.mkdir(parents=True, exist_ok=True)
    path = CHARTS / name
    fig.savefig(path)
    plt.close(fig)
    return path
