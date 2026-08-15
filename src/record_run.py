"""Turn an `mlx-lm` training log into the two artifacts S6 has to commit.

`mlx-lm` reports to stdout and writes nothing a reviewer can audit later. This module is the
missing producer for both files the masterplan requires and `.gitignore` deliberately
un-ignores:

- `runs/<id>/loss.jsonl`      — one record per reported step, train and val
- `runs/<id>/hyperparams.json` — every hyperparameter, the pinned base-model revision, the
                                 dataset hashes, the prompt version, and the tool versions

The point of the second file is the CLAUDE.md rule that a result produced from an unpinned
model is not reproducible and does not count. A reviewer holding `hyperparams.json` can tell
exactly which weights, which data, and which library versions produced the adapter — without
trusting a commit message.

**The log is parsed rather than the trainer being instrumented.** A wrapper that re-implements
mlx-lm's reporting could drift from the code path actually taken; the log is what the run
actually emitted. `nan` is preserved as `None` rather than dropped, because a silently
discarded nan window is exactly the kind of gap that makes a loss curve a lie.

    uv run python -m src.record_run                       # runs/current, after training
    uv run python -m src.record_run --run runs/current --log runs/current/train.log
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# `Iter 25: Train loss 0.454, Learning Rate 1.000e-05, It/sec 0.269, Tokens/sec 13.200,
#  Trained Tokens 1288, Peak mem 31.778 GB`
# `Iter 100: Val loss 0.084, Val took 14.203s`
#
# Not anchored to line start on purpose: mlx-lm's tqdm progress bars use carriage returns, so
# a real `Iter` report frequently shares a physical line with a progress bar.
TRAIN_RE = re.compile(
    r"Iter (\d+): Train loss (nan|-?[\d.]+)"
    r"(?:, Learning Rate ([\d.eE+-]+))?"
    r"(?:, It/sec ([\d.]+))?"
    r"(?:, Tokens/sec ([\d.]+))?"
    r"(?:, Trained Tokens (\d+))?"
    r"(?:, Peak mem ([\d.]+) GB)?"
)
VAL_RE = re.compile(r"Iter (\d+): Val loss (nan|-?[\d.]+)(?:, Val took ([\d.]+)s)?")
TRAINABLE_RE = re.compile(r"Trainable parameters: ([\d.]+)% \(([\d.]+)M/([\d.]+)M\)")
FINAL_RE = re.compile(r"Saved final weights to (.+)")


def _num(raw: str | None) -> float | None:
    """`nan` becomes None so it survives JSON round-tripping as an explicit gap."""
    if raw is None:
        return None
    if raw.lower() == "nan":
        return None
    return float(raw)


def parse_log(text: str) -> tuple[list[dict], dict]:
    """Return (per-step records, run-level facts) from raw mlx-lm stdout."""
    records: list[dict] = []
    for m in TRAIN_RE.finditer(text):
        records.append(
            {
                "iter": int(m.group(1)),
                "split": "train",
                "loss": _num(m.group(2)),
                "learning_rate": _num(m.group(3)),
                "it_per_sec": _num(m.group(4)),
                "tokens_per_sec": _num(m.group(5)),
                "trained_tokens": int(m.group(6)) if m.group(6) else None,
                "peak_mem_gb": _num(m.group(7)),
            }
        )
    for m in VAL_RE.finditer(text):
        records.append(
            {
                "iter": int(m.group(1)),
                "split": "valid",
                "loss": _num(m.group(2)),
                "val_took_s": _num(m.group(3)),
            }
        )
    records.sort(key=lambda r: (r["iter"], r["split"]))

    trainable = TRAINABLE_RE.search(text)
    final = FINAL_RE.search(text)
    train_only = [r for r in records if r["split"] == "train"]
    nan_iters = [r["iter"] for r in records if r["loss"] is None]

    facts = {
        "reported_steps": len(train_only),
        "val_evaluations": len(records) - len(train_only),
        "nan_report_windows": len(nan_iters),
        "nan_at_iters": nan_iters,
        "completed": final is not None,
        "final_weights": final.group(1).strip() if final else None,
        "last_iter": max((r["iter"] for r in records), default=0),
        "peak_mem_gb": max((r.get("peak_mem_gb") or 0 for r in train_only), default=None) or None,
        "trained_tokens": max((r.get("trained_tokens") or 0 for r in train_only), default=None) or None,
    }
    if trainable:
        facts["trainable_parameters"] = {
            "percent": float(trainable.group(1)),
            "trainable_millions": float(trainable.group(2)),
            "total_millions": float(trainable.group(3)),
        }
    speeds = [r["it_per_sec"] for r in train_only if r["it_per_sec"]]
    if speeds:
        facts["median_it_per_sec"] = round(sorted(speeds)[len(speeds) // 2], 4)
        facts["wall_clock_estimate_s"] = round(facts["last_iter"] / facts["median_it_per_sec"], 1)

    losses = [r["loss"] for r in train_only if r["loss"] is not None]
    if losses:
        facts["first_train_loss"] = losses[0]
        facts["final_train_loss"] = losses[-1]
        facts["min_train_loss"] = min(losses)
        facts["loss_decreased"] = losses[-1] < losses[0]
    val_losses = [r["loss"] for r in records if r["split"] == "valid" and r["loss"] is not None]
    if val_losses:
        facts["first_val_loss"] = val_losses[0]
        facts["final_val_loss"] = val_losses[-1]
        facts["min_val_loss"] = min(val_losses)
    return records, facts


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_fingerprint(data_dir: Path) -> dict:
    """Hash and count every split the trainer read. Renaming a file cannot hide a swap."""
    out = {}
    for name in ("train", "valid", "test"):
        path = data_dir / f"{name}.jsonl"
        if not path.exists():
            continue
        out[name] = {
            "path": str(path.relative_to(ROOT)),
            "rows": sum(1 for _ in path.open()),
            "sha256": sha256(path),
        }
    return out


def versions() -> dict:
    out = {
        "python": sys.version.split()[0],
        "platform": f"{platform.system()} {platform.release()} ({platform.machine()})",
    }
    for package in ("mlx", "mlx-lm", "mlx-metal", "transformers", "numpy"):
        try:
            out[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            out[package] = None
    return out


def git_state() -> dict:
    def run(*args: str) -> str | None:
        try:
            return subprocess.run(
                args, cwd=ROOT, capture_output=True, text=True, check=True
            ).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    dirty = run("git", "status", "--porcelain")
    return {
        "commit": run("git", "rev-parse", "HEAD"),
        "branch": run("git", "rev-parse", "--abbrev-ref", "HEAD"),
        # Recorded, not hidden. A run made from a dirty tree is still a run, but a reviewer
        # deserves to know the committed code is not exactly what produced it.
        "dirty": bool(dirty),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Write loss.jsonl and hyperparams.json for a training run.")
    parser.add_argument("--run", type=Path, default=ROOT / "runs" / "current")
    parser.add_argument("--log", type=Path, default=None, help="defaults to <run>/train.log")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "lora.yaml")
    parser.add_argument("--allow-incomplete", action="store_true",
                        help="write the artifacts even if the log has no 'Saved final weights' line")
    args = parser.parse_args()

    log_path = args.log or (args.run / "train.log")
    if not log_path.exists():
        print(f"[record] no log at {log_path}", file=sys.stderr)
        return 1

    records, facts = parse_log(log_path.read_text(errors="replace"))
    if not records:
        print(f"[record] {log_path} contains no Iter reports", file=sys.stderr)
        return 1
    if not facts["completed"] and not args.allow_incomplete:
        print(
            f"[record] log stops at iter {facts['last_iter']} with no 'Saved final weights' line.\n"
            f"[record] refusing to write artifacts for an unfinished run — pass --allow-incomplete "
            f"if that is what you want.",
            file=sys.stderr,
        )
        return 1

    config = yaml.safe_load(args.config.read_text())
    data_dir = ROOT / config.get("data", "data/mlx")

    # Imported late: this pulls in the teacher module, and a missing dependency should not stop
    # the loss curve from being written.
    try:
        from src.prepare_training import PROMPT_VERSION, VALID_FRACTION, SEED

        prompt = {"prompt_version": PROMPT_VERSION, "valid_fraction": VALID_FRACTION, "split_seed": SEED}
    except Exception as exc:  # pragma: no cover - diagnostic path
        prompt = {"prompt_version": None, "error": repr(exc)}

    args.run.mkdir(parents=True, exist_ok=True)
    loss_path = args.run / "loss.jsonl"
    with loss_path.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")

    hyperparams = {
        "run": str(args.run.relative_to(ROOT)),
        "log": str(log_path.relative_to(ROOT)),
        "command": f"uv run python -m mlx_lm lora -c {args.config.relative_to(ROOT)}",
        "base_model": config.get("model"),
        "base_model_revision": config.get("revision"),
        "student_prompt": prompt,
        "config": config,
        "dataset": dataset_fingerprint(data_dir),
        "versions": versions(),
        "git": git_state(),
        "run_facts": facts,
    }
    hp_path = args.run / "hyperparams.json"
    hp_path.write_text(json.dumps(hyperparams, indent=2) + "\n")

    print(f"[record] {loss_path.relative_to(ROOT)}  {len(records)} records "
          f"({facts['reported_steps']} train + {facts['val_evaluations']} val)")
    print(f"[record] {hp_path.relative_to(ROOT)}")
    print(f"[record] iters {facts['last_iter']}  completed={facts['completed']}  "
          f"nan windows={facts['nan_report_windows']}")
    if "first_train_loss" in facts:
        print(f"[record] train loss {facts['first_train_loss']} -> {facts['final_train_loss']}  "
              f"(decreased={facts['loss_decreased']})")
    if "first_val_loss" in facts:
        print(f"[record] val   loss {facts['first_val_loss']} -> {facts['final_val_loss']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
