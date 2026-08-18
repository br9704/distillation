---
id: a7b3e596-517f-4c38-8159-7cb6a9ba6b13
title: "What Distillation Is"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/README.md"
---

# What Distillation Is

**A 4B student was distilled from a 35B teacher, to replace a keyword regex that is running in
production right now.** That last clause is what makes it a measurement rather than a demo.

## The thing being replaced

Sentinel is a live iOS news-intelligence product. Every headline it ingests is sorted into one
of **eight topic classes**, and the thing doing the sorting is `classifyWireItem()`, a keyword
regex in the production backend.

It is **structurally broken in ways visible in its own source**, not inferred:

- The `if` chain returns on first match, so `"Amazon Prime Day"` is `tech` rather than
  `consumer`, and `"SpaceX launch"` is `tech` rather than `science`.
- Any headline containing `china` is `geopolitics` forever.
- **The sixth defect nobody had noticed**: every keyword is a bare noun and the word boundary
  demands a non-word character after it, so `Russian` never matches `russia`, `Chinese` never
  matches `china`, `Israeli` never matches `israel`. Headlines use the adjectival form
  constantly, and every one of them lands in `general`.

It sends **74.2%** of the corpus to the `general` catch-all. It has **never once** emitted the
`consumer` class in 500 held-out headlines.

All six defects are reproduced in `src/regex_baseline.py` and **pinned by passing tests**, so a
future fix fails loudly rather than silently changing the baseline.

## The three arms

**The incumbent is an arm.** Benchmarking only against the teacher would have been choosing the
flattering baseline. And if the student loses to a keyword regex anywhere, that finding leads the
write-up rather than getting buried. It does lose one: `general` recall, 0.682 against 0.985.

**The teacher is open-weight**, `Qwen3.5-35B-A3B` at Q4_K_M through Ollama, Apache-2.0, run
locally. That is a licensing decision as much as a cost one: training on a closed frontier
model's output and then publishing the resulting weights would breach its terms. An open teacher
makes the deliverable clean, costs **$0**, and needs no owner gate.

**The student is `Qwen3.5-4B`**, LoRA fine-tuned in bf16 on MLX, pinned by revision SHA.

## The corpus carries zero credentials and zero user data

It is rebuilt from the same **63 public RSS feeds** the product reads, not read out of the
product's database. So there is no privacy disclosure attached to it and nothing was blocked
waiting for a key.

## What the deliverable actually is

**The trade-off curve, not parity.** If the student reaches most of the teacher's quality at a
fraction of the cost, that is the result. Tuning to close the last few points was explicitly out
of scope.

| Arm | macro-F1 | accuracy | p50 | p95 | cost per 1k requests |
|---|---|---|---|---|---|
| regex | **0.3372** | 0.3420 | 0.0 ms | 0.0 ms | **$0.0000** |
| student | **0.8400** | **0.8540** | **322 ms** | 403 ms | **$0.0037** |
| teacher | n/a | n/a | 782 ms | 868 ms | **$0.1547** |

## The one thing that shaped every sprint boundary

**34 GB of free disk**, not RAM. The naive ordering needs 37 GB: 19 GB teacher plus 8 GB base
plus 8 GB merged plus the environment. So the plan deletes the teacher **before** the student
base model is pulled, which is why teacher latency had to be measured while the weights were
still resident. It was, sequentially, one request at a time, over the same held-out 500, never
inferred from batched labelling throughput.

That constraint is the ancestor of the current state of the repo. See
[[(Note) The Deleted Student Weights]].

## Why this is a measurement and not a benchmark

Three properties, all of them decisions made before any number existed:

1. **The schema and the scorer were frozen before a single label existed.** `src/schema.py` and
   `src/scoring.py` were written, tested and committed in the sprint before the teacher was
   pulled. Choosing a metric after seeing its result is the easiest way to manufacture a
   favourable one.
2. **Macro-F1 averages over all eight classes**, not over classes present in the data.
   scikit-learn's default reads **0.7222** on the S1 fixture against this implementation's
   **0.2708**. A distilled small model silently dropping a tail class is exactly the failure this
   project exists to surface, so it must count as a zero.
3. **The teacher is never scored against its own labels.** Gold is the teacher, so "teacher
   accuracy" would read 100% by construction. The **84%** hand audit is reported instead.

## Related

[[(Note) Honest State]] · [[(Note) Teacher and Student Models]] ·
[[(Note) Evaluation and Scoring]] · [[(Note) The Corpus and Splits]] ·
[[(Note) Results Reference]] · [[(Index) 00 Overview]]
