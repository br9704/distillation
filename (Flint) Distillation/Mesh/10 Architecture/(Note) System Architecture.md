---
id: ffa6a9b7-1c9b-4f8e-ac26-3efa1e95c856
title: "System Architecture"
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

# System Architecture

**One module per pipeline stage, and the pipeline is a straight line with one join at the end.**
`src/reproduce.py` is the only file that knows the whole order, and it **deliberately never
trains**: training is launched explicitly, so no reproduction run can accidentally consume an
hour of GPU.

```mermaid
flowchart TD
    RSS[("63 public RSS feeds<br/>+ 83 same-outlet sections<br/>zero credentials")] --> FEEDS["feeds.py"]
    FEEDS --> HARVEST["harvest.py · rss.py · store.py<br/>async fetch, dedup on normalised URL"]
    GDELT["gdelt.py<br/>planned backfill<br/>0 rows, HTTP 429"] -.->|"unusable"| HARVEST
    HARVEST --> CORPUS[("data/corpus.jsonl<br/>3,706 rows · 54 outlets")]
    CORPUS --> SPLIT["split.py<br/>held-out frozen on first run<br/>disjointness asserted"]
    SPLIT --> POOL[("train_pool<br/>3,206")]
    SPLIT --> HELD[("heldout<br/>500")]
    POOL --> TEACHER["teacher.py<br/>Qwen3.5-35B-A3B Q4_K_M via Ollama<br/>JSON-schema-constrained decoding"]
    HELD --> TEACHER
    TEACHER --> LABELS[("*_labels.jsonl<br/>0.00% unparseable")]
    LABELS --> PREP["prepare_training.py<br/>student_messages()"]
    PREP --> MLX[("data/mlx/<br/>train 3,046 · valid 160 · test 500")]
    MLX --> TRAIN["configs/lora.yaml → mlx_lm.lora<br/>r=16 · bf16 · mask_prompt · 1,200 iters"]
    TRAIN --> CKPT[/"runs/current/adapters/<br/>6 checkpoints"/]
    CKPT --> SEL["select_checkpoint.py<br/>never opens the held-out file"]
    SEL --> BEST[/"runs/current/best/<br/>iteration 800"/]
    BEST --> MERGE["merge_student.py<br/>fuse + 20 sanity predictions"]
    MERGE -.->|"⚠️ deleted 2026-08-16"| MODELS[("models/student-merged/<br/>7.9 GB, gone")]
    BEST --> EVAL["evaluate.py<br/>ONE harness, THREE arms"]
    REGEX["regex_baseline.py<br/>faithful port, 6 defects intact"] --> EVAL
    HELD --> EVAL
    LABELS -.->|"gold"| EVAL
    EVAL --> OUT[("results/summary.json<br/>+ error_analysis + charts/")]
```

## The two decisions that do most of the work

### The contracts were frozen before any label existed

`src/schema.py` and `src/scoring.py` were written, tested and committed in **S1**, commit
`6363455`, in the sprint **before** the teacher was pulled. That is what stops a metric from
being chosen after its result is visible, and it is checkable: the commit predates every label
in the repo.

### Training and evaluation share exactly one prompt definition

`student_messages()` lives in `src/prepare_training.py`. `src/evaluate.py` **imports** it. There
is one definition, so training and evaluation cannot drift apart. This is a small thing that
prevents a whole category of silent, unfalsifiable error.

## Stage by stage

| Stage | Modules | What it produces |
|---|---|---|
| **Harvest** | `feeds.py`, `rss.py`, `harvest.py`, `store.py` | `data/corpus.jsonl`, 3,706 rows from 54 outlets. Async fetch, dedup on normalised URL |
| **Backfill that failed** | `gdelt.py` | **0 rows.** Kept deliberately: the code is correct and the failure is a rate-limit penalty box, so deleting it would lose the finding |
| **Split** | `split.py` | 3,206 train pool, 500 held out. **Membership is frozen on the first split rather than re-drawn**, so a background harvester that keeps adding rows can never leak into the evaluation set. Impossible by construction rather than by remembering the rule |
| **Label** | `teacher.py` | 3,706 labels at **0.00%** unparseable. JSON-schema-constrained decoding, temperature 0, `num_ctx` pinned to 2048 |
| **Prepare** | `prepare_training.py` | `data/mlx/{train,valid,test}.jsonl`, 3,046 / 160 / 500, each with a recorded SHA-256 |
| **Train** | `configs/lora.yaml` → `mlx_lm.lora` | Six checkpoints in `runs/current/adapters/` |
| **Select** | `select_checkpoint.py` | `runs/current/best/`, iteration 800. **The module cannot read the test set**, and it records that it did not |
| **Merge** | `merge_student.py` | ⚠️ `models/student-merged/`, deleted. Fuses, then asks for **20 sanity predictions** against the merged weights, because the merge is the step that could silently produce a valid-but-wrong model |
| **Evaluate** | `evaluate.py`, `error_analysis.py`, `measure_tokens.py`, `cost.py` | `results/summary.json` and everything downstream |
| **Record** | `record_run.py`, `stats.py`, `reproduce.py` | Provenance blocks, corpus receipts, and the seven-step reproduction order |
| **Chart** | `charts.py` + four `chart_*.py` | Five committed PNGs |

## `src/reproduce.py`, the seven steps

Token counts → run record → **checkpoint selection** → training curve → evaluation → error
analysis → confusion matrices.

Selection is a **pipeline step rather than a prerequisite**, so a fresh clone reproduces the
choice of checkpoint instead of inheriting it, and evaluation is pointed at `runs/current/best`
rather than at mlx-lm's final weights. `--dry-run` prints the pipeline without running it.
`--skip-student` loads no model, which is the variant that still works today.

## Related

[[(Note) The Training Pipeline]] · [[(Note) Evaluation and Scoring]] ·
[[(Note) The Corpus and Splits]] · [[(Note) Source Tree]] ·
[[(Note) The Deleted Student Weights]] · [[(Index) 10 Architecture]]
