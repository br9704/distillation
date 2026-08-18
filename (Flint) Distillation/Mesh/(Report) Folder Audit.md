---
id: 58950b00-7c3b-45e3-b53b-87344c6048cd
title: "Folder Audit"
type: "report"
project: "Distillation"
tags:
  - "#report"
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

# Folder Audit

Recursive read-only audit of `/Users/brunojaamaa/Desktop/distillation`, taken **2026-08-17** on
branch `main` at commit `a8a52d1`. Working tree clean, **0** unpushed. **124 files** outside the
exclusions, **85 of them tracked by git**. On disk **484 MB**, of which **380 MB is `.venv`**.

## Verdict

🟢 **Every folder earns its place and there is no dead code.** Thirteen top-level directories,
all referenced by the pipeline, the tests, CI or the write-up. One module, `src/gdelt.py`, is
kept deliberately despite contributing zero rows, and the reason is written down: the code is
correct and the failure was a rate-limit penalty box, so deleting it would lose the finding.

⚠️ **The one real problem is what is not here.** `models/` is an **empty directory**: 7.9 GB of
merged student weights were deleted on **2026-08-16**, and the base HuggingFace weights went
with them. See [[(Note) The Deleted Student Weights]].

⚠️ **The second problem is what git does not have.** `data/` (5.1 MB), `runs/*/adapters/` and
`runs/current/best/adapters.safetensors` are all gitignored. The trained adapter and the entire
corpus exist **only on this Mac**.

## Excluded from the audit, with reasons

| Path | Size | Why excluded |
|---|---|---|
| `.venv/` | **380 MB** | uv-managed virtual environment. Python 3.12, MLX, mlx-lm and friends. Gitignored, rebuilt by `uv sync`, which this audit did **not** run |
| `.git/` internals | **4.3 MB** | Object store. Read-only `log`, `status`, `branch`, `remote`, `ls-files`, `tag` only |
| `__pycache__/` | 25 + 9 files | Bytecode. Gitignored. Counted, never read |
| `.pytest_cache/` | small | Test cache. Gitignored |
| `models/` | **0 bytes, empty** | ⚠️ Not excluded by policy but by absence. See [[(Note) The Deleted Student Weights]] |
| `.mcp.json` · `.cursor/mcp.json` · `.vscode/mcp.json` · `opencode.json` | ~226 B to ~350 B | Hold an `Authorization` bearer header for the hosted Aethereum MCP server. **Never opened.** Grepped for key names only. All gitignored |
| `.claude/` · `.codex/` · `.vscode/` | small | Per-developer agent and editor wiring |
| `uv.lock` | **93 KB** | Dependency lockfile. Summarised, not read line by line |
| `(Flint) Distillation/` | this vault | Created by this audit. Documented in [[(Report) Build Log]] |

**Zero dataless iCloud files.** `find . -type f -flags +dataless` returned nothing.

**No training was run, no weights were downloaded, no `uv sync`, no `pip install`.**

## Root - 20 files, and the documentation is the deliverable

The root carries **eight markdown documents totalling roughly 3,250 lines**, which is more prose
than code by line count and is the point: the project's output is a measurement, and a
measurement nobody can check is not one.

| File | Bytes | Lines | What it is |
|---|---|---|---|
| `masterplan.md` | **77,662** | 1,121 | The sprint log, S0 to S9 plus Sprint D. Acceptance gates, as-shipped deltas, deferrals, and an append-only amendments section |
| `SYNC.md` | **51,122** | 757 | The decision ledger. Every material choice with its reasoning |
| `README.md` | **39,820** | 606 | The public front page: plain-language explanation, the three-arm results table, architecture diagram, how it was built, an evidence table mapping every claim to a file, cost arithmetic, limitations, status |
| `METHODOLOGY.md` | **21,673** | 414 | Corpus construction, the split protocol, the teacher prompt, the noise ceiling, what "gold" costs, training, evaluation, error analysis, limitations, artefact index |
| `CLAUDE.md` | **15,997** | 281 | The agent contract. Locked decisions, non-goals, the 34 GB disk constraint, architecture index, current state |
| `PROJECT.json` | **12,876** | | The machine-readable record the portfolio consumes. Metrics with sources, an `honest` block, decisions with reasons, repairs |
| `ENGINEERPROMPT.md` | 11,661 | | The original brief. ⚠️ Mode `600` |
| `DOCS-ENGINEERPROMPT.md` | 9,621 | | Documentation-pass scaffolding. ⚠️ Mode `600` |
| `AGENTS.md` · `GEMINI.md` | 3,829 each | 33 | The Aethereum room protocol. **Byte-identical to each other** and to the copies in every other Bruno repo |
| `NOTICE.md` | 1,898 | 37 | Third-party attributions, split out of `LICENSE` so GitHub would classify the repo as MIT rather than "Other" |
| `LICENSE` | 1,069 | | MIT |

Config at root: `pyproject.toml` (1,354 B), `uv.lock` (93 KB), `.gitignore`.

## `src/` - 25 modules, 544 KB, 4,363 lines

One module per pipeline stage, and the layering is the pipeline. Last modified 2026-08-15.

| Group | Modules | What they do |
|---|---|---|
| **Corpus** | `feeds.py`, `rss.py`, `harvest.py`, `store.py`, `gdelt.py` | 63 production feeds plus 83 same-outlet section feeds, async fetch, dedup on normalised URL. `gdelt.py` contributed **zero rows** and is kept on purpose |
| **Split** | `split.py` | Held-out **500** frozen on first run, disjointness asserted rather than assumed |
| **Teacher** | `teacher.py` (302 lines) | The Ollama client, JSON-schema-constrained decoding, parser guards |
| **Incumbent** | `regex_baseline.py` | A faithful port of the production `classifyWireItem()`, **six defects intact**, `re.ASCII` set so Python's Unicode-aware word boundary does not accidentally make it stronger than the real thing |
| **Contracts** | `schema.py`, `scoring.py` | Written and committed **before a single label existed**. Macro-F1 over all eight classes, ~60 lines from first principles |
| **Training prep** | `prepare_training.py` | `student_messages()`, the one shared prompt shape that both training and evaluation import |
| **Selection and merge** | `select_checkpoint.py`, `merge_student.py` | Selection never opens the held-out file, and records that it did not. Merge fuses then sanity-checks against the **merged** weights |
| **Evaluation** | `evaluate.py`, `error_analysis.py`, `measure_tokens.py`, `cost.py` | One harness, three arms. `cost.py` reads the measured token counts and raises if they are absent |
| **Provenance** | `record_run.py`, `stats.py`, `reproduce.py` | `reproduce.py` runs seven steps in dependency order and **deliberately never trains** |
| **Charts** | `charts.py`, `chart_labels.py`, `chart_corpus.py`, `chart_training.py`, `chart_confusion.py` | Five committed PNGs, generated from committed artefacts |

**Dead code:** none. **TODO markers:** none found in `src/` or `tests/`.

## `tests/` - 9 files, 248 KB, 1,014 lines

**90 test functions**, which the repo counts as **139 tests** after parametrisation. Largest by
count: `test_corpus.py` (17), `test_error_analysis.py` (15), `test_scoring.py` (12),
`test_regex_baseline.py` (11), `test_teacher.py` (11). See [[(Note) Test Suite]].

## `data/` - 12 files, 5.1 MB ⚠️ gitignored, no backup

`corpus.jsonl` (1.42 MB) · `train_pool.jsonl` (1.25 MB) · `train_labels.jsonl` (758 KB) ·
`heldout.jsonl` (197 KB) · `heldout_labels.jsonl` (118 KB) · `teacher_latency.jsonl` (43.5 KB) ·
`data/mlx/{train,valid,test}.jsonl` (592 KB, 30.8 KB, 97.4 KB) ·
`data/mlx_smoke/{train,valid,test}.jsonl`, the 20-example probe set.

**This directory is the project's irreplaceable asset.** See [[(Note) The Corpus and Splits]].

## `runs/` - 21 files, 49 MB, partly gitignored

| Path | Tracked | Contents |
|---|---|---|
| `runs/current/loss.jsonl` | ✅ | **199,535 bytes**, one point per step for 1,200 steps |
| `runs/current/train.log` | ✅ | **176,649 bytes** |
| `runs/current/hyperparams.json` | ✅ | Config, dataset SHA-256s, library versions, git commit, run facts |
| `runs/current/best/selection.json` | ✅ | The chosen iteration, the full ranking, and the statement that the held-out set was never read |
| `runs/current/best/adapter_config.json` | ✅ | |
| `runs/current/best/adapters.safetensors` | ⚠️ **ignored** | **3.67 MB. The shipped adapter. Only copy** |
| `runs/current/adapters/` | ⚠️ **ignored** | 6 checkpoints at 200 to 1200, plus final |
| `runs/interrupted-panic-20260815/` | ⚠️ **ignored** | The run that died at ~iteration 1,170 in a macOS GPU-driver kernel panic |

## `results/` - 11 files, 344 KB, all committed

`summary.json`, `summary_final_checkpoint.json`, `predictions.jsonl`,
`predictions_final_checkpoint.jsonl`, `corpus_stats.json`, `token_counts.json`,
`error_analysis.json`, `error_analysis.md`, `audit_50.md`, `audit_50_sample.json`,
`sanity_20.json`. **Every number in the README cites one of these.** See
[[(Note) Results Reference]].

## `charts/` - 5 PNGs, 488 KB, all committed

`label_distribution.png` (the hero) · `confusion_student.png` · `confusion_regex.png` ·
`class_distribution.png` · `training_curve.png`. See [[(Note) Charts and Artefacts]].

## `configs/` - 1 file

`lora.yaml`. Every value is copied into `runs/*/hyperparams.json` alongside the resolved
revision SHA, so a result produced from an unpinned model is impossible by construction.

## `assets/fonts/` - 6 files, 684 KB

Geist and Geist Mono, vendored under SIL OFL-1.1, used by the chart renderer. `LICENSE.txt`
included.

## `.github/` - 1 workflow

`ci.yml`, running on **`macos-14`** deliberately: MLX is a Metal library with no Linux wheel, so
an Ubuntu runner cannot even resolve the dependency set. It syncs the pinned environment, runs
pytest, and greps `src/` to assert the reserved amber `#FF9500` is never used outside its named
constant.

## Duplicate and dead flags

| Flag | Finding |
|---|---|
| Duplicate files | `AGENTS.md` and `GEMINI.md` are **byte-identical**, 3,829 bytes each. Deliberate, one per agent harness |
| Dead code | None. `src/gdelt.py` is inert but kept on purpose with the reason recorded |
| Empty directories | `models/` ⚠️ see [[(Note) The Deleted Student Weights]] |
| Untracked irreplaceable data | ⚠️ `data/` and the adapters. The remote does not have them |
| Stale documentation | **2**: `CLAUDE.md` and the README both say nothing is published and no remote exists. Both are false. See [[(Report) Gaps & Questions]] |

## Related

[[(Index) Complete File Inventory]] · [[(Report) Gaps & Questions]] · [[(Note) Source Tree]] ·
[[(Note) The Deleted Student Weights]] · [[(Report) Project Summary]] · [[(Map) Master Map]]
