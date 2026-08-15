"""Fuse the LoRA adapter into standalone weights, then prove the result actually works.

Two S6 acceptance clauses live here: "merge adapter -> `models/student-merged/`" and
"20 sanity predictions parse to valid classes".

The sanity check is not decoration. The S5 probe caught a silent failure that looked exactly
like a failed fine-tune — `enable_thinking=False` was missing, the model emitted
"Thinking Process:" instead of a class, and 0 of 5 predictions parsed. The obvious conclusion
would have been wrong. So the merged model is asked for real predictions before anything
downstream trusts it, and the check runs against the **merged** weights rather than the
adapter, because the merge is the step that could silently produce a valid-but-wrong model.

`models/` is gitignored — 8 GB of weights never enter the repo. What is committed is
`results/sanity_20.json`, which records what the merged model said and whether it parsed.

    uv run python -m src.merge_student                 # fuse, then sanity-check
    uv run python -m src.merge_student --sanity-only   # check an existing merge
    uv run python -m src.merge_student --skip-merge --adapter runs/current/adapters
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

from src.prepare_training import student_messages
from src.schema import TOPIC_CLASSES, UNPARSEABLE
from src.store import DATA, read_jsonl

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CONFIG = ROOT / "configs" / "lora.yaml"
MERGED = ROOT / "models" / "student-merged"

SANITY_N = 20


HF_CACHE = Path.home() / ".cache" / "huggingface" / "hub"


def resolve_local(model: str, revision: str | None) -> str:
    """Prefer the on-disk snapshot directory over the bare repo id.

    `mlx_lm.load()` and `mlx_lm fuse` resolve models differently: fuse goes through
    `snapshot_download(local_files_only=True)`, which raises `IncompleteSnapshotError` if any
    file recorded in the repo is absent from the cache — including `.gitattributes`, which
    carries no weights and which the original download skipped. The model itself is complete.

    Rather than reach for the network to fetch a metadata file, point fuse at the snapshot
    directory. It is named by the revision SHA, so this keeps the pin rather than weakening it:
    the path itself is the provenance.
    """
    if Path(model).exists() or revision is None:
        return model
    cached = HF_CACHE / f"models--{model.replace('/', '--')}" / "snapshots" / revision
    if (cached / "config.json").exists():
        return str(cached)
    return model


def fuse(model: str, adapter: Path, out: Path) -> int:
    """Call mlx-lm's own fuse rather than reimplementing the merge.

    A hand-rolled merge that is subtly wrong would produce a model that loads, generates, and
    is quietly not the model that was trained. Using the library's own path removes that class
    of error entirely.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    argv = [
        sys.executable, "-m", "mlx_lm", "fuse",
        "--model", model,
        "--adapter-path", str(adapter),
        "--save-path", str(out),
    ]
    print(f"[merge] {' '.join(argv)}")
    return subprocess.run(argv, cwd=ROOT).returncode


def sanity(model_path: str, rows: list[dict], adapter: str | None = None) -> dict:
    """Ask for SANITY_N real predictions and record every one, parsed or not."""
    from mlx_lm import generate, load

    model, tokenizer = load(model_path, adapter_path=adapter)

    results, correct, valid = [], 0, 0
    for row in rows:
        prompt = tokenizer.apply_chat_template(
            student_messages(row), add_generation_prompt=True, enable_thinking=False
        )
        started = time.perf_counter()
        raw = generate(model, tokenizer, prompt=prompt, max_tokens=6, verbose=False)
        elapsed = (time.perf_counter() - started) * 1000

        answer = raw.strip().split()[0].strip(".\"'`") if raw.strip() else ""
        parsed = answer if answer in TOPIC_CLASSES else UNPARSEABLE
        is_valid = parsed != UNPARSEABLE
        is_correct = parsed == row["gold"]
        valid += is_valid
        correct += is_correct
        results.append(
            {
                "id": row["id"],
                "headline": row["headline"],
                "outlet": row["outlet"],
                "gold": row["gold"],
                # The raw string is kept so any parse decision can be re-audited later —
                # the same rule S3 applied to the teacher's output.
                "raw_output": raw.strip(),
                "parsed": parsed,
                "valid": is_valid,
                "agrees_with_teacher": is_correct,
                "latency_ms": round(elapsed, 2),
            }
        )

    return {
        "n": len(results),
        "valid": valid,
        "invalid": len(results) - valid,
        "agrees_with_teacher": correct,
        "note": (
            "Gold is the teacher's label, so `agrees_with_teacher` is agreement, not accuracy. "
            "The acceptance criterion is that predictions PARSE to valid classes; agreement is "
            "reported alongside because a model that parses perfectly and answers randomly "
            "would otherwise pass."
        ),
        "predictions": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fuse the adapter and sanity-check the merged model.")
    parser.add_argument("--adapter", type=Path, default=ROOT / "runs" / "current" / "adapters")
    parser.add_argument("--model", default=None, help="defaults to the model in configs/lora.yaml")
    parser.add_argument("--out", type=Path, default=MERGED)
    parser.add_argument("--n", type=int, default=SANITY_N)
    parser.add_argument("--skip-merge", action="store_true", help="sanity-check the adapter instead")
    parser.add_argument("--sanity-only", action="store_true", help="skip the fuse, check the existing merge")
    args = parser.parse_args()

    config = yaml.safe_load(CONFIG.read_text()) if CONFIG.exists() else {}
    model = args.model or config.get("model", "mlx-community/Qwen3.5-4B-bf16")
    model = resolve_local(model, config.get("revision"))

    if not args.adapter.exists():
        print(f"[merge] no adapter at {args.adapter}", file=sys.stderr)
        return 1

    if not (args.skip_merge or args.sanity_only):
        code = fuse(model, args.adapter, args.out)
        if code != 0:
            print(f"[merge] fuse failed (exit {code})", file=sys.stderr)
            return code
        print(f"[merge] fused -> {args.out}")

    # Sanity-check the merged weights when they exist, because the merge is the step that could
    # silently change behaviour. Fall back to base+adapter only if there is no merge to test.
    if args.skip_merge or not args.out.exists():
        target, adapter_arg, what = model, str(args.adapter), "base + adapter"
    else:
        target, adapter_arg, what = str(args.out), None, "merged weights"

    examples = {row["id"]: row for row in read_jsonl(DATA / "heldout.jsonl")}
    rows = []
    for label_row in read_jsonl(DATA / "heldout_labels.jsonl"):
        if label_row["label"] == UNPARSEABLE:
            continue
        example = examples.get(label_row["id"])
        if example:
            rows.append({**example, "gold": label_row["label"]})
        if len(rows) >= args.n:
            break

    print(f"[merge] sanity-checking {what}: {len(rows)} predictions")
    report = sanity(target, rows, adapter_arg)
    report["checked"] = what
    report["model"] = target
    report["adapter"] = adapter_arg
    report["base_model_revision"] = config.get("revision")

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "sanity_20.json").write_text(json.dumps(report, indent=2) + "\n")

    print(f"[merge] {report['valid']}/{report['n']} parsed to valid classes · "
          f"{report['agrees_with_teacher']}/{report['n']} agree with the teacher")
    for r in report["predictions"][:5]:
        mark = "ok " if r["valid"] else "BAD"
        print(f"[merge]   {mark} {r['parsed']:<14} gold {r['gold']:<14} {r['headline'][:58]}")
    print(f"[merge] wrote {(RESULTS / 'sanity_20.json').relative_to(ROOT)}")

    if report["invalid"]:
        # A failing acceptance criterion must exit non-zero. Printing it and returning 0 is how
        # a broken model reaches a README.
        print(f"[merge] ACCEPTANCE FAILED: {report['invalid']} prediction(s) did not parse",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
