---
id: 086406ce-76f3-41cf-b6bb-52bece9c1de4
title: "Test Suite"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/tests"
---

# Test Suite

**90 test functions across 9 files, 1,014 lines, which the repo counts as 139 tests after
parametrisation.** pytest, `testpaths = ["tests"]`, `pythonpath = ["."]`. **They all run today
with no model on disk**, which is the reason the repo is still verifiable.

| File | Functions | What it guards |
|---|---|---|
| `test_corpus.py` | **17** | Harvest, dedup on normalised URL, the split protocol, disjointness |
| `test_error_analysis.py` | **15** | The error taxonomy, head-to-head counts, the length and outlet breakdowns |
| `test_scoring.py` | **12** | ⚙️ **Policy.** Pins the macro-F1 averaging convention at **0.2708**, not the flattering **0.7222** that scikit-learn's default would report on the same fixture |
| `test_regex_baseline.py` | **11** | ⚙️ **Policy.** Reproduces **all six** incumbent defects, so a future "fix" to the production regex fails loudly here rather than silently changing the baseline |
| `test_teacher.py` | **11** | The Ollama client, JSON-schema-constrained decoding, the parser guards, and that unparseable output is never coerced |
| `test_cost.py` | 9 | The cost arithmetic, and that `cost.py` **raises** when `results/token_counts.json` is missing rather than falling back to a constant |
| `test_record_run.py` | 6 | The provenance block: dataset hashes, resolved revision, versions, git state |
| `test_chart_confusion.py` | 5 | Confusion-matrix rendering |
| `test_charts_guard.py` | 4 | ⚙️ **Policy.** Reads the **committed PNGs pixel by pixel** to prove the reserved amber `#FF9500` never appears in a rendered chart |

## The tests that are policy, not testing

Four of the nine files exist to stop a number from moving quietly.

**`test_regex_baseline.py`** is the clearest case. The incumbent's six defects are not bugs in
this repo, they are the thing being measured. If someone fixes `classifyWireItem()` in the
Sentinel backend and someone else re-syncs the port, the baseline would silently improve and
every published comparison would become wrong. **The test makes that impossible to do by
accident.**

**`test_scoring.py`** pins the averaging convention with a fixture where the two conventions
disagree by a factor of nearly three. That number is the difference between the incumbent
looking mediocre and the incumbent looking broken, and it is now checked on every push.

**`test_cost.py`** enforces that `cost.py` cannot fall back to a hardcoded constant. That guard
exists because four hardcoded constants **were** wrong, and the published headline moved from
45.4x to 41.3x when they were measured.

**`test_charts_guard.py`** reads image pixels. `pillow` is declared as a dev dependency
specifically so this guard cannot silently skip in CI, with a comment saying so, because a
skipped guard is the same as no guard.

## Quality signals

| Signal | Value |
|---|---|
| `TODO` / `FIXME` / `HACK` markers in `src/` and `tests/` | **0** |
| Tests requiring a model on disk | **0** |
| Tests requiring network | **0** |
| CI platform | `macos-14`, Apple silicon, deliberately |
| Extra CI gate | A grep asserting the reserved amber is only ever named |

## What the suite does not cover

- **No test loads a model.** That is a feature for portability and a gap for correctness: the
  `enable_thinking=False` behaviour that makes the student parseable at all is verified by the
  S5 probe and by the committed `results/sanity_20.json`, not by a test.
- **No end-to-end training test.** Training takes 64 minutes and 43.9 GB, which is not a CI job.
- **No variance testing.** One seed, one run. The repo says so, and recommends a second seed.

## Related

[[(Note) Evaluation and Scoring]] · [[(Note) Charts and Artefacts]] ·
[[(Note) CI and Publication]] · [[(Note) Source Tree]] · [[(Index) 80 Testing & Quality]]
