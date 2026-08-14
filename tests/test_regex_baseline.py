"""Pins the incumbent's behaviour, bugs included.

If one of these tests ever starts failing it means someone "fixed" the port. Don't. The
production function behaves this way, and the whole comparison depends on the incumbent
arm being the incumbent rather than an improved version of it.
"""

from __future__ import annotations

import pytest

from src.regex_baseline import classify_wire_item
from src.schema import TOPIC_CLASSES


# ── The bugs, pinned ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "headline",
    [
        "Amazon Prime Day deals begin Tuesday",
        "Amazon Prime members get free delivery",
    ],
)
def test_amazon_prime_is_tech_because_the_tech_rule_runs_first(headline):
    """Bug 1. `amazon` is in the tech rule, checked before consumer, so the consumer
    rule's own `amazon prime` keyword is unreachable — dead code in production."""
    assert classify_wire_item(headline) == "tech"


def test_spacex_is_tech_never_science():
    """Bug 2. `spacex` appears in both the tech and science rules; tech wins on order,
    so the science occurrence can never fire."""
    assert classify_wire_item("SpaceX launches Starship on eleventh test flight") == "tech"
    # Same story without the brand name: this one reaches science.
    assert classify_wire_item("Starship reaches orbit in test launch to Mars") == "science"


@pytest.mark.parametrize(
    ("headline", "why"),
    [
        ("China's Singles Day shopping festival breaks records", "should be consumer"),
        ("Korea's Netflix hit tops the charts worldwide", "should be entertainment"),
        ("Russia's tennis star advances at Wimbledon", "should be sports"),
    ],
)
def test_a_country_name_anywhere_forces_geopolitics(headline, why):
    """Bug 3. Country names sit in the geopolitics rule, checked second, so any headline
    mentioning one is geopolitics regardless of what it is actually about."""
    assert classify_wire_item(headline) == "geopolitics", why


def test_general_is_a_catch_all_not_a_class():
    """Bug 5, and the reason macro-F1 rather than accuracy is the headline metric."""
    assert classify_wire_item("Local council approves new park on Riverside Drive") == "general"
    assert classify_wire_item("Heavy rain expected across the south this weekend") == "general"


# ── ASCII word-boundary semantics ────────────────────────────────────────────────────
def test_word_boundaries_use_ascii_semantics_like_javascript():
    """JavaScript's \\b is ASCII-based; Python's is Unicode-aware by default.

    In "Iraníes", `í` is a word character to Python but not to JS, so default-mode Python
    would find no boundary after "Iran" and return `general`, while production returns
    `geopolitics`. `re.ASCII` restores the production behaviour. This matters on a corpus
    that includes DW, France24, SCMP and Haaretz.
    """
    assert classify_wire_item("Iraníes protest in the capital") == "geopolitics"


def test_word_boundaries_still_prevent_substring_matches():
    """ASCII mode must not become "substring match" — `ai` should not fire inside `said`,
    `chair`, `Dubai` or `campaign`."""
    assert classify_wire_item("Chairman said the campaign would continue in Dubai") == "general"
    assert classify_wire_item("AI startup raises funding") == "tech"


# ── Rule ordering, positively stated ─────────────────────────────────────────────────
@pytest.mark.parametrize(
    ("headline", "expected"),
    [
        ("Fed holds rates steady as inflation cools", "finance"),
        ("Ceasefire talks resume after missile strike", "geopolitics"),
        ("Premier League title race goes to the final day", "sports"),
        ("Netflix cancels its most-watched original", "entertainment"),
        ("Nvidia unveils next-generation chip", "tech"),
        ("NASA confirms water ice at the lunar south pole", "science"),
        ("Walmart recalls frozen berries over listeria fears", "consumer"),
        ("Man rescues cat from storm drain", "general"),
    ],
)
def test_each_rule_can_be_reached(headline, expected):
    assert classify_wire_item(headline) == expected


def test_earlier_rules_beat_later_ones_when_both_match():
    # "market" (finance, rule 1) vs "Netflix" (entertainment, rule 4)
    assert classify_wire_item("Netflix stock jumps as market rallies") == "finance"
    # "attack" (geopolitics, rule 2) vs "cybersecurity" (tech, rule 5)
    assert classify_wire_item("Cybersecurity firm reports ransomware attack") == "geopolitics"


# ── Total function ───────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "headline",
    ["", "   ", "!!!", "123", "a" * 500, "🇺🇦 breaking", "Ünïcödé tèst"],
)
def test_always_returns_a_valid_class(headline):
    assert classify_wire_item(headline) in TOPIC_CLASSES


def test_is_case_insensitive():
    assert classify_wire_item("NASDAQ CLIMBS") == classify_wire_item("nasdaq climbs") == "finance"
