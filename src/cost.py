"""Cost arithmetic for the three arms.

**These are LIST-PRICE figures, not measured spend.** Every arm in this project ran locally
on one Mac and cost $0. Presenting a dollar number as though money changed hands would be
dishonest, so the label travels with the number everywhere it appears — in this module, in
`results/summary.json`, and in the README.

What *is* measured, and what makes the arithmetic real rather than asserted, is the token
count. The four figures come from `results/token_counts.json`, which `src/measure_tokens.py`
produces by rendering all 500 held-out headlines through the exact prompt builders each arm
used and tokenising them with the pinned Qwen3.5-4B tokeniser. This module reads that artifact
and refuses to run without it, so no hardcoded token count can drift back in.

## Prices

Fireworks publishes serverless rates by **parameter tier**, which is the rare case where a
price can be applied to a specific open model without guessing:

| tier | rate | source |
|---|---|---|
| under 4B parameters | **$0.10 / 1M tokens** | docs.fireworks.ai/serverless/pricing |
| MoE up to 56B parameters | **$0.50 / 1M tokens** | same |

Both are flat — the same rate for input and output — which removes the usual ambiguity about
input/output split. Our arms land in those tiers without interpretation:

- **student** — Qwen3.5-4B, 4.21B params. Sits at the boundary of the sub-4B tier; the
  cheaper tier is assumed and the sensitivity of that assumption is reported below.
- **teacher** — Qwen3.5-35B-A3B, a 35B MoE. Squarely inside "MoE up to 56B".

Cross-checked against Together's published list (Qwen3.5-9B at $0.17/$0.25, Qwen3.5-397B-A17B
at $0.60/$3.60): the Fireworks tiers sit sensibly between those points, so neither provider's
numbers look anomalous.

Prices retrieved 2026-08-15. They move; re-check before republishing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# $ per 1M tokens, flat across input and output.
RATE_SUB_4B = 0.10
RATE_MOE_56B = 0.50

TOKEN_COUNTS = Path(__file__).resolve().parent.parent / "results" / "token_counts.json"


def _measured() -> dict:
    """Load the token counts from the committed artifact `src/measure_tokens.py` produces.

    These used to be four hardcoded constants under a docstring claiming they were measured.
    They were not, and two were wrong in the direction that flattered the headline: the student
    input was set to 32 (A3's figure for a whole *training example*, a different quantity — it
    measures 35.98) and the teacher output to 10 (it measures 6.51, so teacher cost was
    overstated). Reading the artifact makes the docstring's claim true and means the number
    cannot drift from the tokeniser again.
    """
    if not TOKEN_COUNTS.exists():
        raise FileNotFoundError(
            f"{TOKEN_COUNTS} is missing — run `uv run python -m src.measure_tokens` first. "
            "The cost model refuses to fall back to hardcoded token counts."
        )
    return json.loads(TOKEN_COUNTS.read_text())["counts"]


_COUNTS = _measured()

# Means, because cost per 1,000 requests is a total and the mean is what totals.
TEACHER_INPUT_TOKENS = _COUNTS["teacher_input"]["mean"]
TEACHER_OUTPUT_TOKENS = _COUNTS["teacher_output"]["mean"]  # `{"topic": "..."}` envelope
STUDENT_INPUT_TOKENS = _COUNTS["student_input"]["mean"]
STUDENT_OUTPUT_TOKENS = _COUNTS["student_output"]["mean"]  # the bare class name

REQUESTS = 1000


@dataclass
class ArmCost:
    arm: str
    rate_per_m: float
    input_tokens: float
    output_tokens: float

    @property
    def tokens_per_request(self) -> float:
        return round(self.input_tokens + self.output_tokens, 2)

    @property
    def cost_per_request(self) -> float:
        return self.tokens_per_request * self.rate_per_m / 1_000_000

    @property
    def cost_per_1k(self) -> float:
        return self.cost_per_request * REQUESTS


TEACHER = ArmCost("teacher", RATE_MOE_56B, TEACHER_INPUT_TOKENS, TEACHER_OUTPUT_TOKENS)
STUDENT = ArmCost("student", RATE_SUB_4B, STUDENT_INPUT_TOKENS, STUDENT_OUTPUT_TOKENS)

# The regex is a pure function. No tokens, no model, no request. Zero is not a rounding.
REGEX_COST_PER_1K = 0.0


def breakdown() -> dict:
    """Every number the README cites about cost, with the arithmetic kept alongside."""
    ratio = STUDENT.cost_per_1k / TEACHER.cost_per_1k

    # What the student would cost if it had kept the teacher's full prompt — i.e. if
    # AMENDMENT A3 had not been made. Isolates how much of the win is the price tier and
    # how much is the token count.
    student_fat_prompt = ArmCost("student (full prompt)", RATE_SUB_4B, TEACHER_INPUT_TOKENS, STUDENT_OUTPUT_TOKENS)

    # Sensitivity: the student is 4.21B, just over the sub-4B tier boundary. If a provider
    # billed it at the next tier up instead, this is the result.
    student_next_tier = ArmCost("student (next tier up)", RATE_MOE_56B, STUDENT_INPUT_TOKENS, STUDENT_OUTPUT_TOKENS)

    return {
        "disclaimer": (
            "LIST-PRICE ARITHMETIC, NOT MEASURED SPEND. Every arm in this project ran locally "
            "and cost $0. Token counts are measured with the real tokeniser; prices are "
            "published serverless rates (Fireworks, retrieved 2026-08-15)."
        ),
        "rates_per_1m_tokens": {"under_4B": RATE_SUB_4B, "moe_up_to_56B": RATE_MOE_56B},
        "arms": {
            "regex": {
                "tokens_per_request": 0,
                "cost_per_1k_requests": REGEX_COST_PER_1K,
                "note": "a pure function — no model, no tokens, no request",
            },
            "teacher": {
                "rate_per_1m": TEACHER.rate_per_m,
                "input_tokens": TEACHER.input_tokens,
                "output_tokens": TEACHER.output_tokens,
                "tokens_per_request": TEACHER.tokens_per_request,
                "cost_per_1k_requests": round(TEACHER.cost_per_1k, 6),
                "arithmetic": (
                    f"({TEACHER.input_tokens} in + {TEACHER.output_tokens} out) x {REQUESTS} req "
                    f"= {TEACHER.tokens_per_request * REQUESTS:,} tokens "
                    f"x ${TEACHER.rate_per_m}/1M = ${TEACHER.cost_per_1k:.4f}"
                ),
            },
            "student": {
                "rate_per_1m": STUDENT.rate_per_m,
                "input_tokens": STUDENT.input_tokens,
                "output_tokens": STUDENT.output_tokens,
                "tokens_per_request": STUDENT.tokens_per_request,
                "cost_per_1k_requests": round(STUDENT.cost_per_1k, 6),
                "arithmetic": (
                    f"({STUDENT.input_tokens} in + {STUDENT.output_tokens} out) x {REQUESTS} req "
                    f"= {STUDENT.tokens_per_request * REQUESTS:,} tokens "
                    f"x ${STUDENT.rate_per_m}/1M = ${STUDENT.cost_per_1k:.4f}"
                ),
            },
        },
        "headline": {
            "student_as_fraction_of_teacher": round(ratio, 4),
            "student_cheaper_by": round(1 / ratio, 1),
            "decomposition": {
                "price_tier_factor": round(TEACHER.rate_per_m / STUDENT.rate_per_m, 2),
                "token_count_factor": round(TEACHER.tokens_per_request / STUDENT.tokens_per_request, 2),
                "note": "the two multiply; neither alone produces the headline",
            },
        },
        "sensitivity": {
            "if_student_kept_the_full_prompt": {
                "cost_per_1k_requests": round(student_fat_prompt.cost_per_1k, 6),
                "student_cheaper_by": round(TEACHER.cost_per_1k / student_fat_prompt.cost_per_1k, 1),
                "note": "what the S5 decision would have cost, before AMENDMENT A3 reversed it",
            },
            "if_student_billed_at_the_next_tier_up": {
                "cost_per_1k_requests": round(student_next_tier.cost_per_1k, 6),
                "student_cheaper_by": round(TEACHER.cost_per_1k / student_next_tier.cost_per_1k, 1),
                "note": "Qwen3.5-4B is 4.21B params, just over the sub-4B boundary — this is the pessimistic read",
            },
        },
    }


def main() -> None:
    data = breakdown()
    print(data["disclaimer"])
    print()
    for arm in ("regex", "teacher", "student"):
        entry = data["arms"][arm]
        print(f"{arm:<9} ${entry['cost_per_1k_requests']:.4f} / 1k requests")
        if "arithmetic" in entry:
            print(f"          {entry['arithmetic']}")
    head = data["headline"]
    print()
    print(f"student is {head['student_as_fraction_of_teacher']:.2%} of teacher cost "
          f"({head['student_cheaper_by']}x cheaper)")
    print(f"  = {head['decomposition']['price_tier_factor']}x price tier "
          f"x {head['decomposition']['token_count_factor']}x fewer tokens")
    print()
    for name, entry in data["sensitivity"].items():
        print(f"  sensitivity · {name}: {entry['student_cheaper_by']}x cheaper")
    print()
    print(json.dumps(data, indent=2)[:0])  # keep json import meaningful for callers


if __name__ == "__main__":
    main()
