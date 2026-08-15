"""Error analysis is the part of S7 that turns numbers into findings, so its bucketing is
tested against hand-constructed cases where the correct bucket is unambiguous.

The one that matters most is `student_loses`: CLAUDE.md says any class where the student loses
to the regex leads the README. If that flag can be wrong, the repo's headline can be wrong.
"""

from __future__ import annotations

import pytest

from src.error_analysis import band, confused_pairs, head_to_head, per_class_gap, taxonomy
from src.schema import UNPARSEABLE


def row(gold: str, pred: str, headline: str = "x", **extra) -> dict:
    return {
        "id": extra.get("id", headline),
        "gold": gold,
        "pred": pred,
        "headline": headline,
        "outlet": extra.get("outlet", "Reuters"),
        "tier": extra.get("tier", 1),
        "correct": gold == pred,
    }


class TestTaxonomy:
    def test_regex_catch_all_is_its_own_cause(self) -> None:
        errors = [row("science", "general", "NASA probe reaches Jupiter orbit")]
        buckets = taxonomy(errors, "regex")
        assert any("catch-all" in name for name in buckets)

    def test_the_china_rule_is_named_as_the_mechanism(self) -> None:
        """Visible in the incumbent's source: any headline containing `china` returns
        geopolitics before any later branch can run."""
        errors = [row("consumer", "geopolitics", "China shopping festival breaks records")]
        buckets = taxonomy(errors, "regex")
        assert any("china" in name for name in buckets)

    def test_a_china_headline_predicted_as_something_else_is_not_blamed_on_the_china_rule(self) -> None:
        errors = [row("finance", "tech", "China chipmaker lists in Shanghai")]
        buckets = taxonomy(errors, "regex")
        assert not any("china" in name for name in buckets)

    def test_unparseable_is_never_folded_into_a_class(self) -> None:
        """CLAUDE.md forbids coercing unparseable output to a class — it must stay visible."""
        errors = [row("tech", UNPARSEABLE, "Anything")]
        buckets = taxonomy(errors, "student")
        assert "unparseable output" in buckets

    def test_student_causes_stay_coarse(self) -> None:
        """Inventing fine-grained causes for a neural model's errors would be storytelling."""
        errors = [row("science", "tech", "SpaceX launches Starlink batch")]
        buckets = taxonomy(errors, "student")
        assert "cross-domain confusion: science vs tech" in buckets

    def test_shares_sum_to_one(self) -> None:
        errors = [
            row("science", "general", "a"),
            row("consumer", "geopolitics", "China sale"),
            row("tech", UNPARSEABLE, "c"),
        ]
        buckets = taxonomy(errors, "regex")
        # Shares are rounded to four places for the report, so they sum to 1 within rounding.
        assert sum(b["share_of_errors"] for b in buckets.values()) == pytest.approx(1.0, abs=1e-3)


class TestBands:
    def test_length_bands_partition_every_headline(self) -> None:
        for length in (0, 39, 40, 69, 70, 89, 90, 400):
            assert band("x" * length)

    def test_boundaries_land_in_the_expected_band(self) -> None:
        assert "short" in band("x" * 39)
        assert "medium" in band("x" * 40)
        assert "very long" in band("x" * 90)


class TestHeadToHead:
    def test_wins_are_attributed_to_the_right_arm(self) -> None:
        student = [row("consumer", "consumer", "Amazon Prime Day deals", id="1")]
        regex = [row("consumer", "tech", "Amazon Prime Day deals", id="1")]
        result = head_to_head(student, regex)
        assert result["student_right_regex_wrong"]["n"] == 1
        assert result["regex_right_student_wrong"]["n"] == 0
        assert result["student_right_regex_wrong"]["examples"][0]["regex_said"] == "tech"

    def test_a_regex_win_is_recorded_first_class(self) -> None:
        student = [row("sports", "general", "Team wins final", id="1")]
        regex = [row("sports", "sports", "Team wins final", id="1")]
        result = head_to_head(student, regex)
        assert result["regex_right_student_wrong"]["n"] == 1
        assert result["regex_right_student_wrong"]["examples"][0]["student_said"] == "general"

    def test_rows_missing_from_one_arm_are_skipped_not_counted_as_wins(self) -> None:
        student = [row("tech", "tech", "a", id="1"), row("tech", "tech", "b", id="2")]
        regex = [row("tech", "general", "a", id="1")]
        result = head_to_head(student, regex)
        assert result["student_right_regex_wrong"]["n"] == 1


class TestPerClassGap:
    def test_student_loses_is_flagged_when_the_regex_is_better(self) -> None:
        """This flag decides what leads the README."""
        student = [row("sports", "general", "a", id="1"), row("sports", "sports", "b", id="2")]
        regex = [row("sports", "sports", "a", id="1"), row("sports", "sports", "b", id="2")]
        gap = per_class_gap(student, regex)
        assert gap["sports"]["student_agreement"] == 0.5
        assert gap["sports"]["regex_agreement"] == 1.0
        assert gap["sports"]["student_loses"] is True
        assert gap["sports"]["student_minus_regex"] == -0.5

    def test_a_tie_is_not_a_loss(self) -> None:
        student = [row("tech", "tech", "a", id="1")]
        regex = [row("tech", "tech", "a", id="1")]
        assert per_class_gap(student, regex)["tech"]["student_loses"] is False

    def test_every_class_is_reported_even_with_no_gold_examples(self) -> None:
        """A class the held-out set never contains must not vanish from the table — that is
        the same silent-forgiveness failure the macro-F1 convention exists to prevent."""
        gap = per_class_gap([row("tech", "tech", "a", id="1")], [row("tech", "tech", "a", id="1")])
        assert len(gap) == 8
        assert gap["consumer"]["n_gold"] == 0


def test_confused_pairs_ranks_by_frequency_and_ignores_correct_rows() -> None:
    rows = [
        row("science", "tech", "a"),
        row("science", "tech", "b"),
        row("consumer", "tech", "c"),
        row("tech", "tech", "d"),
    ]
    pairs = confused_pairs(rows)
    assert pairs[0] == {"gold": "science", "pred": "tech", "n": 2}
    assert all(p["gold"] != p["pred"] for p in pairs)
