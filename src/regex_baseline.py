"""Arm 1: the incumbent.

A faithful Python port of `classifyWireItem()` from Sentinel's production backend:
  ~/Desktop/AI REPORTING APP MVP/supabase/functions/_shared/wire.ts:353

**Port the behaviour, not the intent.** This function has real bugs and they are the point
of the comparison — if we quietly fixed them the incumbent arm would be a strawman in the
opposite direction, flattering nothing and measuring nothing.

The bugs, all consequences of "first `if` that matches wins":

  1. `amazon` sits in the tech rule, which is checked before the consumer rule, so
     "Amazon Prime Day deals" is `tech`. The consumer rule's own `amazon prime` keyword is
     unreachable — dead code in production.
  2. `spacex` appears in BOTH the tech and science rules. Tech is checked first, so the
     science occurrence is dead code too.
  3. Country names (`china`, `russia`, `korea`, `israel`, `iran`, `taiwan`, `ukraine`) sit
     in the geopolitics rule, which is checked second. Any headline mentioning one is
     geopolitics regardless of subject — "China's Singles Day shopping festival" is
     geopolitics, not consumer.
  4. `target` in the consumer rule matches the verb "target", but the rule is last so it
     rarely gets the chance.
  5. Everything unmatched falls to `general`, so `general` is a catch-all rather than a
     class — which is why macro-F1 rather than accuracy is this project's headline metric.

ASCII semantics: JavaScript's `\\b` is defined over ASCII word characters. Python's `\\b` is
Unicode-aware by default, which would diverge on accented text — `\\biran\\b` matches
"Iraníes" in JS but not in default-mode Python. `re.ASCII` restores JS behaviour, and this
is a real difference on a corpus that includes DW, France24, SCMP and Haaretz.
"""

from __future__ import annotations

import re

# Rule order is load-bearing. Do not sort, do not deduplicate across rules.
_RULES: tuple[tuple[str, str], ...] = (
    (
        "finance",
        r"\b(stock|market|earnings|nasdaq|nyse|s&p|fed|inflation|gdp|crypto|bitcoin|ethereum|opec|oil price)\b",
    ),
    (
        "geopolitics",
        r"\b(war|military|missile|attack|strike|ceasefire|sanctions|nato|kremlin|gaza|ukraine|russia|israel|iran|hamas|hezbollah|china|taiwan|korea)\b",
    ),
    (
        "sports",
        r"\b(nfl|nba|mlb|nhl|fifa|f1|olympics|premier league|la liga|champions league|world cup|tennis|golf)\b",
    ),
    (
        "entertainment",
        r"\b(spotify|netflix|disney|hbo|movie|film|album|grammy|oscar|emmy|concert|tour)\b",
    ),
    (
        "tech",
        r"\b(ai|openai|anthropic|google|apple|microsoft|meta|amazon|tesla|nvidia|chip|semiconductor|cybersecurity|spacex)\b",
    ),
    (
        "science",
        r"\b(climate|nasa|spacex|vaccine|covid|disease|cancer|genome|mars|moon|space)\b",
    ),
    (
        "consumer",
        r"\b(walmart|costco|target|amazon prime|black friday|recall|fda)\b",
    ),
)

_COMPILED: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (label, re.compile(pattern, re.ASCII)) for label, pattern in _RULES
)


def classify_wire_item(headline: str) -> str:
    """Return one of TOPIC_CLASSES. Behaviourally identical to the production function."""
    lower = headline.lower()
    for label, pattern in _COMPILED:
        if pattern.search(lower):
            return label
    return "general"
