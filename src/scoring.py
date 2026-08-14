"""Scoring. Frozen before any label exists.

Implemented from first principles rather than pulling in scikit-learn: it is ~60 lines of
arithmetic, it keeps the dependency surface honest, and — the real reason — the averaging
convention below is a choice with consequences, and it should be visible in this repo
rather than inherited from a library default.

**Macro-F1 is averaged over all eight classes in TOPIC_CLASSES**, not over the classes that
happen to appear in the data. A class the model never predicts and never gets right scores
0.0 and drags the mean down. That is deliberate: a distilled small model failing to learn a
tail class entirely is exactly the failure this project exists to surface, and averaging it
away would hide it. (scikit-learn's default averages over labels present in y_true ∪ y_pred,
which would quietly forgive that.)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.schema import TOPIC_CLASSES


@dataclass
class ClassScore:
    label: str
    precision: float
    recall: float
    f1: float
    support: int  # count in y_true


@dataclass
class Scores:
    accuracy: float
    macro_f1: float
    per_class: list[ClassScore]
    confusion: dict[str, dict[str, int]] = field(default_factory=dict)
    n: int = 0

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "accuracy": round(self.accuracy, 4),
            "macro_f1": round(self.macro_f1, 4),
            "per_class": [
                {
                    "label": c.label,
                    "precision": round(c.precision, 4),
                    "recall": round(c.recall, 4),
                    "f1": round(c.f1, 4),
                    "support": c.support,
                }
                for c in self.per_class
            ],
            "confusion": self.confusion,
        }


def _safe_div(numerator: float, denominator: float) -> float:
    """0.0 rather than NaN when a class is never predicted or never occurs.

    This is the convention that makes a never-predicted class score 0.0 instead of
    vanishing from the average. See the module docstring.
    """
    return numerator / denominator if denominator else 0.0


def score(y_true: list[str], y_pred: list[str]) -> Scores:
    if len(y_true) != len(y_pred):
        raise ValueError(f"length mismatch: {len(y_true)} true vs {len(y_pred)} pred")
    if not y_true:
        raise ValueError("cannot score an empty set")

    unknown = ({*y_true} | {*y_pred}) - {*TOPIC_CLASSES}
    if unknown:
        # UNPARSEABLE must be filtered by the caller, not silently averaged in here.
        raise ValueError(f"values outside TOPIC_CLASSES reached the scorer: {sorted(unknown)}")

    confusion = {t: {p: 0 for p in TOPIC_CLASSES} for t in TOPIC_CLASSES}
    for t, p in zip(y_true, y_pred, strict=True):
        confusion[t][p] += 1

    per_class: list[ClassScore] = []
    for label in TOPIC_CLASSES:
        tp = confusion[label][label]
        fn = sum(confusion[label][p] for p in TOPIC_CLASSES) - tp
        fp = sum(confusion[t][label] for t in TOPIC_CLASSES) - tp
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        per_class.append(
            ClassScore(label=label, precision=precision, recall=recall, f1=f1, support=tp + fn)
        )

    correct = sum(confusion[c][c] for c in TOPIC_CLASSES)
    return Scores(
        accuracy=correct / len(y_true),
        macro_f1=sum(c.f1 for c in per_class) / len(TOPIC_CLASSES),
        per_class=per_class,
        confusion=confusion,
        n=len(y_true),
    )


def percentile(values: list[float], q: float) -> float:
    """Nearest-rank percentile. q in [0, 100].

    Deliberately nearest-rank rather than interpolated: a p95 latency should be a latency
    that was actually observed, not an average of two that weren't.
    """
    if not values:
        raise ValueError("cannot take a percentile of an empty list")
    ordered = sorted(values)
    rank = max(1, min(len(ordered), math.ceil(q / 100 * len(ordered))))
    return ordered[rank - 1]


def confusion_pairs(scores: Scores, top: int = 5) -> list[tuple[str, str, int]]:
    """The most-confused (true, predicted) pairs, excluding the diagonal.

    Feeds the S7 error taxonomy — "it confuses tech and science on space-launch headlines"
    is worth more than any aggregate number.
    """
    pairs = [
        (t, p, n)
        for t, row in scores.confusion.items()
        for p, n in row.items()
        if t != p and n > 0
    ]
    return sorted(pairs, key=lambda x: -x[2])[:top]
