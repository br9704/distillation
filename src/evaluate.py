"""S7: one harness, three arms, the same 500 held-out headlines, the same machine.

    uv run python -m src.evaluate --adapter runs/current/adapters

**Gold is the teacher's own label, so the teacher arm is not scored for quality here.**
Scoring it against its own output would return 100% by construction and mean nothing. The
teacher's estimated true accuracy is the **84%** from the S4 hand audit
(`results/audit_50.md`), and that number — not a constructed 100% — is what the README
reports. Everything the student and regex score is therefore *agreement with the teacher*,
not correctness, and the write-up says so in those words.

**Latency.** Student latency is measured here: sequential, one request at a time, warm-up
discarded. Teacher latency was measured identically in S4 (`data/teacher_latency.jsonl`)
before the 22 GB of weights were deleted. The regex is timed the same way, which is faintly
absurd for a function call and is done anyway so all three numbers come from one harness.

**`enable_thinking=False` is mandatory** — see S5. Qwen3.5-4B's chat template opens a
`<think>` block by default; training data carries a closed one. Without the flag the student
emits reasoning instead of a class and scores near zero for reasons that have nothing to do
with the fine-tune.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from src.prepare_training import student_messages
from src.regex_baseline import classify_wire_item
from src.schema import TOPIC_CLASSES, UNPARSEABLE
from src.scoring import confusion_pairs, percentile, score
from src.store import DATA, read_jsonl, write_jsonl

RESULTS = Path(__file__).resolve().parent.parent / "results"
WARMUP = 3


def load_heldout() -> list[dict]:
    examples = {row["id"]: row for row in read_jsonl(DATA / "heldout.jsonl")}
    rows = []
    for label_row in read_jsonl(DATA / "heldout_labels.jsonl"):
        if label_row["label"] == UNPARSEABLE:
            continue
        example = examples.get(label_row["id"])
        if example:
            rows.append({**example, "gold": label_row["label"]})
    return rows


def run_regex(rows: list[dict]) -> list[dict]:
    predictions = []
    for row in rows:
        started = time.perf_counter()
        pred = classify_wire_item(row["headline"])
        elapsed = (time.perf_counter() - started) * 1000
        predictions.append({"id": row["id"], "arm": "regex", "pred": pred, "gold": row["gold"], "latency_ms": elapsed})
    return predictions


def run_student(rows: list[dict], model_path: str, adapter: str | None) -> list[dict]:
    from mlx_lm import generate, load

    model, tokenizer = load(model_path, adapter_path=adapter)

    def predict(row: dict) -> tuple[str, float]:
        prompt = tokenizer.apply_chat_template(
            student_messages(row), add_generation_prompt=True, enable_thinking=False
        )
        started = time.perf_counter()
        out = generate(model, tokenizer, prompt=prompt, max_tokens=6, verbose=False)
        elapsed = (time.perf_counter() - started) * 1000
        answer = out.strip().split()[0].strip(".\"'`") if out.strip() else ""
        return (answer if answer in TOPIC_CLASSES else UNPARSEABLE), elapsed

    print(f"[eval] student warm-up ({WARMUP} discarded calls)")
    for row in rows[:WARMUP]:
        predict(row)

    predictions = []
    for index, row in enumerate(rows, start=1):
        pred, elapsed = predict(row)
        predictions.append({"id": row["id"], "arm": "student", "pred": pred, "gold": row["gold"], "latency_ms": elapsed})
        if index % 100 == 0:
            print(f"[eval] student {index}/{len(rows)}")
    return predictions


def teacher_latencies() -> list[float]:
    """From the S4 run, measured identically before the weights were deleted."""
    return [row["latency_ms"] for row in read_jsonl(DATA / "teacher_latency.jsonl")]


def summarise(arm: str, predictions: list[dict], latencies: list[float] | None = None) -> dict:
    usable = [p for p in predictions if p["pred"] != UNPARSEABLE]
    invalid = len(predictions) - len(usable)
    scores = score([p["gold"] for p in usable], [p["pred"] for p in usable])
    values = latencies if latencies is not None else [p["latency_ms"] for p in predictions]
    return {
        "arm": arm,
        "n": len(predictions),
        "invalid_outputs": invalid,
        **scores.as_dict(),
        "latency_ms": {
            "p50": round(percentile(values, 50), 2),
            "p95": round(percentile(values, 95), 2),
            "mean": round(sum(values) / len(values), 2),
        },
        "top_confusions": [
            {"gold": g, "pred": p, "n": n} for g, p, n in confusion_pairs(scores, top=5)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate all three arms on the held-out 500.")
    parser.add_argument("--adapter", default="runs/current/adapters")
    parser.add_argument("--model", default="mlx-community/Qwen3.5-4B-bf16")
    parser.add_argument("--skip-student", action="store_true")
    args = parser.parse_args()

    rows = load_heldout()
    print(f"[eval] {len(rows)} held-out examples")

    predictions = run_regex(rows)
    summaries = [summarise("regex", predictions)]
    all_predictions = list(predictions)

    if not args.skip_student:
        student = run_student(rows, args.model, args.adapter)
        all_predictions += student
        summaries.append(summarise("student", student))

    # Teacher: quality is not scored against its own labels (see the module docstring).
    # Only latency is reported here, from the S4 measurement.
    teacher_ms = teacher_latencies()
    summaries.append(
        {
            "arm": "teacher",
            "n": len(teacher_ms),
            "note": (
                "Quality is NOT scored against gold — gold IS this model's output, so any such "
                "figure would be 100% by construction. The teacher's estimated true accuracy is "
                "the 84% hand-audit agreement in results/audit_50.md."
            ),
            "hand_audit_agreement": 0.84,
            "hand_audit_agreement_excluding_ambiguous": 0.93,
            "latency_ms": {
                "p50": round(percentile(teacher_ms, 50), 2),
                "p95": round(percentile(teacher_ms, 95), 2),
                "mean": round(sum(teacher_ms) / len(teacher_ms), 2),
            },
        }
    )

    RESULTS.mkdir(parents=True, exist_ok=True)
    write_jsonl(RESULTS / "predictions.jsonl", all_predictions)
    (RESULTS / "summary.json").write_text(json.dumps({"arms": summaries}, indent=2) + "\n")

    print()
    print(f"{'arm':<10}{'macro-F1':>10}{'accuracy':>10}{'p50 ms':>10}{'p95 ms':>10}{'invalid':>9}")
    for s in summaries:
        if "macro_f1" in s:
            print(
                f"{s['arm']:<10}{s['macro_f1']:>10.4f}{s['accuracy']:>10.4f}"
                f"{s['latency_ms']['p50']:>10.1f}{s['latency_ms']['p95']:>10.1f}{s['invalid_outputs']:>9}"
            )
        else:
            print(
                f"{s['arm']:<10}{'n/a':>10}{'n/a':>10}"
                f"{s['latency_ms']['p50']:>10.1f}{s['latency_ms']['p95']:>10.1f}{'—':>9}"
            )
    print("\n[eval] teacher quality is n/a by construction — see results/summary.json")
    print(f"[eval] wrote {RESULTS / 'summary.json'} and {RESULTS / 'predictions.jsonl'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
