---
id: fe9da501-59b0-47ca-98d8-b5a3e2562133
title: "Evaluation and Scoring"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/src/scoring.py"
---

# Evaluation and Scoring

**One harness, three arms, one held-out set of 500 that was frozen before a single label
existed.** `src/evaluate.py` runs all three so no arm can get a different measurement path.

## Macro-F1 over all eight classes, computed the hard way

The scorer is roughly **60 lines written from first principles**, specifically so the averaging
choice is visible in the repo rather than inherited from a library default.

**scikit-learn's default silently forgives a class the model never learned.** On the S1 fixture
it reads **0.7222** against this implementation's **0.2708**. A distilled small model dropping a
tail class entirely is precisely the failure this project exists to surface, so it must count as
a **zero**.

That choice is worth exactly the difference between the incumbent looking mediocre and the
incumbent looking broken. The regex scores `consumer` at **0.000 F1 on 34 held-out examples**,
because the rule never fires once: `amazon` is matched by the `tech` branch above it.

## The teacher is never scored

**Gold is the teacher's own output**, so a "teacher accuracy" figure would read 100% by
construction. Publishing a constructed 100% next to a real student number would be the single
most misleading thing this project could do.

What is reported instead: **84% strict agreement** with a human adjudicator, from a hand audit of
50 headlines recorded in `results/audit_50.md` **before any student existed**. Excluding
genuinely ambiguous cases it is **93%**. Neither is rounded up, and the 84% is the ceiling on
everything downstream.

The eval harness prints `n/a` for the teacher's quality columns and a line explaining why.

## Unparseable outputs are marked, never coerced

Silently coercing an unparseable teacher output to `general` would bias the teacher toward the
majority class and corrupt the ceiling everything else is measured against. **The scorer raises
if it ever sees one**, so the rule is enforced by code rather than documented.

It never fired: **0.00% unparseable** across 3,706 teacher labels and 500 student predictions.

## The split protocol

**Held-out membership is frozen on the first split rather than re-drawn.** A background harvester
that keeps adding rows can therefore never leak into the evaluation set. Every row added after
the first split goes to the training pool by construction. Disjointness is **asserted**, not
assumed.

| Split | Rows |
|---|---|
| Corpus harvested | 3,812 |
| Split and labelled | **3,706** |
| Unused late arrivals | 106 |
| Train pool | **3,206** |
| Held out | **500** |
| MLX train / valid / test | **3,046** / **160** / **500** |

Each MLX file's SHA-256 is recorded in `runs/current/hyperparams.json`.

## Latency is measured, cost is arithmetic

**Latency** is measured by this repo's own monotonic timer around single sequential requests,
warm, with warm-up calls discarded. A cold first call costs **19.6 s** against ~800 ms warm, and
including that in p95 would measure the cost of starting a server rather than of serving a
request.

**Cost is list-price arithmetic over measured token counts**, and the code says so. Every arm ran
locally at **$0**.

## Reproducibility of the labels, evidenced three ways

1. **100 of 100** unanimous at temperature 0.
2. **60 of 60** identical across the mid-run `num_ctx` configuration change, which is how the
   Ollama swap incident was proven to have altered no label.
3. **500 of 500** on an independent re-prediction of the whole held-out set.

At temperature 0.7 the teacher disagrees with itself on **14 of 100** headlines, and every
disagreement inspected was genuine multi-label ambiguity rather than noise. That is a soft
ceiling on every arm.

## Error analysis

`src/error_analysis.py` writes `results/error_analysis.json` and a readable
`results/error_analysis.md`: a taxonomy by cause, head to head, and breakdowns by headline length
and outlet volume.

| Finding | Value |
|---|---|
| Student errors involving the `general` catch-all | **53.4%** of 73 errors |
| Student right where the regex is wrong | **285** |
| Regex right where the student is wrong | **29** |
| Regex-`general` held-out headlines the teacher reassigns | **310 of 375**, **82.7%** |

The `general` concentration was **predicted before a student existed**, by the S4 hand audit
identifying that the taxonomy has no `politics` class.

## Related

[[(Note) Results Reference]] · [[(Note) The Training Pipeline]] ·
[[(Note) The Corpus and Splits]] · [[(Note) What Distillation Is]] ·
[[(Note) Test Suite]] · [[(Index) 10 Architecture]]
