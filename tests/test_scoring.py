"""The scorer is the instrument every result in this repo is measured with, so it is
verified against a fixture whose macro-F1 was computed by hand rather than by the code
under test.
"""

from __future__ import annotations

import math

import pytest

from src.schema import TOPIC_CLASSES
from src.scoring import confusion_pairs, percentile, score

# ── The hand-computed fixture ────────────────────────────────────────────────────────
#
#   idx   true        pred
#   0     tech        tech        ✓
#   1     tech        tech        ✓
#   2     tech        finance     ✗
#   3     finance     finance     ✓
#   4     finance     tech        ✗
#   5     sports      sports      ✓
#
# By hand:
#   tech      tp=2 fp=1 fn=1  → P=2/3      R=2/3   F1=2/3
#   finance   tp=1 fp=1 fn=1  → P=1/2      R=1/2   F1=1/2
#   sports    tp=1 fp=0 fn=0  → P=1        R=1     F1=1
#   the other five classes never occur and are never predicted → F1 = 0 each
#
#   accuracy  = 4/6                                = 0.666666…
#   macro-F1  = (2/3 + 1/2 + 1 + 0+0+0+0+0) / 8    = 2.166666… / 8 = 0.270833…
Y_TRUE = ["tech", "tech", "tech", "finance", "finance", "sports"]
Y_PRED = ["tech", "tech", "finance", "finance", "tech", "sports"]

EXPECTED_ACCURACY = 4 / 6
EXPECTED_MACRO_F1 = (2 / 3 + 1 / 2 + 1.0) / 8


def test_accuracy_matches_hand_computation():
    assert math.isclose(score(Y_TRUE, Y_PRED).accuracy, EXPECTED_ACCURACY)


def test_macro_f1_matches_hand_computation():
    assert math.isclose(score(Y_TRUE, Y_PRED).macro_f1, EXPECTED_MACRO_F1)


def test_macro_f1_averages_over_all_eight_classes_not_just_present_ones():
    """Pins the averaging convention documented in scoring.py.

    Averaging over only the three classes present would give 0.7222 — nearly 3x flattering.
    That is the number scikit-learn's default would produce, and adopting it silently would
    hide exactly the tail-class failure this project exists to surface.
    """
    result = score(Y_TRUE, Y_PRED).macro_f1
    flattering = (2 / 3 + 1 / 2 + 1.0) / 3
    assert math.isclose(result, EXPECTED_MACRO_F1)
    assert not math.isclose(result, flattering)
    assert result < flattering


def test_per_class_covers_every_class_including_absent_ones():
    per_class = {c.label: c for c in score(Y_TRUE, Y_PRED).per_class}
    assert set(per_class) == set(TOPIC_CLASSES)

    assert math.isclose(per_class["tech"].f1, 2 / 3)
    assert per_class["tech"].support == 3
    assert math.isclose(per_class["finance"].f1, 0.5)
    assert per_class["finance"].support == 2
    assert math.isclose(per_class["sports"].f1, 1.0)
    assert per_class["sports"].support == 1

    # A class that never occurs scores 0.0, not NaN, and is not omitted.
    assert per_class["consumer"].f1 == 0.0
    assert per_class["consumer"].support == 0


def test_perfect_prediction_scores_one_only_when_every_class_is_present():
    """A perfect score on a subset of classes is still not a macro-F1 of 1.0."""
    subset = score(["tech", "finance"], ["tech", "finance"])
    assert subset.accuracy == 1.0
    assert math.isclose(subset.macro_f1, 2 / 8)

    everything = list(TOPIC_CLASSES)
    assert score(everything, everything).macro_f1 == 1.0


def test_confusion_matrix_is_dense_and_counts_correctly():
    confusion = score(Y_TRUE, Y_PRED).confusion
    assert set(confusion) == set(TOPIC_CLASSES)
    assert all(set(row) == set(TOPIC_CLASSES) for row in confusion.values())
    assert confusion["tech"]["tech"] == 2
    assert confusion["tech"]["finance"] == 1
    assert confusion["finance"]["tech"] == 1
    assert sum(sum(row.values()) for row in confusion.values()) == len(Y_TRUE)


def test_confusion_pairs_excludes_the_diagonal_and_ranks_by_count():
    pairs = confusion_pairs(score(Y_TRUE, Y_PRED))
    assert all(t != p for t, p, _ in pairs)
    assert {(t, p) for t, p, _ in pairs} == {("tech", "finance"), ("finance", "tech")}


def test_unparseable_must_be_filtered_by_the_caller_not_absorbed_here():
    """Guards the rule in schema.py: UNPARSEABLE is not a ninth class."""
    with pytest.raises(ValueError, match="outside TOPIC_CLASSES"):
        score(["tech"], ["UNPARSEABLE"])


def test_length_mismatch_and_empty_input_are_errors():
    with pytest.raises(ValueError, match="length mismatch"):
        score(["tech", "finance"], ["tech"])
    with pytest.raises(ValueError, match="empty"):
        score([], [])


# ── Latency percentiles ──────────────────────────────────────────────────────────────
def test_percentile_is_nearest_rank_and_returns_an_observed_value():
    values = [float(v) for v in range(1, 11)]  # 1..10
    assert percentile(values, 50) == 5.0
    assert percentile(values, 95) == 10.0
    assert percentile(values, 100) == 10.0
    # Every result is a value that was actually observed — never an interpolation.
    assert all(percentile(values, q) in values for q in (1, 25, 50, 75, 90, 95, 99, 100))


def test_percentile_handles_a_single_observation():
    assert percentile([7.5], 50) == 7.5
    assert percentile([7.5], 95) == 7.5


def test_percentile_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        percentile([], 95)
