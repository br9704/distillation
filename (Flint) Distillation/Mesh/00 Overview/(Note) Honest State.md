---
id: 2826034c-7989-48c1-93a3-b1e1bb63f8ac
title: "Honest State"
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

# Honest State

**Verdict: 🟡 the science is finished and unusually well evidenced, but the two artefacts that
cannot be regenerated are sitting untracked on one Mac with no backup.** Health **amber**, and
the amber is entirely about storage rather than about the work.

S0 to S8 are closed, Sprint D is closed, the repo is public and CI is green. **S9 is open**, and
every remaining task in it is an owner gate.

## What is genuinely working 🚀

| | Evidence |
|---|---|
| The student works | macro-F1 **0.8400**, accuracy **0.8540**, **0** unparseable in 500 · `results/summary.json` |
| It beats the incumbent decisively | **0.3372** macro-F1 for the regex on the same 500. The student is right where the regex is wrong **285** times; the regex is right where the student is wrong **29** times |
| It wins all eight classes on F1 | Including `general`, 0.698 against 0.295 |
| Cost and latency both hold up | **41.3x** cheaper at list price, **2.4x** lower p50 latency than the teacher |
| Every number cites a file | The README's evidence table maps claim to artefact line by line. **11 files** under `results/`, all committed |
| Provenance is recorded | `results/summary.json` carries base model, pinned revision SHA, adapter SHA-256, held-out file hashes, git commit and a dirty flag |
| Checkpoint choice is auditable | `runs/current/best/selection.json` records the chosen iteration, the full ranking, **and** that the held-out set was never read by the selecting module |
| The unflattering result is published too | `results/summary_final_checkpoint.json`, the final-iteration evaluation at **0.7599**, sits next to the shipped **0.8400** |
| Tests | **90** functions, **139** after parametrisation, green in CI on `macos-14` |
| Git hygiene | Working tree clean, **0** unpushed, one branch, one remote |
| Repo is public | `github.com/br9704/distillation`, MIT, **10** topics |

## What is missing from disk ⚠️

**`models/student-merged/`, 7.9 GB, and the base HuggingFace weights were deleted on
2026-08-16** with Bruno's explicit authorisation. The repo went from **8.3 GB** to **484 MB**.
The trained adapter survived at **3.67 MB**. Full detail, including exactly what it would cost
to rebuild and what still runs, is in [[(Note) The Deleted Student Weights]].

Short version: restoring the merged model needs an **~8.5 GB download and minutes of compute**,
not a training run, because the adapter is still here. Most of the repo still works. No
published number depends on re-running anything.

## What is not backed up, and this is the real risk ⚠️

`.gitignore` excludes `*.safetensors`, `runs/*/adapters/` and all of `data/`. Verified with
`git status --ignored`.

| Artefact | Size | Copies that exist |
|---|---|---|
| The shipped LoRA adapter | 3.67 MB | **one**, on this Mac |
| The corpus, splits and all 3,706 labels | 5.1 MB | **one**, on this Mac |

**And the corpus cannot be re-harvested.** `.gitignore` claims `data/` is "regenerable from
`src/harvest.py`". The repo's own measurements say otherwise: one pass over the feeds yields
**~1,800** unique headlines, a second pass fifteen minutes later yields **7**, and GDELT
returns **429** on every request after the first. The README describes the corpus as "a snapshot
of August 2026 rather than a stable benchmark". **Feeds have moved on.**

Together those two files are **9 MB**. Backing them up is the cheapest high-value action
available in this project.

## Two documents that are now false 🟡

Both `CLAUDE.md` and the README's Status section say **"nothing is published"** and
**"no remote exists"**. Neither is true. Commit `86b43ee` records the public-repo gate as
approved and executed on 2026-08-15, `origin` is `https://github.com/br9704/distillation`, and
the working tree is clean with 0 unpushed. The stale lines were written before the gate and were
not updated after it, which is exactly the failure mode the repo's own rule about updating the
current-state line at every sprint close exists to prevent.

## What is open, and it is all owner-gated 🟡

| Gate | State |
|---|---|
| Push weights to Hugging Face | **⏭ Deferred** by Bruno on 2026-08-15. "We defer it", not declined, so it stays available. The masterplan recommends against publishing the **merged** weights regardless, and recommends the **adapter** repo instead |
| Make the repo public | **✅ Approved and executed**, 2026-08-15 |
| Publish the labelled dataset | **❓ Still open.** Explicitly not to be inferred from the Hugging Face deferral. Recommendation on file: keep it local |
| Optional paid ablation on a larger hosted teacher | **❓ Still open.** Would produce a teacher-strength curve for roughly $5 to $15. The repo's own recommendation is that **a second training seed is the better spend of the same effort**, because it costs nothing but local GPU time and closes the one gap a reviewer can legitimately attack |

`git-lfs` and `huggingface-cli` remain **deliberately uninstalled**, because installing them
would be preparing for a gate that may be declined.

## The limitations the project states about itself

These are printed in the README and in `METHODOLOGY.md`. They are boundaries, not oversights.

- **Gold labels come from a model.** The student's 85.4% measures **agreement with the teacher,
  not correctness**. The hand audit puts the teacher's own strict agreement with a human at
  **84%**, and that is the ceiling. The two numbers must not be read as the student beating the
  teacher.
- **The taxonomy has no `politics` class**, and that is an irreducible noise floor for every arm.
  US domestic politics fits neither `geopolitics` (relations between states) nor `general` (the
  catch-all), so any labeller wobbles. The student inherited it exactly as predicted: **53.4%**
  of its 73 errors involve `general`.
- **`consumer` is the weak class**, recall **0.529** against 0.86 to 0.94 for every well
  populated class. It is the smallest class at roughly **190** training examples, which is
  precisely the tail-class cost amendment **A1** predicted when the corpus target dropped from
  5,500 to 3,500.
- **One run, one seed, one machine, one 500-example draw.** No variance estimate. Treat the third
  decimal as noise.
- **Headline-only and English-only**, despite the corpus including DW, France24, NHK and SCMP.
- **Cost is list-price arithmetic over measured token counts**, not measured spend. Everything
  ran locally at **$0**. **41.3x** is the optimistic read; billed one parameter tier up it is
  **8.3x**, and both are published.

## The failures worth remembering

1. **A macOS GPU-driver kernel panic killed a training run at roughly iteration 1,170 of 1,200**
   and took its stdout log with it. Rather than resume from a checkpoint, which restarts the
   iteration counter and yields a curve that cannot honestly be plotted, it was **retrained from
   scratch** with the log written inside the repo. The dead run's checkpoints are still on disk
   at `runs/interrupted-panic-20260815/`.
2. **Ollama defaulted the teacher to a 32,768-token context** for ~250-token prompts, driving a
   48 GB machine into **7.7 GB of swap** and taking free disk from 12 GB to 4 GB mid-run. Pinning
   `num_ctx: 2048` stopped it, and **60 examples from before the change were re-labelled to prove
   it altered no label**: 60 of 60 identical.
3. **The S5 probe caught a silent failure that looked exactly like a failed fine-tune.**
   Qwen3.5-4B's chat template opens a `<think>` block at inference while the training data
   carries a closed one, so the adapter returned "Thinking Process:" for all five test cases.
   `enable_thinking=False` reproduces the training prefix byte for byte, and the same adapter
   then scored **5 of 5**.
4. **All four token constants in the cost model were wrong** when re-measured over the real 500
   held-out prompts. The published headline moved from **45.4x** to **41.3x**. `cost.py` now
   reads the artefact and raises if it is missing, so it cannot fall back to a constant.
5. **The Python port of the regex needed `re.ASCII` to be faithful.** JavaScript's word boundary
   is ASCII-based and Python's is Unicode-aware, so without the flag the incumbent arm would have
   been quietly **weaker** than the thing actually in production. Verified empirically on accented
   text, and the corpus includes DW, France24, SCMP and Haaretz.

## Honest one-line verdict

**A finished, public, unusually well evidenced piece of ML measurement whose single point of
failure is a 9 MB pair of gitignored files sitting on one laptop.**

## Related

[[(Note) The Deleted Student Weights]] · [[(Note) Results Reference]] · [[(Note) Git History]] ·
[[(Report) Gaps & Questions]] · [[(Note) Roadmap and Owner Gates]] · [[(Index) 00 Overview]]
