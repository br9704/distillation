---
id: a063110e-6eda-4bcd-90e2-8111b638bf9d
title: "The Corpus and Splits"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/data"
---

# The Corpus and Splits

**3,706 labelled headlines from 54 outlets, harvested from public RSS in August 2026, carrying
zero credentials and zero user data.** ⚠️ It is **5.1 MB, gitignored, and cannot be
re-harvested.**

## The numbers

| | |
|---|---|
| Harvested rows | **3,812** |
| Split and labelled | **3,706** |
| Unused late arrivals | 106 |
| Outlets | **54** |
| Production feeds | **63**, plus **83** committed `EXPANSION_FEEDS` |
| Train pool | **3,206** |
| Held out | **500**, frozen on first split |
| MLX train / valid / test | **3,046** / **160** / **500** |
| Unparseable teacher labels | **0**, a rate of **0.00%** |
| Smallest held-out class | **34** (`consumer`) |
| Teacher model | `hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M`, prompt version `v1` |

## The distribution, which is the argument

On the 3,206-row training pool:

| Class | Teacher | Incumbent regex |
|---|---|---|
| geopolitics | 563 | 197 |
| finance | 359 | 125 |
| tech | 356 | 241 |
| sports | 364 | 91 |
| entertainment | 410 | 67 |
| science | 537 | 105 |
| **consumer** | **191** | **6** |
| **general** | **426** (13.3%) | **2,374 (74%)** |

**The regex sends 74.2% of everything to the catch-all** and has produced the `consumer` class
**six times in 3,206 rows**. That single table is the project's case, and
`charts/label_distribution.png` is it as a picture.

## Why the corpus is 3,706 and not 5,500

**Amendment A1.** The 5,500 target was set during planning on an estimate of 61 feeds times ~35
items times repeat passes. Measurement changed the picture:

- **A first pass yields ~1,800 unique headlines.**
- **A second pass fifteen minutes later yields 7**, because RSS carries a rolling window that has
  not moved.
- Volume therefore comes from **breadth** or from **hours**, never from more passes.

Breadth was exploited as far as it honestly could be: `EXPANSION_FEEDS` added **83** live section
feeds from outlets already in the catalog, worth **+1,890** rows. The remaining lever was GDELT,
which turned out unusable, and the alternative was spending several more hours harvesting toward
a target the repo had set for itself rather than one the brief set.

**What this cost, stated by the project itself:** roughly 3,200 training examples rather than
5,000 is a smaller distillation set, and the honest expectation was a slightly weaker student,
particularly on the tail classes. **It landed exactly there.** `consumer`, the smallest class at
roughly 190 training examples, recalls **0.529** against 0.86 to 0.94 for every well-populated
class.

## The split protocol, and why it cannot leak

**Held-out membership is frozen on the first split rather than re-drawn.** A background harvester
kept adding rows opportunistically, and every one of them goes to the training pool by
construction. **The evaluation set cannot be contaminated by growth**, and that is enforced by
the code rather than by remembering the rule. Disjointness is asserted, not assumed.

Each MLX file's SHA-256 is recorded in `runs/current/hyperparams.json`, and
`results/summary.json` records the held-out file hashes independently, so an evaluation traced
back to the wrong split is detectable.

## ⚠️ It cannot be re-harvested

`.gitignore` says `data/` is "regenerable from `src/harvest.py` + `src/gdelt.py`, and large".
**The first half of that is wrong**, and the repo's own measurements prove it:

- Feeds do not refill within a session.
- **GDELT is unusable on this network**: one request succeeds, then every subsequent request
  returns **429** regardless of spacing, verified at **20 s** and at **65 s**, contributing
  **zero rows over 20 minutes**. `src/gdelt.py` is kept anyway, because the code is correct and
  the failure is a rate-limit penalty box rather than a bug.
- The README states plainly that "feeds move, so the corpus is a snapshot of August 2026 rather
  than a stable benchmark".

**Two days have passed. The window has moved.** Re-running `src.harvest` today would produce a
different corpus, and any number computed on it would not be comparable to the published ones.

## What that means

`data/` is **5.1 MB of irreplaceable material** with exactly one copy, on one laptop, excluded
from git. Backing it up costs nothing. See [[(Note) The Deleted Student Weights]] for the same
problem applied to the adapter, and [[(Report) Gaps & Questions]] for the gap row.

## Privacy posture

**Zero credentials, zero user data.** The corpus is rebuilt from the same public feeds the
product reads, not read out of the product's database and not touching any user-generated
content. There is therefore no privacy disclosure attached to it, and the open owner gate about
publishing the dataset is genuinely a **choice** rather than a constraint.

## Related

[[(Note) The Deleted Student Weights]] · [[(Note) Evaluation and Scoring]] ·
[[(Note) What Distillation Is]] · [[(Note) External Services]] ·
[[(Index) 40 Data & Integrations]]
