"""Turn teacher labels into `mlx-lm` LoRA training data.

Writes `data/mlx/{train,valid,test}.jsonl` in chat format.

**The student sees the same prompt shape the teacher saw.** Same system prompt, same
`Outlet:/Headline:` user turn, from the same frozen `PROMPT_VERSION`. If the two differed,
the comparison would be measuring prompt engineering rather than distillation, and the whole
result would be uninterpretable.

The assistant turn is the bare class name rather than the teacher's `{"topic": ...}` JSON.
The teacher needed that envelope because constrained decoding required a schema; the student
is being taught to emit the answer directly, which is the point — it is one token instead of
a JSON object, and that is part of where the latency win comes from.

**Splits.** `train` and `valid` are carved out of the training pool only. `test` is the
held-out 500 and is written purely so the eval harness has a consistent input format — it is
never passed to the trainer. The 500 have never been trained on and never will be.

    uv run python -m src.prepare_training
    uv run python -m src.prepare_training --limit 20 --out data/mlx_smoke   # S5 probe
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import Counter
from pathlib import Path

from src.schema import UNPARSEABLE, is_valid_class
from src.store import DATA, read_jsonl, write_jsonl
from src.teacher import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt

VALID_FRACTION = 0.05
SEED = 20260814


def to_chat(example: dict, label: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(example["headline"], example["outlet"])},
            {"role": "assistant", "content": label},
        ]
    }


def join(examples_path: Path, labels_path: Path) -> list[tuple[dict, str]]:
    """Pair each example with its teacher label, dropping UNPARSEABLE rows loudly."""
    examples = {row["id"]: row for row in read_jsonl(examples_path)}
    paired, dropped = [], 0
    for row in read_jsonl(labels_path):
        label = row["label"]
        if label == UNPARSEABLE or not is_valid_class(label):
            dropped += 1
            continue
        example = examples.get(row["id"])
        if example is None:
            dropped += 1
            continue
        paired.append((example, label))
    if dropped:
        print(f"[prepare] dropped {dropped} rows from {labels_path.name} (unparseable or unmatched)")
    return paired


def main() -> int:
    parser = argparse.ArgumentParser(description="Build mlx-lm LoRA training data from teacher labels.")
    parser.add_argument("--out", type=Path, default=DATA / "mlx")
    parser.add_argument("--limit", type=int, default=0, help="cap the training pool (smoke runs)")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    train_pairs = join(DATA / "train_pool.jsonl", DATA / "train_labels.jsonl")
    test_pairs = join(DATA / "heldout.jsonl", DATA / "heldout_labels.jsonl")
    if not train_pairs:
        print("[prepare] no training labels — run src.teacher first", file=sys.stderr)
        return 1

    rng = random.Random(args.seed)
    train_pairs.sort(key=lambda pair: pair[0]["id"])  # deterministic regardless of file order
    rng.shuffle(train_pairs)
    if args.limit:
        train_pairs = train_pairs[: args.limit]

    n_valid = max(1, int(len(train_pairs) * VALID_FRACTION))
    valid_pairs, fit_pairs = train_pairs[:n_valid], train_pairs[n_valid:]

    args.out.mkdir(parents=True, exist_ok=True)
    written = {
        "train": write_jsonl(args.out / "train.jsonl", (to_chat(e, l) for e, l in fit_pairs)),
        "valid": write_jsonl(args.out / "valid.jsonl", (to_chat(e, l) for e, l in valid_pairs)),
        "test": write_jsonl(args.out / "test.jsonl", (to_chat(e, l) for e, l in test_pairs)),
    }

    # Leakage assertion. The held-out set must not appear in anything the trainer reads.
    fit_ids = {e["id"] for e, _ in fit_pairs} | {e["id"] for e, _ in valid_pairs}
    test_ids = {e["id"] for e, _ in test_pairs}
    assert not (fit_ids & test_ids), "LEAKAGE: a held-out example reached the training data"

    print(f"[prepare] prompt_version={PROMPT_VERSION}  seed={args.seed}  out={args.out}")
    for name, count in written.items():
        print(f"[prepare]   {name:<6} {count:>5}")
    print("[prepare] train label balance: " + " · ".join(
        f"{k}={v}" for k, v in sorted(Counter(l for _, l in fit_pairs).items())
    ))
    print(f"[prepare] leakage check: OK ({len(test_ids)} held-out ids absent from train+valid)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
