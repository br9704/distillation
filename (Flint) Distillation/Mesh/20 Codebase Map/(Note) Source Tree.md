---
id: 46a790f2-62a5-45ec-8845-8d90c90e1860
title: "Source Tree"
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

# Source Tree

**25 modules, 544 KB, 4,363 lines.** Flat, no packages beneath `src/`, one module per stage.
Every module is runnable as `python -m src.<name>`.

## Corpus

| Module | What it does |
|---|---|
| `feeds.py` | The feed catalog. **63** production feeds plus **83** committed `EXPANSION_FEEDS`, live section feeds from outlets already in the catalog, worth **+1,890** rows |
| `rss.py` | Feed parsing |
| `harvest.py` | Async fetch, dedup on normalised URL |
| `store.py` | JSONL read and write, the `DATA` path constant |
| `gdelt.py` | The planned backfill. Contributed **0 rows**. ⚫ Kept deliberately: the code is correct and the failure was a rate-limit penalty box, so deleting it would lose the finding |

## Split and contracts

| Module | What it does |
|---|---|
| `split.py` | Held-out **500** frozen on first run. Disjointness asserted, not assumed |
| `schema.py` | `TOPIC_CLASSES`, `UNPARSEABLE`, the eight-class taxonomy. **Committed before any label existed** |
| `scoring.py` | Macro-F1 over all eight classes, ~60 lines from first principles. **Committed before any label existed** |

## Teacher and incumbent

| Module | Lines | What it does |
|---|---|---|
| `teacher.py` | **302**, the largest | The Ollama client. JSON-schema-constrained decoding, temperature 0, `num_ctx` pinned to 2048, parser guards, a `--latency` mode for sequential timing |
| `regex_baseline.py` | | A faithful Python port of the production `classifyWireItem()`. **Six defects intact.** `re.ASCII` is set because JavaScript's word boundary is ASCII-based and Python's is Unicode-aware, and without the flag the incumbent arm would have been quietly stronger than the real thing |

## Training

| Module | What it does |
|---|---|
| `prepare_training.py` | `student_messages()`, the single shared prompt shape that `evaluate.py` imports. Writes `data/mlx/{train,valid,test}.jsonl` |
| `select_checkpoint.py` | Ranks checkpoints on validation loss. **Never opens the held-out file**, and records that it did not, in `runs/current/best/selection.json` |
| `merge_student.py` | Fuses the adapter into standalone weights, then asks the **merged** model for 20 sanity predictions before anything downstream trusts it. ⚠️ Its output directory was deleted. See [[(Note) The Deleted Student Weights]] |

## Evaluation

| Module | What it does |
|---|---|
| `evaluate.py` | **One harness, three arms.** `--skip-student` loads no model, which is the mode that still runs today |
| `error_analysis.py` | Taxonomy by cause, head to head, breakdowns by headline length and outlet volume |
| `measure_tokens.py` | Re-tokenises all 500 held-out prompts through each arm's real prompt builder. This is what corrected four wrong constants and moved the headline from 45.4x to 41.3x |
| `cost.py` | List-price arithmetic. **Reads `results/token_counts.json` and raises if it is missing**, so it can no longer fall back to a hardcoded constant |

## Provenance and reproduction

| Module | What it does |
|---|---|
| `record_run.py` | Writes `runs/*/hyperparams.json`: config, dataset SHA-256s, resolved revision, library versions, git commit and dirty flag, run facts |
| `stats.py` | Recomputes every corpus and teacher figure from the gitignored JSONL into `results/corpus_stats.json`, so the README cites an artefact rather than a ledger entry |
| `reproduce.py` | Seven steps in dependency order. **Deliberately never trains.** `--dry-run` prints the pipeline, `--skip-student` loads no model |

## Charts

`charts.py` is the shared renderer, which vendors Geist from `assets/fonts/` and names the
reserved amber `#FF9500` without ever using it. Four producers: `chart_labels.py`,
`chart_corpus.py`, `chart_training.py`, `chart_confusion.py`.

## Quality signals

| Signal | Value |
|---|---|
| `TODO` / `FIXME` / `HACK` markers | **0** in `src/` and `tests/` |
| Dead modules | **0**. `gdelt.py` is inert but kept with a written reason |
| Runtime dependencies | **7**: mlx, mlx-lm, httpx, pydantic, matplotlib, numpy, pyyaml |
| Dev dependencies | **2**: pytest, pillow |

`pyyaml` is declared explicitly with a comment explaining why: `record_run.py` and `evaluate.py`
read the pinned revision out of `configs/lora.yaml`, and **a result's provenance must not depend
on a transitive dependency staying put**, even though mlx-lm happens to pull it in. `pillow` is
declared for the same reason: `tests/test_charts_guard.py` reads committed PNGs pixel by pixel,
and undeclared, that guard would silently skip in CI, which is the same as not having it.

## Related

[[(Note) System Architecture]] · [[(Note) Charts and Artefacts]] · [[(Note) Test Suite]] ·
[[(Report) Folder Audit]] · [[(Index) 20 Codebase Map]]
