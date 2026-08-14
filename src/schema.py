"""Contracts. Frozen before a single label exists — the brief is explicit that this
ordering is not optional.

Everything downstream (harvest, teacher, train, evaluate) reads its shapes from here, so
the prompt and the label space cannot drift apart.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ── The label space ──────────────────────────────────────────────────────────────────
# Copied verbatim from Sentinel's production classifier:
#   ~/Desktop/AI REPORTING APP MVP/supabase/functions/_shared/wire.ts:350-380
# These strings are the contract with the product. Do not "improve" them, do not reorder
# them, do not add a ninth. If the product's set ever changes, that is an AMENDMENT in
# masterplan.md, not an edit here.
TOPIC_CLASSES: tuple[str, ...] = (
    "geopolitics",
    "finance",
    "tech",
    "sports",
    "entertainment",
    "science",
    "consumer",
    "general",
)

TopicClass = Literal[
    "geopolitics",
    "finance",
    "tech",
    "sports",
    "entertainment",
    "science",
    "consumer",
    "general",
]

# Sentinel used to mark a wire item to be classified by the teacher, whose output could not
# be parsed into one of the eight strings after a retry.
#
# It is NOT a ninth class. It is never written into training data and never counted as a
# prediction. It exists so the unparseable rate is reported rather than hidden — silently
# coercing these to `general` would bias the teacher toward the majority class and corrupt
# the very ceiling the whole project is measured against.
UNPARSEABLE = "UNPARSEABLE"

# One line per class, used to build the teacher prompt. Kept beside the class tuple so the
# prompt cannot drift from the label space. Written to describe the *product's* intent,
# inferred from the keyword sets the production regex uses for each class.
CLASS_DEFINITIONS: dict[str, str] = {
    "geopolitics": "war, military action, diplomacy, sanctions, elections and relations between states",
    "finance": "markets, stocks, earnings, central banks, inflation, commodities and crypto",
    "tech": "technology companies, software, AI, chips, cybersecurity and the tech industry",
    "sports": "professional and international sport, athletes, matches, leagues and tournaments",
    "entertainment": "film, television, music, celebrity, streaming and the arts",
    "science": "scientific research, space, climate, medicine, health and the environment",
    "consumer": "retail, consumer products, recalls, shopping, food and consumer safety",
    "general": "genuine general news that fits none of the above — crime, weather, human interest, local news",
}

assert set(CLASS_DEFINITIONS) == set(TOPIC_CLASSES), "class definitions drifted from the label space"

Split = Literal["train", "heldout"]
Arm = Literal["regex", "teacher", "student"]


# ── CONTRACT: Example ────────────────────────────────────────────────────────────────
class Example(BaseModel):
    """One harvested headline. Produced by src/harvest.py and src/gdelt.py."""

    id: str = Field(description="sha256(url)[:16] — stable, and the key disjointness is asserted on")
    headline: str
    outlet: str = Field(description="lowercase hostname without www., per extractOutlet() in wire.ts")
    url: str
    published_at: str | None = Field(default=None, description="ISO 8601 where the feed provided one")
    source: str = Field(description="the feed URL or 'gdelt'")
    split: Split


# ── CONTRACT: Label ──────────────────────────────────────────────────────────────────
class Label(BaseModel):
    """One teacher label. Produced by src/teacher.py.

    `label` may be UNPARSEABLE; consumers must filter, never coerce.
    """

    id: str
    label: str = Field(description="one of TOPIC_CLASSES, or UNPARSEABLE")
    teacher_model: str
    teacher_revision: str = Field(description="quant tag or revision SHA — a result from an unpinned model is not reproducible")
    prompt_version: str
    latency_ms: float
    raw_output: str = Field(description="kept so any parse decision can be re-audited")


# ── CONTRACT: Prediction ─────────────────────────────────────────────────────────────
class Prediction(BaseModel):
    """One arm's answer on one held-out example. The results JSONL row shape.

    `gold` is the teacher's label for that example. Calling it "gold" is a convenience:
    it is a model's opinion, not truth, and the S4 hand-audit measures how far apart those
    two things are. The README says so.
    """

    id: str
    arm: Arm
    pred: str
    gold: str
    latency_ms: float


def is_valid_class(value: str) -> bool:
    return value in TOPIC_CLASSES
