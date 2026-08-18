---
id: 17c2360e-0e1f-431d-b335-77d3e55a29c4
title: "Command Surface"
type: "note"
project: "Distillation"
tags:
  - "#note"
  - "#project"
  - "#ld/living"
  - "#stack/python"
  - "#status/shipped"
  - "#cluster/personal"
status: shipped
created: "2026-08-17"
updated: "2026-08-17"
source_path: "/Users/brunojaamaa/Desktop/distillation/src"
---

# Command Surface

**There is no CLI binary. Every stage is a module, run as `python -m src.<name>`.** That is
deliberate: the pipeline is the interface, and each stage is independently runnable and
independently testable.

## In pipeline order

| Command | Stage | Runs today |
|---|---|---|
| `uv run python -m src.harvest` | Fetch the corpus from 63 feeds plus 83 section feeds | ⚠️ runs, but cannot reproduce the corpus |
| `uv run python -m src.gdelt` | The planned backfill | ⚫ returns 429 |
| `uv run python -m src.split` | Held-out 500, **frozen on first run** | 🟢 |
| `uv run python -m src.teacher --input <in> --output <out>` | Label with the 35B teacher | ⚫ needs the 22 GB pull |
| `uv run python -m src.teacher --latency --n 500` | Sequential warm timing | ⚫ same |
| `uv run python -m src.prepare_training` | Build `data/mlx/{train,valid,test}.jsonl` | 🟢 |
| `uv run mlx_lm.lora --config configs/lora.yaml` | The training run, **launched explicitly** | ⚫ needs base weights, ~64 min |
| `uv run python -m src.select_checkpoint` | Rank checkpoints on validation loss only | 🟢 reads `loss.jsonl` |
| `uv run python -m src.merge_student` | Fuse, then 20 sanity predictions | ⚫ needs base weights |
| `uv run python -m src.merge_student --sanity-only` | Check an existing merge | ⚫ no merge exists |
| `uv run python -m src.merge_student --skip-merge --adapter runs/current/adapters` | Sanity-check an adapter directly | ⚫ needs base weights |
| `uv run python -m src.evaluate` | All three arms | ⚫ needs base weights |
| `uv run python -m src.evaluate --skip-student` | **Regex and teacher rows, no model load** | 🟢 |
| `uv run python -m src.measure_tokens` | Re-tokenise all 500 held-out prompts | ⚫ needs the tokeniser |
| `uv run python -m src.error_analysis` | Taxonomy, head to head, breakdowns | 🟢 |
| `uv run python -m src.record_run` | Write the provenance block | 🟢 |
| `uv run python -m src.stats` | Corpus and teacher receipts | 🟢 |
| `uv run python -m src.reproduce` | The seven-step pipeline | ⚫ partly |
| `uv run python -m src.reproduce --dry-run` | Print the pipeline, run nothing | 🟢 |
| `uv run python -m src.reproduce --skip-student` | Everything that loads no model | 🟢 |
| `uv run pytest -q` | **139 tests** | 🟢 |

## The seven steps `reproduce` runs

Token counts → run record → **checkpoint selection** → training curve → evaluation → error
analysis → confusion matrices.

**It deliberately never trains.** Training is launched explicitly, so a reproduction run cannot
accidentally consume an hour of GPU. And **selection is a step rather than a prerequisite**, so a
fresh clone reproduces the choice of checkpoint instead of inheriting it. Evaluation is pointed at
`runs/current/best`, not at mlx-lm's final weights.

## The flags that matter

| Flag | Meaning |
|---|---|
| `--skip-student` | Load no model. **This is the flag that keeps the repo useful today** |
| `--dry-run` | Print the pipeline without running it |
| `--sanity-only` | Check an existing merge instead of producing one |
| `--skip-merge --adapter <path>` | Sanity-check an adapter without fusing |
| `--latency --n <n>` | Sequential warm timing, warm-up calls discarded |

## Related

[[(Note) Install and Run]] · [[(Note) System Architecture]] ·
[[(Note) The Deleted Student Weights]] · [[(Index) 30 Setup & Run]]
