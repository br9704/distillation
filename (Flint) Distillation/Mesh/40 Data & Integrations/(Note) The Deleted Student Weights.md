---
id: a133bd6d-d9fc-4789-8cd2-b740b8008630
title: "The Deleted Student Weights"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/models"
---

# The Deleted Student Weights

> [!warning] Read this before running anything that loads a model
> `models/student-merged/` is gone. The `models/` directory exists and is **empty**. Do not
> start a download or a training run to "fix" it without asking Bruno first.

**Verdict: ⚠️ the merged student weights and the base model were deleted on 2026-08-16, with
Bruno's explicit authorisation, during a storage migration. The trained adapter survived. Every
published result survived. The repo still runs for everything except loading a model.**

## What was deleted, and when

| Artefact | Size | When | Why |
|---|---|---|---|
| `models/student-merged/` | **7.9 GB** | **2026-08-16** | Storage migration, authorised by Bruno |
| Base HuggingFace weights, `mlx-community/Qwen3.5-4B-bf16` | **~8 GB** | **2026-08-16** | Same migration. `~/.cache/huggingface/hub` **no longer exists at all** |
| Teacher weights, `hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M` | **22 GB** | **earlier, during S4** | Deleted **by the project's own plan**, not by the migration. `~/.ollama` is now **12 KB** |

The repo was **8.3 GB** and is now **484 MB**, of which `.venv` is **380 MB**. The deletion took
**95%** of the tree.

**The teacher deletion is a different event and predates the migration.** The whole sprint
sequence was designed around **34 GB of free disk**: the naive ordering needs 37 GB, being 19 GB
teacher plus 8 GB base plus 8 GB merged plus the environment, so the plan deletes the teacher
before the student base is pulled. That is also why teacher latency had to be measured while the
weights were still resident, which the repo did, sequentially, over the same held-out 500.
Amendment **A2** records that the real pull was **22 GB** rather than the budgeted 19 GB.

## What survived, and this is the important part

| Artefact | Size | Path |
|---|---|---|
| **The shipped LoRA adapter** | **3,672,013 bytes**, 3.67 MB | `runs/current/best/adapters.safetensors` |
| Its config and selection record | 1,125 B + 1,502 B | `runs/current/best/adapter_config.json`, `selection.json` |
| Six training checkpoints, iterations 200 to 1200 | 3.67 MB each | `runs/current/adapters/` |
| Six more from the run that died | 3.67 MB each | `runs/interrupted-panic-20260815/adapters/` |
| The full loss curve and training log | 199,535 B + 176,649 B | `runs/current/loss.jsonl`, `train.log` |
| The corpus, splits and all labels | **5.1 MB** | `data/` |
| **Every published result** | 344 KB | `results/`, all **11 files committed to git** |
| **Every chart** | 488 KB | `charts/`, all **5 PNGs committed to git** |

`runs/` totals **49 MB**. The adapter's SHA-256 is recorded in `results/summary.json`'s
provenance block alongside the pinned base-model revision and the held-out file hashes, so the
surviving adapter can be proven to be the one that produced the published numbers.

## ⚠️ The adapter and the corpus are not backed up anywhere

This is a bigger risk than the deletion itself.

`.gitignore` excludes `*.safetensors`, `runs/*/adapters/` and all of `data/`. Confirmed with
`git status --ignored`: `runs/current/adapters/`, `runs/current/best/adapters.safetensors` and
`runs/interrupted-panic-20260815/` are all ignored. **The GitHub remote does not have them.**

So the only copy of the trained adapter, and the only copy of the corpus, is on this Mac.

**And the corpus is not re-harvestable.** `.gitignore` says `data/` is "regenerable from
`src/harvest.py` + `src/gdelt.py`". The repo's own measurements contradict that: one pass over
the 63 feeds yields **~1,800 unique** headlines and a second pass fifteen minutes later yields
**7**, because RSS carries a rolling window. GDELT is unusable on this network, one request
succeeds and every subsequent one returns **429** regardless of spacing, verified at 20 s and at
65 s, contributing **zero** rows over 20 minutes. The README states the corpus is "a snapshot of
August 2026 rather than a stable benchmark". **Feeds have moved on. It cannot be rebuilt.**

## What it would cost to rebuild, three scenarios

### Scenario 1 - restore `models/student-merged/` · ~8.5 GB download + minutes of compute

This is all that is actually required, because the adapter survived.

1. Re-download `mlx-community/Qwen3.5-4B-bf16` at revision
   `491fdc7c087ba7fb48adcb1253f8e76d011db783`, pinned in `configs/lora.yaml`. **~8.5 GB.**
2. `uv run python -m src.merge_student`, which fuses the adapter and then asks the merged model
   for **20 sanity predictions** before anything downstream trusts it.

Compute is minutes. **No training run is needed.** The claim that the merged model is
"re-derivable only by a multi-hour training run" is **not correct while the adapter exists**,
and it becomes correct the moment the adapter is lost.

The merge is also, in the project's own words, worth questioning: the masterplan recommends
**against** publishing merged weights at all, calling 7.9 GB "a maintenance liability, not a
contribution" when the alternative is one `mlx_lm fuse` command.

### Scenario 2 - the adapter is also lost · ~8.5 GB download + ~64 minutes training

Retraining is possible **only because `data/mlx/` still exists locally**.

| | Measured value |
|---|---|
| Wall clock | **3,833.9 s**, about **64 minutes** |
| Iterations | **1,200** at batch 8, roughly 3.2 epochs over 3,046 examples |
| Throughput | median **0.313** iterations per second |
| Peak memory | **43.911 GB** unified. This needs the 48 GB machine |
| Trained tokens | **61,910** |
| Trainable parameters | **0.918M**, **0.022%** of 4.21B |
| Seed | `20260814`, pinned |

Add the **~8.5 GB** base download first. Then `src.select_checkpoint` and `src.reproduce` to
regenerate everything else. Note that a different run will not reproduce 0.840 exactly: the repo
is explicit that there is **one seed and one run**, with no variance estimate, and that the third
decimal is noise.

### Scenario 3 - full rebuild from a fresh clone · not possible as specified

A clone of `br9704/distillation` has no `data/` and no adapter. Rebuilding would need:

1. **Re-harvest the corpus.** ❌ **Cannot be done.** Feeds have moved, and the repo measured that
   they do not refill.
2. Re-download the teacher, **22 GB**, and re-label **3,706** headlines. At the measured
   sequential p50 of **782 ms** that is **~48 minutes** of pure inference as a floor, and the
   real labelling run was longer.
3. Re-download the base, **~8.5 GB**, and retrain, **~64 minutes**.
4. Merge and evaluate.

Even then the result would be a **different** corpus and therefore a different, non-comparable
number. **This project is reproducible in method but not in data.** That is worth stating
plainly, and it is the strongest argument for backing up `data/` today.

## Can the repo still run as it stands? Mostly yes 🟢

`.venv` is present at **380 MB**, so nothing needs installing.

| Works today | Command |
|---|---|
| 🟢 The whole test suite | `uv run pytest -q` |
| 🟢 The incumbent regex arm, end to end | `uv run python -m src.evaluate --skip-student` |
| 🟢 Corpus and teacher statistics | `uv run python -m src.stats` |
| 🟢 Cost arithmetic | reads the committed `results/token_counts.json` |
| 🟢 Error analysis | reads the committed `results/predictions.jsonl` |
| 🟢 Checkpoint selection | reads `runs/current/loss.jsonl` |
| 🟢 All five charts | `src/chart_*.py` read committed artefacts |
| 🟢 Most of the pipeline | `uv run python -m src.reproduce --skip-student` |

| Does not work | Why |
|---|---|
| ⚫ Merging the adapter | Needs the base weights |
| ⚫ Any student prediction, including the 20 sanity checks | Needs the base weights |
| ⚫ Re-measuring token counts | Needs the tokeniser, which ships with the base weights |
| ⚫ Anything calling the teacher | Needs the 22 GB Ollama pull |

**No published number depends on any of this.** Every figure in the README and in
`METHODOLOGY.md` cites a file under `results/` or `runs/current/`, and all of those are
committed. The evidence table in the README maps claim to artefact line by line.

## What to do about it

- [ ] **Back up `runs/current/best/adapters.safetensors` and all of `data/` off this machine.** Together they are **5.1 MB plus 3.67 MB**. This is the highest-value, lowest-cost action in the whole project #task [project:: Distillation] [priority:: high]
- [ ] Reconsider the deferred Hugging Face gate for the **adapter only**, a few MB with `base_model:` metadata. It would put the one irreplaceable artefact somewhere durable and give the lineage third-party corroboration #task [project:: Distillation]
- [ ] Fix the `.gitignore` comment that calls `data/` "regenerable". The repo's own measurements say it is not #task [project:: Distillation]
- [ ] Do **not** re-download anything to restore `models/student-merged/` unless there is a reason to run the student again. The masterplan already recommends against keeping merged weights #task [project:: Distillation] [priority:: low]

## Related

[[(Note) The Corpus and Splits]] · [[(Note) Teacher and Student Models]] ·
[[(Note) The Training Pipeline]] · [[(Note) Honest State]] · [[(Note) Install and Run]] ·
[[(Report) Gaps & Questions]] · [[(Index) 40 Data & Integrations]]
