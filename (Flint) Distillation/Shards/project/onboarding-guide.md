---
id: 7930b98f-1123-428f-abd6-98a1567b0fcc
title: "onboarding-guide"
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
source_path: "/Users/brunojaamaa/Desktop/distillation"
---

# onboarding-guide

**Produce a briefing for someone who has never seen this project, in under an hour.**

## Say this first, before anything else

⚠️ **The model weights are gone and the surviving adapter has no backup.** Read
[[(Note) The Deleted Student Weights]] before running a single command. Never start a download or
a training run to "fix" it.

## The 25-minute path

1. [[(Report) Project Summary]] - the whole project on one page.
2. [[(Note) What Distillation Is]] - what was distilled from what, and why the incumbent regex is
   an arm rather than a footnote.
3. [[(Note) The Deleted Student Weights]] - what is missing, what a rebuild costs, what still
   runs.
4. [[(Note) Results Reference]] - every number, with its caveats attached.
5. [[(Note) Honest State]] - what is finished and what is at risk.

## Then, depending on what they are here to do

| They want to | Send them to |
|---|---|
| Understand the training run | [[(Note) The Training Pipeline]] |
| Argue about a metric | [[(Note) Evaluation and Scoring]], then `src/scoring.py`, which is ~60 lines |
| Understand the data | [[(Note) The Corpus and Splits]] |
| Find a file | [[(Note) Source Tree]] · [[(Index) Complete File Inventory]] |
| Run something | [[(Note) Install and Run]] · [[(Note) Command Surface]] |
| Argue with a decision | [[(Note) Locked Decisions and Amendments]] first |
| Know what is left | [[(Note) Roadmap and Owner Gates]] |

## Run this before reading more

```bash
cd /Users/brunojaamaa/Desktop/distillation
uv run python -m src.evaluate --skip-student    # the incumbent, end to end, no model needed
uv run python -m src.reproduce --dry-run        # see the pipeline without running it
```

Then open `charts/label_distribution.png`. The **74.2% `general`** column is the entire argument
in one picture.

## The six things that surprise people

1. **The incumbent is an arm**, ported with its six defects intact and each one pinned by a test.
   And the student **loses one class to it**, which the README says before it says anything else.
2. **The teacher has no quality score, on purpose.** Gold is its own output, so scoring it would
   read 100% by construction. The **84%** hand audit is reported instead.
3. **The metric was frozen before a single label existed**, in commit `6363455`. That timestamp is
   the proof.
4. **Macro-F1 is computed the hard way**, over all eight classes. scikit-learn's default would
   have read 0.7222 where this reads 0.2708.
5. **The shipped checkpoint is iteration 800, not 1200**, worth **+8.0** macro-F1 points, and the
   selecting module **cannot read the test set**.
6. **`enable_thinking=False` is why the student parses at all.** Without it the same adapter emits
   "Thinking Process:" and scores near zero.

## Hard rules to state up front

Read-only outside the vault. **Never run training, never download weights, never `uv sync`, never
`pip install`.** Never open `.env*` or any `mcp.json`. Never touch `runs/`, `data/` or `models/`.
**REPO WINS OVER NOTE.**

⚠️ And warn them: **`CLAUDE.md` and the README both say nothing is published and no remote
exists. Both are false.** See [[(Report) Gaps & Questions]].

## Related

[[(System) Flint Init]] · [[vault-audit]] · [[codebase-map-refresh]] · [[(Map) Master Map]]
