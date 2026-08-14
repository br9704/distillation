"""S3 guards: prompt integrity and the parser's refusal to guess.

None of these need the model. They cover the part that can silently corrupt a dataset — the
step between what the model said and what gets written to disk.
"""

from __future__ import annotations

import pytest

from src.schema import CLASS_DEFINITIONS, TOPIC_CLASSES, UNPARSEABLE
from src.teacher import PROMPT_VERSION, SYSTEM_PROMPT, TOPIC_SCHEMA, _parse, build_user_prompt


# ── The prompt ───────────────────────────────────────────────────────────────────────
def test_prompt_names_every_class_exactly_once():
    for label in TOPIC_CLASSES:
        assert SYSTEM_PROMPT.count(f"- {label}:") == 1, f"{label} missing or duplicated"


def test_prompt_is_built_from_the_schema_so_it_cannot_drift():
    """CLASS_DEFINITIONS lives beside TOPIC_CLASSES and is asserted equal to it there.
    The prompt is generated from that dict, so adding a class cannot leave the prompt stale."""
    for label, description in CLASS_DEFINITIONS.items():
        assert f"- {label}: {description}" in SYSTEM_PROMPT


def test_prompt_tells_the_model_general_is_not_a_default():
    """`general` being a dumping ground is the incumbent's defining failure. The teacher
    must not be invited to repeat it."""
    assert "not as a default" in SYSTEM_PROMPT


def test_constrained_decoding_enum_is_exactly_the_label_space():
    assert TOPIC_SCHEMA["properties"]["topic"]["enum"] == list(TOPIC_CLASSES)
    assert UNPARSEABLE not in TOPIC_SCHEMA["properties"]["topic"]["enum"]


def test_prompt_version_is_set():
    assert PROMPT_VERSION and isinstance(PROMPT_VERSION, str)


def test_user_prompt_carries_both_signals():
    prompt = build_user_prompt("Fed holds rates", "cnbc.com")
    assert "Fed holds rates" in prompt
    assert "cnbc.com" in prompt


# ── The parser ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "raw",
    [
        '{"topic": "finance"}',
        '{"topic":"finance"}',
        '  {"topic": "finance"}  ',
        '<think>The Fed is monetary policy.</think>{"topic": "finance"}',
        'Here is the answer:\n{"topic": "finance"}\n',
        "finance",
        "  Finance  ",
        "`finance`",
        '"finance."',
    ],
)
def test_parses_valid_answers_in_every_wrapper_the_model_might_use(raw):
    assert _parse(raw) == "finance"


def test_takes_the_last_json_object_so_reasoning_preamble_cannot_win():
    assert _parse('{"topic": "sports"} then reconsidered {"topic": "finance"}') == "finance"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "business",  # plausible, but not one of the eight
        "Finance and markets",
        '{"topic": "business"}',
        '{"topic": ""}',
        '{"label": "finance"}',  # wrong key
        "{broken json",
        "<error> TimeoutException: timed out",
        "I am not sure.",
        "general news",
    ],
)
def test_returns_none_rather_than_guessing(raw):
    assert _parse(raw) is None


def test_never_invents_general():
    """The single most important property in this file.

    Coercing a failed label to `general` would bias the teacher toward the majority class,
    and the majority class is already 74% of what the incumbent produces — so this is
    precisely the direction the data would be poisoned in. A failure must stay a failure.
    """
    for raw in ("", "unknown", "none of the above", "I cannot tell", '{"topic": "unclear"}'):
        assert _parse(raw) is None, f"{raw!r} was coerced instead of failing"


def test_parse_accepts_every_class():
    for label in TOPIC_CLASSES:
        assert _parse(f'{{"topic": "{label}"}}') == label
        assert _parse(label) == label
