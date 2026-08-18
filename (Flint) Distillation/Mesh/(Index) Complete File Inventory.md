---
id: 0aa4823f-09a8-4ca7-9d58-869802be05bb
title: "Complete File Inventory"
type: "index"
project: "Distillation"
tags:
  - "#index"
  - "#project"
  - "#ld/living"
  - "#stack/python"
  - "#status/shipped"
  - "#cluster/personal"
status: shipped
created: "2026-08-17"
updated: "2026-08-17"
source_path: "/Users/brunojaamaa/Desktop/distillation"
---

# Complete File Inventory

Every file in `/Users/brunojaamaa/Desktop/distillation` outside the exclusions listed in
[[(Report) Folder Audit]]. Counted **2026-08-17** on branch `main` at `a8a52d1`.

**124 files on disk · 85 tracked by git · 484 MB total, 104 MB outside `.venv`.**

## Tracked file types

| Extension | Count |
|---|---|
| `.py` | **36** |
| `.json` | 14 |
| `.md` | 12 |
| `.ttf` | 5 |
| `.png` | 5 |
| `.jsonl` | 3 |
| `.toml` | 2 |
| `.yml` | 1 |
| `.yaml` | 1 |
| `.txt` | 1 |
| `.mdc` | 1 |
| `.log` | 1 |
| `.lock` | 1 |
| `.gitignore` | 1 |
| `LICENSE` | 1 |

## Root - 20 files

`.gitignore` · `.mcp.json` ⚠️ **never opened** · `AGENTS.md` · `CLAUDE.md` ·
`DOCS-ENGINEERPROMPT.md` · `ENGINEERPROMPT.md` · `GEMINI.md` (byte-identical to `AGENTS.md`) ·
`LICENSE` · `METHODOLOGY.md` · `NOTICE.md` · `OBSIDIANLOG.md` · `PROJECT.json` · `README.md` ·
`SYNC.md` · `masterplan.md` · `opencode.json` ⚠️ **never opened** · `pyproject.toml` ·
`uv.lock` · `.DS_Store`

Directories: `assets/`, `charts/`, `configs/`, `data/`, `models/` ⚠️ **empty**, `results/`,
`runs/`, `src/`, `tests/`, `.claude/`, `.codex/`, `.cursor/`, `.github/`, `.vscode/`,
`.git/` ⚫, `.venv/` ⚫, `.pytest_cache/` ⚫, and `(Flint) Distillation/` (this vault).

## `src/` - 25 modules, 544 KB, 4,363 lines

`__init__.py` · `chart_confusion.py` · `chart_corpus.py` · `chart_labels.py` ·
`chart_training.py` · `charts.py` · `cost.py` · `error_analysis.py` · `evaluate.py` ·
`feeds.py` · `gdelt.py` · `harvest.py` · `measure_tokens.py` · `merge_student.py` ·
`prepare_training.py` · `record_run.py` · `regex_baseline.py` · `reproduce.py` · `rss.py` ·
`schema.py` · `scoring.py` · `select_checkpoint.py` · `split.py` · `stats.py` ·
`teacher.py` (302 lines, the largest)

Plus `src/__pycache__/` ⚫ 25 `.pyc` files, gitignored.

## `tests/` - 9 files plus `__init__.py`, 248 KB, 1,014 lines

| File | Test functions |
|---|---|
| `test_corpus.py` | **17** |
| `test_error_analysis.py` | **15** |
| `test_scoring.py` | **12** |
| `test_regex_baseline.py` | **11** |
| `test_teacher.py` | **11** |
| `test_cost.py` | 9 |
| `test_record_run.py` | 6 |
| `test_chart_confusion.py` | 5 |
| `test_charts_guard.py` | 4 |

**90 functions total**, counted as **139 tests** after parametrisation. Plus
`tests/__pycache__/` ⚫ 9 `.pyc` files.

## `data/` - 12 files, 5.1 MB ⚠️ gitignored, no backup

`corpus.jsonl` (1,421,452 B) · `train_pool.jsonl` (1,251,073 B) ·
`train_labels.jsonl` (758,201 B) · `heldout.jsonl` (197,096 B) ·
`heldout_labels.jsonl` (118,312 B) · `teacher_latency.jsonl` (43,516 B) ·
`mlx/train.jsonl` (591,913 B) · `mlx/test.jsonl` (97,409 B) · `mlx/valid.jsonl` (30,846 B) ·
`mlx_smoke/test.jsonl` (750,409 B) · `mlx_smoke/train.jsonl` (28,452 B) ·
`mlx_smoke/valid.jsonl` (1,520 B)

## `runs/` - 21 files, 49 MB

**`runs/current/` (13)**: `loss.jsonl` (199,535 B) ✅ · `train.log` (176,649 B) ✅ ·
`hyperparams.json` (2,634 B) ✅ · `best/selection.json` (1,502 B) ✅ ·
`best/adapter_config.json` (1,125 B) ✅ · `best/adapters.safetensors` (3,672,013 B) ⚠️ **ignored** ·
`adapters/adapter_config.json` (1,125 B) ⚠️ · `adapters/adapters.safetensors` ⚠️ ·
`adapters/{0000200,0000400,0000600,0000800,0001000,0001200}_adapters.safetensors` ⚠️,
**3,672,013 bytes each**

**`runs/interrupted-panic-20260815/` (8)** ⚠️ all ignored: `adapters/adapter_config.json`
(1,126 B) · `adapters/adapters.safetensors` ·
`adapters/{0000200,0000400,0000600,0000800,0001000}_adapters.safetensors`. The run that died at
~iteration 1,170 of 1,200.

## `results/` - 11 files, 344 KB, all tracked ✅

`audit_50.md` · `audit_50_sample.json` · `corpus_stats.json` · `error_analysis.json` ·
`error_analysis.md` · `predictions.jsonl` · `predictions_final_checkpoint.jsonl` ·
`sanity_20.json` · `summary.json` · `summary_final_checkpoint.json` · `token_counts.json`

## `charts/` - 5 files, 488 KB, all tracked ✅

`label_distribution.png` (120,646 B, the hero) · `training_curve.png` (112,937 B) ·
`class_distribution.png` (101,428 B) · `confusion_student.png` (78,280 B) ·
`confusion_regex.png` (76,782 B)

## `configs/` - 1 file

`lora.yaml`

## `assets/fonts/` - 6 files, 684 KB

`Geist-Regular.ttf` · `Geist-Medium.ttf` · `Geist-SemiBold.ttf` · `GeistMono-Regular.ttf` ·
`GeistMono-Medium.ttf` · `LICENSE.txt`

## `.github/` - 1 file

`workflows/ci.yml`

## Agent and editor wiring - gitignored

`.claude/` · `.codex/` · `.cursor/` (including `rules/aethereum.mdc` and `mcp.json`
⚠️ **never opened**) · `.vscode/mcp.json` ⚠️ **never opened**

## `models/` - 0 files ⚠️

Empty. **7.9 GB deleted 2026-08-16.** See [[(Note) The Deleted Student Weights]].

## Excluded, counted only

| Path | Size |
|---|---|
| `.venv/` | **380 MB** |
| `.git/` | **4.3 MB** |
| `__pycache__/` | 34 `.pyc` files |
| `.pytest_cache/` | small |

## Related

[[(Report) Folder Audit]] · [[(Note) Source Tree]] · [[(Note) The Deleted Student Weights]] ·
[[(Map) Master Map]]
