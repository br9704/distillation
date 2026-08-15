"""Pick the checkpoint with the lowest validation loss and materialise it as a loadable adapter.

Why this exists: `mlx-lm` saves periodic checkpoints as `0000400_adapters.safetensors`, but
`load(adapter_path=...)` expects a *directory* holding `adapters.safetensors` next to
`adapter_config.json`. So the intermediate checkpoints are on disk and effectively unloadable
without this step, and "just use the final weights" becomes the path of least resistance
rather than a decision.

That matters here. Training loss falls monotonically while validation loss bottoms out and
turns — the classic overfitting signature. Evaluating the final checkpoint when an earlier one
generalises better would understate the student, and picking a checkpoint on the *validation*
split is standard practice precisely because that split is not the held-out 500.

**The held-out 500 play no part in this choice.** Selection reads only the validation series in
`runs/<id>/loss.jsonl`, which comes from the 160 validation examples carved out of the training
pool. Selecting on the test set would be a leak, and the whole project's headline number would
be worthless. This module never opens the held-out file.

    uv run python -m src.select_checkpoint              # report the ranking, choose nothing
    uv run python -m src.select_checkpoint --materialise # write runs/current/best/
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def val_series(loss_path: Path) -> list[dict]:
    records = [json.loads(line) for line in loss_path.open() if line.strip()]
    return [r for r in records if r.get("split") == "valid" and r.get("loss") is not None]


def available_checkpoints(adapter_dir: Path) -> dict[int, Path]:
    """Map iteration -> checkpoint file. `adapters.safetensors` is the rolling latest and is
    deliberately excluded: it duplicates whichever numbered checkpoint was written last."""
    out = {}
    for path in adapter_dir.glob("*_adapters.safetensors"):
        stem = path.name.split("_")[0]
        if stem.isdigit():
            out[int(stem)] = path
    return dict(sorted(out.items()))


def choose(val: list[dict], checkpoints: dict[int, Path]) -> tuple[int | None, dict]:
    """Lowest validation loss among iterations that actually have a saved checkpoint.

    A val evaluation at an iteration with no checkpoint cannot be selected, however good it
    looks — reporting a number produced by weights that no longer exist would be unbackable.
    """
    candidates = [r for r in val if r["iter"] in checkpoints]
    ranking = sorted(candidates, key=lambda r: r["loss"])
    detail = {
        "val_evaluations": len(val),
        "val_evaluations_with_a_checkpoint": len(candidates),
        "ranking": [{"iter": r["iter"], "val_loss": r["loss"]} for r in ranking],
        "unselectable": [
            {"iter": r["iter"], "val_loss": r["loss"], "why": "no checkpoint saved at this iteration"}
            for r in val
            if r["iter"] not in checkpoints
        ],
    }
    return (ranking[0]["iter"] if ranking else None), detail


def materialise(adapter_dir: Path, iteration: int, checkpoints: dict[int, Path], out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(checkpoints[iteration], out / "adapters.safetensors")
    config = adapter_dir / "adapter_config.json"
    if config.exists():
        shutil.copy2(config, out / "adapter_config.json")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Select the best-validation checkpoint.")
    parser.add_argument("--run", type=Path, default=ROOT / "runs" / "current")
    parser.add_argument("--out", type=Path, default=None, help="defaults to <run>/best")
    parser.add_argument("--materialise", action="store_true", help="write the chosen adapter directory")
    parser.add_argument("--iter", type=int, default=None, help="force a specific iteration")
    args = parser.parse_args()

    loss_path = args.run / "loss.jsonl"
    adapter_dir = args.run / "adapters"
    out = args.out or (args.run / "best")

    if not loss_path.exists():
        print(f"[select] no loss log at {loss_path} — run src.record_run first", file=sys.stderr)
        return 1

    val = val_series(loss_path)
    checkpoints = available_checkpoints(adapter_dir)
    if not val:
        print("[select] no validation losses in the log", file=sys.stderr)
        return 1
    if not checkpoints:
        print(f"[select] no numbered checkpoints in {adapter_dir}", file=sys.stderr)
        return 1

    best, detail = choose(val, checkpoints)
    chosen = args.iter if args.iter is not None else best
    final = max(checkpoints)

    print(f"[select] checkpoints on disk: {sorted(checkpoints)}")
    print("[select] validation loss by iteration (selectable only):")
    for row in detail["ranking"]:
        mark = " <- best" if row["iter"] == best else ""
        print(f"[select]   iter {row['iter']:>5}  val {row['val_loss']:.4f}{mark}")
    for row in detail["unselectable"]:
        print(f"[select]   iter {row['iter']:>5}  val {row['val_loss']:.4f}  (no checkpoint)")

    if chosen is None:
        print("[select] nothing selectable", file=sys.stderr)
        return 1

    by_val = {r["iter"]: r["loss"] for r in val}
    if chosen != final:
        print(f"[select] the best checkpoint is NOT the final one: "
              f"iter {chosen} (val {by_val[chosen]:.4f}) vs iter {final} (val {by_val.get(final, float('nan')):.4f})")
    else:
        print(f"[select] the final checkpoint is also the best (iter {final})")

    if args.materialise:
        path = materialise(adapter_dir, chosen, checkpoints, out)
        record = {
            "chosen_iter": chosen,
            "chosen_val_loss": by_val.get(chosen),
            "final_iter": final,
            "final_val_loss": by_val.get(final),
            "forced": args.iter is not None,
            "selected_on": (
                "the 160-example validation split carved from the training pool. The held-out "
                "500 played no part in this choice and were never read by this module."
            ),
            **detail,
        }
        (out / "selection.json").write_text(json.dumps(record, indent=2) + "\n")
        print(f"[select] materialised -> {path.relative_to(ROOT)} (adapters.safetensors + adapter_config.json)")
        print(f"[select] wrote {(out / 'selection.json').relative_to(ROOT)}")
    else:
        print("[select] dry run — pass --materialise to write the adapter directory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
