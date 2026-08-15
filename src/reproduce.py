"""One command that regenerates every result and chart the README cites.

S7's acceptance asks for exactly this: "one command regenerates all of it". Without it, the
numbers in the write-up are only as good as somebody's memory of which scripts ran in which
order — and this project already lost one training run's entire loss history to an assumption
about where a file lived.

    uv run python -m src.reproduce                 # everything downstream of training
    uv run python -m src.reproduce --skip-student  # no model load (safe while training runs)
    uv run python -m src.reproduce --dry-run       # print the pipeline, run nothing

What it does NOT do is train. Training is a 70-minute GPU job with its own failure modes and
its own artifacts; it is launched deliberately, not as a side effect of asking for a chart:

    uv run python -m mlx_lm lora -c configs/lora.yaml > runs/current/train.log 2>&1

Everything below that line is reproducible from committed inputs plus the adapter.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Order matters: the cost model reads token_counts.json, and both the error analysis and the
# confusion charts read predictions.jsonl, which only evaluate.py writes.
Step = tuple[str, list[str], str]


def pipeline(skip_student: bool) -> list[Step]:
    evaluate = ["-m", "src.evaluate"]
    # Evaluate the SELECTED checkpoint, not mlx-lm's final one.
    #
    # This is the difference between macro-F1 0.8400 and 0.7599. `evaluate.py` defaults to
    # `runs/current/adapters`, which holds the last iteration — and the last 200 iterations of
    # this run made the model measurably worse. Leaving the default in place would mean anyone
    # regenerating results silently overwrote the published headline with the worse number and
    # had no way to tell. `runs/current/best` is written by `src.select_checkpoint --materialise`.
    best = ROOT / "runs" / "current" / "best"
    if best.exists():
        evaluate += ["--adapter", str(best)]
    if skip_student:
        evaluate.append("--skip-student")
    return [
        (
            "token counts",
            ["-m", "src.measure_tokens"],
            "results/token_counts.json — the measured inputs the cost model reads",
        ),
        (
            "run record",
            ["-m", "src.record_run", "--allow-incomplete"],
            "runs/current/loss.jsonl + hyperparams.json — parsed from the real training log",
        ),
        (
            "checkpoint selection",
            ["-m", "src.select_checkpoint", "--materialise"],
            "runs/current/best/ — the best-validation checkpoint, chosen on the validation "
            "split alone (never the held-out 500)",
        ),
        (
            "training curve",
            ["-m", "src.chart_training"],
            "charts/training_curve.png",
        ),
        (
            "evaluation",
            evaluate,
            "results/summary.json + predictions.jsonl — three arms, quality, latency, cost",
        ),
        (
            "error analysis",
            ["-m", "src.error_analysis"],
            "results/error_analysis.{json,md} — taxonomy, head-to-head, breakdowns",
        ),
        (
            "confusion matrices",
            ["-m", "src.chart_confusion"],
            "charts/confusion_<arm>.png",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate every committed result and chart.")
    parser.add_argument("--skip-student", action="store_true",
                        help="skip the model load — safe to run while training holds the GPU")
    parser.add_argument("--dry-run", action="store_true", help="print the pipeline and exit")
    parser.add_argument("--keep-going", action="store_true",
                        help="continue after a failing step instead of stopping")
    args = parser.parse_args()

    steps = pipeline(args.skip_student)

    if args.dry_run:
        for name, argv, produces in steps:
            print(f"  {name:<20} python {' '.join(argv)}")
            print(f"  {'':<20} -> {produces}")
        return 0

    failures: list[str] = []
    for index, (name, argv, produces) in enumerate(steps, start=1):
        print(f"\n[{index}/{len(steps)}] {name} -> {produces}")
        result = subprocess.run([sys.executable, *argv], cwd=ROOT)
        if result.returncode != 0:
            failures.append(name)
            if not args.keep_going:
                print(f"\n[reproduce] FAILED at '{name}' (exit {result.returncode}). "
                      f"Pass --keep-going to run the rest anyway.", file=sys.stderr)
                return result.returncode

    print()
    if failures:
        # Reported as a failure, not summarised away. A pipeline that prints "done" after a
        # broken step is how an unbacked number reaches a README.
        print(f"[reproduce] completed with {len(failures)} failing step(s): {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"[reproduce] all {len(steps)} steps succeeded")
    if args.skip_student:
        print("[reproduce] NOTE: --skip-student was set, so summary.json carries "
              "student_evaluated=false and no student numbers are publishable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
