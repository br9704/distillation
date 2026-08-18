---
id: 12946f3a-de45-41f7-b848-a42f1fa157ba
title: "Charts and Artefacts"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/results"
---

# Charts and Artefacts

**Sixteen committed files carry every number the project publishes.** Eleven under `results/`,
five under `charts/`. The README's evidence table maps each claim to one of them, which is the
whole reason a reader can check this project rather than believe it.

## `results/` - 11 files, 344 KB, all tracked

| File | What it proves |
|---|---|
| `summary.json` | The headline. All three arms, per-class precision, recall and F1, latency, the cost block, and a **provenance block**: base model, pinned revision SHA, adapter SHA-256, held-out file hashes, git commit, dirty flag |
| `summary_final_checkpoint.json` | The **unflattering** evaluation, iteration 1200 at **0.7599**, published next to the shipped 0.8400 so a reader does not have to wonder |
| `predictions.jsonl` | Every one of the 500 student predictions |
| `predictions_final_checkpoint.jsonl` | The same for the final checkpoint |
| `corpus_stats.json` | Corpus receipts: **3,812** harvested, **3,706** labelled, **54** outlets, the full per-class distribution for both teacher and regex, and teacher latency |
| `token_counts.json` | Per-arm token counts measured over all 500 held-out prompts. The artefact `cost.py` refuses to run without |
| `error_analysis.json` · `error_analysis.md` | The error taxonomy by cause, head to head, length and outlet-volume breakdowns |
| `audit_50.md` · `audit_50_sample.json` | The hand audit. **84%** strict teacher agreement, **93%** excluding ambiguous. Recorded **before any student existed** |
| `sanity_20.json` | What the merged model said for 20 predictions and whether each parsed. ⚠️ The merged model it tested no longer exists on disk |

## `charts/` - 5 PNGs, 488 KB, all tracked

| Chart | Bytes | What it shows |
|---|---|---|
| `label_distribution.png` | 120,646 | The hero image. Teacher labels against regex labels across the eight classes. The **74.2% `general`** column is the argument in one picture |
| `training_curve.png` | 112,937 | 1,200 steps of training and validation loss, one point per step because `steps_per_report: 1`. The excursion after iteration 800 is visible |
| `class_distribution.png` | 101,428 | Corpus composition |
| `confusion_student.png` | 78,280 | The student's confusion matrix. `general` and `geopolitics` carry the mass of the errors |
| `confusion_regex.png` | 76,782 | The incumbent's. The `consumer` row is empty |

All five are generated from committed artefacts by `src/chart_*.py`, so they can be regenerated
today **without any model on disk**.

## The design constraint CI enforces

The inherited design system reserves **`#FF9500`** for collision alerts. `src/charts.py` names
the token so the constraint is documented, and **CI greps `src/` to make sure naming it is the
only thing that ever happens to it**. `tests/test_charts_guard.py` goes further and reads the
committed PNGs **pixel by pixel** to prove the reserved amber never appears in a rendered chart.

That is why `pillow` is a declared dev dependency rather than an assumed one: undeclared, the
guard would silently skip in CI, which is the same as not having it.

## `runs/current/` - the provenance layer

| File | Tracked | What it proves |
|---|---|---|
| `hyperparams.json` | ✅ | Config, dataset SHA-256s, resolved revision, library versions, git commit, and 20 recorded run facts including peak memory and NaN windows |
| `loss.jsonl` | ✅ | **199,535 bytes**, one point per step |
| `train.log` | ✅ | **176,649 bytes**, written inside the repo after the first run's log died with it |
| `best/selection.json` | ✅ | The chosen iteration, the ranking, the seven unselectable evaluations, and the statement that the held-out set was never read |
| `best/adapters.safetensors` | ⚠️ **ignored** | **The shipped adapter. Only copy on earth.** See [[(Note) The Deleted Student Weights]] |

## Related

[[(Note) Results Reference]] · [[(Note) Source Tree]] ·
[[(Note) The Deleted Student Weights]] · [[(Note) Test Suite]] · [[(Index) 20 Codebase Map]]
