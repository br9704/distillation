---
id: a39c3b9b-9c4a-4f09-8564-9cb89adc3e8c
title: "Install and Run"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/pyproject.toml"
---

# Install and Run

**The environment is already installed.** `.venv/` is present at **380 MB**. There is no reason
to run `uv sync` on this machine, and doing so is explicitly out of bounds for agents.

## Requirements

| | |
|---|---|
| Python | **≥ 3.12, < 3.13**, pinned. System Python is 3.14, which is **too new for the ML wheels** |
| Package manager | `uv`, with `package = false`, so the project is scripts rather than a library |
| Platform | **Apple silicon.** MLX is a Metal library with no Linux wheel. CI runs on `macos-14` for the same reason |
| Memory | The training run peaked at **43.911 GB** unified, so it needs the 48 GB machine |
| Runtime dependencies | mlx ≥ 0.32.0 · mlx-lm ≥ 0.31.3 · httpx ≥ 0.27 · pydantic ≥ 2.9 · matplotlib ≥ 3.9 · numpy ≥ 1.26 · pyyaml ≥ 6.0 |
| Dev dependencies | pytest ≥ 8.3 · pillow ≥ 10.0 |

## 🟢 What runs today, with no weights on disk

```bash
cd /Users/brunojaamaa/Desktop/distillation
uv run pytest -q                                  # 139 tests, green
uv run python -m src.evaluate --skip-student      # the incumbent regex arm, end to end
uv run python -m src.stats                        # corpus + teacher receipts
uv run python -m src.reproduce --dry-run          # print the pipeline without running it
uv run python -m src.reproduce --skip-student     # everything that loads no model
```

Cost arithmetic, error analysis, checkpoint selection and all five charts also work, because
each reads a committed artefact rather than a model.

## ⚫ What does not run

| Command | Why |
|---|---|
| `uv run python -m src.merge_student` | Needs the base weights. **~8.5 GB download** |
| Any student prediction, including the 20 sanity checks | Needs the base weights |
| `uv run python -m src.measure_tokens` | Needs the tokeniser, which ships with the base weights |
| `uv run python -m src.teacher ...` | Needs the **22 GB** Ollama pull |
| `uv run mlx_lm.lora --config configs/lora.yaml` | Needs the base weights, and ~64 minutes |

**No published number depends on any of these.** Everything is committed under `results/`.

## The full pipeline, for reference only

This is what the README documents. **Do not run the labelling or training steps.**

```bash
uv sync                                          # already done; do not re-run
uv run pytest -q

uv run python -m src.harvest                     # rebuild the corpus from public RSS
uv run python -m src.split                       # held-out 500, frozen on first run

# Labelling needs the teacher pulled locally first:
#   ollama pull hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M    # 22 GB
uv run python -m src.teacher --input data/heldout.jsonl    --output data/heldout_labels.jsonl
uv run python -m src.teacher --input data/train_pool.jsonl --output data/train_labels.jsonl
uv run python -m src.teacher --latency --n 500             # sequential timing, before deletion
uv run python -m src.prepare_training            # → data/mlx/{train,valid,test}.jsonl

uv run mlx_lm.lora --config configs/lora.yaml    # LoRA r=16, bf16

uv run python -m src.reproduce                   # every result and chart, in dependency order
uv run python -m src.stats                       # corpus + teacher receipts
```

⚠️ **`src.harvest` would not reproduce the corpus even if you ran it.** Feeds have moved. See
[[(Note) The Corpus and Splits]].

## The output you should see

```
arm         macro-F1  accuracy    p50 ms    p95 ms  invalid
regex         0.3372    0.3420       0.0       0.0        0
student       0.8400    0.8540     322.1     403.0        0
teacher          n/a       n/a     781.8     867.7
[eval] teacher quality is n/a by construction, see results/summary.json
```

`invalid 0` on the student matters more than it looks: **every one of its 500 outputs parsed to a
valid class with no coercion and no retry.** That is the payoff of the S5 `enable_thinking=False`
finding. Without it, the same adapter emits reasoning prose and scores near zero.

## Related

[[(Note) Command Surface]] · [[(Note) The Deleted Student Weights]] ·
[[(Note) CI and Publication]] · [[(Note) Environment Variables]] · [[(Index) 30 Setup & Run]]
