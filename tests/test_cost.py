"""The cost model is the project's headline claim, so its arithmetic is checked by hand and
its inputs are checked for provenance.

The bug this suite exists to prevent has already happened once: `cost.py` hardcoded four token
constants under a docstring claiming they were "measured with the real tokeniser", and two of
them were wrong in the direction that flattered the headline. The fix was to read
`results/token_counts.json`, which `src/measure_tokens.py` produces. These tests hold that
line.
"""

from __future__ import annotations

import json

import pytest

from src import cost


def test_token_counts_come_from_the_committed_artifact() -> None:
    """Not from a literal in the module. This is the whole point of the refactor."""
    assert cost.TOKEN_COUNTS.exists(), "run `uv run python -m src.measure_tokens`"
    measured = json.loads(cost.TOKEN_COUNTS.read_text())["counts"]
    assert cost.TEACHER_INPUT_TOKENS == measured["teacher_input"]["mean"]
    assert cost.TEACHER_OUTPUT_TOKENS == measured["teacher_output"]["mean"]
    assert cost.STUDENT_INPUT_TOKENS == measured["student_input"]["mean"]
    assert cost.STUDENT_OUTPUT_TOKENS == measured["student_output"]["mean"]


def test_the_artifact_carries_its_own_caveats() -> None:
    """The teacher's weights were deleted in S4, so its tokens are counted with the student's
    tokeniser. That must travel with the number, not live only in a commit message."""
    payload = json.loads(cost.TOKEN_COUNTS.read_text())
    assert "tokenizer" in payload and payload["tokenizer"]["revision"]
    assert "caveat" in payload and "deleted" in payload["caveat"]
    assert payload["counts"]["student_input"]["n"] == 500


def test_the_student_input_is_not_the_stale_32() -> None:
    """32 was AMENDMENT A3's figure for a whole training example — a different quantity from a
    request's input, and low. Regression guard against it creeping back."""
    assert cost.STUDENT_INPUT_TOKENS > 33, "student input looks like the stale A3 constant"


def test_arithmetic_matches_a_hand_calculation() -> None:
    teacher_tokens = cost.TEACHER_INPUT_TOKENS + cost.TEACHER_OUTPUT_TOKENS
    student_tokens = cost.STUDENT_INPUT_TOKENS + cost.STUDENT_OUTPUT_TOKENS

    expected_teacher = teacher_tokens * 1000 * cost.RATE_MOE_56B / 1_000_000
    expected_student = student_tokens * 1000 * cost.RATE_SUB_4B / 1_000_000

    assert cost.TEACHER.cost_per_1k == pytest.approx(expected_teacher)
    assert cost.STUDENT.cost_per_1k == pytest.approx(expected_student)


def test_the_headline_decomposes_into_its_two_factors() -> None:
    """5x from the price tier times ~8x from the token count. If the two factors stop
    multiplying to the headline, one of them is being reported wrong."""
    data = cost.breakdown()
    head = data["headline"]
    price = head["decomposition"]["price_tier_factor"]
    tokens = head["decomposition"]["token_count_factor"]
    assert price * tokens == pytest.approx(head["student_cheaper_by"], rel=0.01)
    assert price == pytest.approx(5.0)


def test_the_regex_arm_is_free_and_says_why() -> None:
    arms = cost.breakdown()["arms"]
    assert arms["regex"]["cost_per_1k_requests"] == 0.0
    assert arms["regex"]["tokens_per_request"] == 0
    assert "pure function" in arms["regex"]["note"]


def test_the_list_price_disclaimer_is_unmissable() -> None:
    """CLAUDE.md: cost is arithmetic, latency is measured, and the two must never be blurred."""
    disclaimer = cost.breakdown()["disclaimer"]
    assert "NOT MEASURED SPEND" in disclaimer
    assert "$0" in disclaimer


def test_both_sensitivities_cut_against_the_headline() -> None:
    """A sensitivity analysis that only makes the result look better is marketing. Both rows
    here must be less favourable than the headline."""
    data = cost.breakdown()
    headline = data["headline"]["student_cheaper_by"]
    for name, row in data["sensitivity"].items():
        assert row["student_cheaper_by"] < headline, f"{name} does not cut against the headline"


def test_missing_artifact_raises_rather_than_falling_back() -> None:
    """A silent fallback to hardcoded numbers is how the original bug survived."""
    original = cost.TOKEN_COUNTS
    try:
        cost.TOKEN_COUNTS = original.with_name("token_counts_absent.json")
        with pytest.raises(FileNotFoundError, match="measure_tokens"):
            cost._measured()
    finally:
        cost.TOKEN_COUNTS = original
