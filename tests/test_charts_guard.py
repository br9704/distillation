"""The amber guard `src/charts.py` promised.

`charts.py` states, in its own module docstring: "Amber `#FF9500` is RESERVED for collision
alerts. It must not appear in any chart in this repo. **A test asserts this.**"

No such test existed. That is a false claim in committed code, and it left the S8 acceptance
criterion ("no amber in any chart") with nothing enforcing it. This file is that test.

It checks two things, because either alone is escapable:

1. **No chart module names the reserved colour.** A source-level scan, so a chart cannot use
   amber by hardcoding the hex even if it never touches `charts.ACCENT_AMBER`.
2. **No committed PNG contains amber pixels.** A pixel-level scan of `charts/`, so a colour
   arriving through a matplotlib colormap — the likeliest accidental route, since several of
   the default ramps pass straight through orange — is caught too.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
CHARTS = ROOT / "charts"

AMBER = (0xFF, 0x95, 0x00)
AMBER_HEX = re.compile(r"#ff9500", re.IGNORECASE)

# The one legal mention: `charts.py` defines the constant so this suite has something to assert
# against, and says so on the line above it. Every other chart module is in scope.
ALLOWED_TO_NAME_AMBER = {"charts.py"}

CHART_MODULES = sorted(p for p in SRC.glob("chart*.py") if p.name not in ALLOWED_TO_NAME_AMBER)


def test_charts_py_defines_the_reserved_colour() -> None:
    """If the constant is renamed or removed, this test should fail loudly rather than pass
    vacuously — a guard that silently stops guarding is worse than no guard."""
    from src import charts

    assert charts.ACCENT_AMBER.lower() == "#ff9500"


@pytest.mark.parametrize("module", CHART_MODULES, ids=lambda p: p.name)
def test_no_chart_module_hardcodes_amber(module: Path) -> None:
    assert not AMBER_HEX.search(module.read_text()), (
        f"{module.name} names the reserved collision-alert colour #FF9500. "
        f"Use --accent-yellow #FFD60A for warnings or --accent-red #FF3B30 for errors."
    )


def test_no_chart_module_uses_the_amber_constant() -> None:
    """`charts.ACCENT_AMBER` exists only so this suite can assert against it."""
    offenders = [m.name for m in CHART_MODULES if "ACCENT_AMBER" in m.read_text()]
    assert not offenders, f"these modules reference the reserved colour: {offenders}"


def _amberish(pixel: tuple[int, int, int], tolerance: int = 18) -> bool:
    return all(abs(channel - target) <= tolerance for channel, target in zip(pixel, AMBER))


@pytest.mark.parametrize(
    "png", sorted(CHARTS.glob("*.png")) or [None], ids=lambda p: p.name if p else "no-charts-yet"
)
def test_committed_charts_contain_no_amber_pixels(png: Path | None) -> None:
    if png is None:
        pytest.skip("no charts committed yet")
    Image = pytest.importorskip("PIL.Image", reason="Pillow not installed")

    with Image.open(png) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        # tobytes() rather than getdata(): getdata() is deprecated in Pillow 14, and a flat
        # bytes buffer is faster over a ~1.9M-pixel chart anyway.
        raw = rgb.tobytes()

    offenders = sum(
        1 for i in range(0, len(raw), 3) if _amberish((raw[i], raw[i + 1], raw[i + 2]))
    )
    total = width * height
    # A hard zero is the honest threshold: nothing in the token palette is within 18 of amber,
    # so any hit is a real one rather than antialiasing between two legal colours.
    assert offenders == 0, (
        f"{png.name} contains {offenders} amber-ish pixels of {total} "
        f"({offenders / total:.4%}). Amber #FF9500 is reserved for collision alerts."
    )
