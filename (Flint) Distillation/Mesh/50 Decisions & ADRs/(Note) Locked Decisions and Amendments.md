---
id: 881b273f-adc3-4783-a2a8-f09c383bdd9b
title: "Locked Decisions and Amendments"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/masterplan.md"
---

# Locked Decisions and Amendments

**Eleven locked decisions and an append-only amendments section.** The rule is stated in the
masterplan: every material change to a locked decision lands in `AMENDMENTS` with a date and a
why, and historical entries are never edited.

## The decisions that make it a measurement

### Three arms, not two

**Why.** The regex is the actual incumbent in production. Benchmarking only against the teacher
would have been choosing the flattering baseline, **and if the student loses to a keyword regex
anywhere, that is the finding and it leads.** It does lose one: `general` recall, 0.682 against
0.985, and the README says so before it says anything else about the student.

### The schema and the scorer were frozen before a single label existed

**Why.** Choosing a metric after seeing its result is the easiest way to manufacture a favourable
one. Both were written, tested and committed in **S1**, commit `6363455`, the sprint before the
teacher was pulled. The timestamp is the proof.

### Macro-F1 over all eight classes, not over classes present in the data

**Why.** scikit-learn's default silently forgives a class the model never learned, reading
**0.7222** against this implementation's **0.2708** on the same fixture. A distilled small model
dropping a tail class entirely is precisely the failure this project exists to surface, so it
must count as a **zero**. Written from first principles in ~60 lines specifically so the choice is
visible in the repo.

### The teacher arm is never scored against its own labels

**Why.** Gold is the teacher, so "teacher accuracy" would read **100% by construction**.
Reporting a constructed 100% next to a real student number would be **the single most misleading
thing this project could publish**. The **84%** hand audit is reported instead.

### Unparseable teacher outputs are marked and reported, never coerced to `general`

**Why.** Coercing them would bias the teacher toward the majority class and corrupt the very
ceiling everything downstream is measured against. **The scorer raises if it ever sees one**, so
the rule is enforced by code rather than documented.

### Ship the best-validation checkpoint, chosen on the validation split alone

**Why.** The final iteration was **8.0 macro-F1 points worse**. Choosing on the held-out set
would leak it, so `src/select_checkpoint.py` **never opens that file** and records the fact, the
ranking and the chosen iteration in `runs/current/best/selection.json`. **The guard is that the
module cannot read the test set, not that nobody remembered the rule.**

### Publish the final-checkpoint evaluation next to the shipped one

**Why.** Reporting only the checkpoint selected for being best invites the reader to wonder what
the others looked like. `results/summary_final_checkpoint.json` answers it.

## The decisions about licensing and cost

### Open-weight teacher only, run locally

`Qwen3.5-35B-A3B`, Apache-2.0. **Why.** Training on a closed frontier model's output and then
publishing the resulting weights would breach its terms. An open teacher makes the headline
deliverable clean, costs **$0**, and needs no owner gate.

### The corpus is rebuilt from public RSS with zero credentials and zero user data

**Why.** It reproduces the production distribution without touching the product's database or any
user-generated content, so there is no privacy disclosure attached and nothing blocks waiting for
a key.

## The decisions about the machine

### MLX for training, LoRA r=16 in bf16, no QLoRA

**Why.** Unsloth and bitsandbytes are CUDA-only and this is an M4 Pro. TRL and peft on MPS are
slow and flaky. At 4B in bf16 the memory is available on 48 GB unified, so **QLoRA buys nothing**,
and Unsloth advises against it for Qwen3.5 due to quantization artifacts.

### Held-out membership is frozen on the first split

**Why.** A background harvester that keeps adding rows can never leak into the evaluation set.
**Impossible by construction instead of by remembering the rule.**

## The four amendments

| Amendment | Date | What changed |
|---|---|---|
| **A1** | 2026-08-14 | **Corpus target lowered from ≥5,500 to ≥3,500.** Measurement killed the volume plan: a first pass yields ~1,800 unique, a second fifteen minutes later yields **7**. Breadth was exploited to +1,890 rows via 83 section feeds; GDELT was unusable. Landed at **3,706**. **Cost stated plainly at the time: a smaller distillation set means a slightly weaker student, particularly on the tail classes.** It landed exactly there, `consumer` at 0.529 recall |
| **A2** | 2026-08-14 | **Teacher on-disk size is 22 GB, not the budgeted 19 GB.** Leaves ~9 GB free rather than ~13 GB during S3 and S4. Two available options were **not** taken: dropping to Q3_K_M would degrade the teacher, and the teacher is the ceiling for everything; and deleting Bruno's two pre-existing Ollama models would free plenty, **but this project does not delete a user's models to make room for itself** |
| **A3** | 2026-08-15 | **The student gets a lean 32-token prompt, reversing the S5 decision.** The original reasoning was backwards: a distilled student is supposed to **stop needing** the instructions, and making it re-read 262 tokens of class definitions would have understated the distillation win in the one place the project measures it. Both arms still see identical information and the identical held-out 500, so quality is unaffected. Worth the difference between **5.1x** and **41.3x** |
| **A8-equivalent, Sprint D** | 2026-08-15 | **All four token constants in `cost.py` were wrong** when re-measured over the real 500 prompts. Student input understated at 32 against **35.98**, teacher output overstated at 10 against **6.51**. Published headline moved **45.4x → 41.3x**. `cost.py` now reads the artefact and **raises if it is missing** |

## Non-goals, stated as hard boundaries

Parity with the teacher. Tuning to close the last few points. Article bodies. Non-English. A
production deployment. The deliverable is **the trade-off curve**, and that was fixed before any
number existed.

## Related

[[(Note) What Distillation Is]] · [[(Note) The Training Pipeline]] ·
[[(Note) Evaluation and Scoring]] · [[(Note) The Corpus and Splits]] ·
[[(Note) Git History]] · [[(Index) 50 Decisions & ADRs]]
