"""Measure the token counts the cost model depends on. No estimates, no round numbers.

`src/cost.py` used to hardcode its four token constants while its own docstring claimed they
were "measured with the real tokeniser on the real rendered prompts". They were not, and one
of them was wrong: the student input was set to 32, which is AMENDMENT A3's figure for a whole
*training example*, a different quantity from a *request's input*. This module makes the claim
true by producing the numbers as a committed artifact that `cost.py` then reads.

**What is measured.** Every held-out headline, rendered through the exact prompt builders the
two arms actually used, tokenised with the pinned Qwen3.5-4B tokeniser:

- teacher input  — `SYSTEM_PROMPT` + `Outlet:/Headline:` user turn, chat-templated
- teacher output — the constrained-decoding envelope, `{"topic": "<class>"}`
- student input  — `student_messages()` alone (A3's lean shape), chat-templated with
                   `enable_thinking=False`, which is the shape the student is actually served
- student output — the bare class name

The tokeniser is the student's. The teacher (Qwen3.5-35B-A3B) shares the Qwen tokeniser family,
and its own weights were deleted in S4, so this is the closest honest measurement available —
and it is stated as such in the artifact rather than glossed.

The mean is reported alongside the median, the min and the max, because a single headline's
token count is not a constant and the cost table should not pretend it is. `cost.py` uses the
**mean**, since cost per 1,000 requests is a total and the mean is what totals.

Loads a tokeniser only — no model weights, no GPU. Safe to run during training.

    uv run python -m src.measure_tokens
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from src.prepare_training import student_messages
from src.store import DATA, read_jsonl
from src.teacher import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

MODEL = "mlx-community/Qwen3.5-4B-bf16"
REVISION = "491fdc7c087ba7fb48adcb1253f8e76d011db783"


def _stats(counts: list[int]) -> dict:
    return {
        "n": len(counts),
        "mean": round(statistics.mean(counts), 2),
        "median": statistics.median(counts),
        "min": min(counts),
        "max": max(counts),
        "stdev": round(statistics.pstdev(counts), 2) if len(counts) > 1 else 0.0,
    }


def measure(rows: list[dict], tokenizer) -> dict:
    """Tokenise both arms' real rendered prompts over every row."""

    def n_tokens(text: str) -> int:
        return len(tokenizer.encode(text, add_special_tokens=False))

    def n_chat(messages: list[dict]) -> int:
        rendered = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False, enable_thinking=False
        )
        return n_tokens(rendered)

    teacher_in, student_in, teacher_out, student_out = [], [], [], []
    for row in rows:
        headline, outlet = row["headline"], row["outlet"]
        user = build_user_prompt(headline, outlet)
        teacher_in.append(
            n_chat([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}])
        )
        student_in.append(n_chat(student_messages(row)))

    # Outputs vary only by which class is emitted — but the classes are not equally likely, so
    # counting each class once would mis-weight the average. Weight by the actual gold label of
    # each held-out row instead. Falls back to one-per-class only if labels are unavailable.
    from src.schema import TOPIC_CLASSES

    labels = {row["id"]: row["label"] for row in read_jsonl(DATA / "heldout_labels.jsonl")}
    emitted = [labels[row["id"]] for row in rows if labels.get(row["id"]) in TOPIC_CLASSES]
    if not emitted:
        emitted = list(TOPIC_CLASSES)
    for topic in emitted:
        teacher_out.append(n_tokens(json.dumps({"topic": topic})))
        student_out.append(n_tokens(topic))

    return {
        "teacher_input": _stats(teacher_in),
        "teacher_output": _stats(teacher_out),
        "student_input": _stats(student_in),
        "student_output": _stats(student_out),
        "system_prompt_alone": n_tokens(SYSTEM_PROMPT),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure real token counts for the cost model.")
    parser.add_argument("--input", type=Path, default=DATA / "heldout.jsonl")
    parser.add_argument("--out", type=Path, default=RESULTS / "token_counts.json")
    args = parser.parse_args()

    rows = list(read_jsonl(args.input))
    if not rows:
        print(f"[tokens] no rows in {args.input}", file=sys.stderr)
        return 1

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    measured = measure(rows, tokenizer)

    payload = {
        "note": (
            "Measured, not estimated. Every held-out headline rendered through the exact prompt "
            "builders each arm used, tokenised with the pinned Qwen3.5-4B tokeniser. cost.py "
            "reads the MEAN of each field, because cost per 1,000 requests is a total."
        ),
        "caveat": (
            "The teacher (Qwen3.5-35B-A3B) shares the Qwen tokeniser family but its weights were "
            "deleted in S4, so teacher counts are measured with the student's tokeniser. Stated "
            "rather than glossed."
        ),
        "tokenizer": {"model": MODEL, "revision": REVISION},
        "source": str(args.input.relative_to(ROOT)),
        "prompt_version": PROMPT_VERSION,
        "counts": measured,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")

    c = measured
    print(f"[tokens] {len(rows)} headlines · tokeniser {MODEL} @ {REVISION[:8]}")
    print(f"[tokens] system prompt alone      {c['system_prompt_alone']:>7}")
    for name in ("teacher_input", "student_input", "teacher_output", "student_output"):
        s = c[name]
        print(f"[tokens] {name:<22} mean {s['mean']:>7}  median {s['median']:>5}  "
              f"min {s['min']:>4}  max {s['max']:>5}")
    ratio = c["teacher_input"]["mean"] / c["student_input"]["mean"]
    print(f"[tokens] input reduction: {ratio:.2f}x")
    print(f"[tokens] wrote {args.out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
