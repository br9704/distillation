"""The confusion matrix is a committed S7 artifact, so its construction is tested rather than
eyeballed.

The invariant that matters most is the `UNPARSEABLE` column. CLAUDE.md forbids coercing
unparseable output into a class — doing so biases the arm toward the majority class and hides
the failure. In a matrix that coercion would be completely invisible, so it gets its own
column or it does not appear at all.
"""

from __future__ import annotations

from src.chart_confusion import matrix
from src.schema import TOPIC_CLASSES, UNPARSEABLE


def pred(gold: str, predicted: str) -> dict:
    return {"gold": gold, "pred": predicted, "arm": "student"}


def test_rows_are_gold_and_cover_every_class() -> None:
    """A class absent from the held-out set still gets a row — the same reason macro-F1
    averages over all eight rather than over those present."""
    grid, columns = matrix([pred("tech", "tech")])
    assert len(grid) == len(TOPIC_CLASSES) == 8
    assert columns == list(TOPIC_CLASSES)


def test_counts_land_in_the_right_cell() -> None:
    rows = [pred("science", "tech"), pred("science", "tech"), pred("science", "science")]
    grid, columns = matrix(rows)
    r = TOPIC_CLASSES.index("science")
    assert grid[r][columns.index("tech")] == 2
    assert grid[r][columns.index("science")] == 1


def test_unparseable_gets_its_own_column_and_is_never_folded_into_a_class() -> None:
    rows = [pred("tech", UNPARSEABLE), pred("tech", "tech")]
    grid, columns = matrix(rows)
    assert columns[-1] == UNPARSEABLE
    r = TOPIC_CLASSES.index("tech")
    assert grid[r][columns.index(UNPARSEABLE)] == 1
    assert grid[r][columns.index("tech")] == 1
    # The unparseable row did not silently inflate `general`, the catch-all it would most
    # plausibly have been coerced into.
    assert grid[r][columns.index("general")] == 0


def test_no_unparseable_column_when_every_output_parsed() -> None:
    """The column is evidence of a problem. It should not appear when there isn't one."""
    _, columns = matrix([pred("tech", "tech")])
    assert UNPARSEABLE not in columns


def test_total_is_conserved() -> None:
    rows = [pred("tech", "tech"), pred("science", "general"), pred("sports", UNPARSEABLE)]
    grid, _ = matrix(rows)
    assert sum(sum(row) for row in grid) == len(rows)
