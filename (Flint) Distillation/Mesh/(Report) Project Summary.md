---
id: 359c3bd6-6931-45d8-8ec5-c9604f75ba71
title: "distillation — Project Summary"
type: project-summary
project: "Distillation"
kind: research
stack: "Python 3.12 · MLX · mlx-lm · LoRA · Qwen3.5 · Ollama · pydantic · matplotlib · pytest · uv"
status: shipped
health: amber
health_note: "the science is finished, public and fully backed by committed artefacts, but the merged student weights and the base model were deleted on 2026-08-16, and the surviving adapter and corpus are gitignored so local disk is their only copy"
last_commit: "2026-08-15"
last_commit_note: "a8a52d1 · docs: link the case study on brunojaamaa.dev"
path: "/Users/brunojaamaa/Desktop/distillation"
live_url: "https://github.com/br9704/distillation"
repo: "https://github.com/br9704/distillation"
cluster: "personal"
tags:
  - "#report"
  - "#project"
  - "#ld/living"
  - "#stack/python"
  - "#status/shipped"
  - "#cluster/personal"
created: "2026-08-17"
updated: "2026-08-17"
source_path: "/Users/brunojaamaa/Desktop/distillation"
---

# distillation — Project Summary

**A 4B LoRA student was distilled from a 35B open teacher, to replace a keyword regex that is
live in production.** Three arms were measured on the same 500 headlines held out before a
single label existed: the incumbent regex, the teacher, and the student.

🚀 **shipped** in **two days**, 2026-08-14 to 2026-08-15, **19 commits**, repo public. The
science is done and every published number cites a committed artefact.

## The headline result

| Arm | macro-F1 | accuracy | p50 latency | unparseable |
|---|---|---|---|---|
| Incumbent regex | **0.3372** | 0.3420 | 0.0 ms | 0 |
| **Student**, Qwen3.5-4B + LoRA | **0.8400** | **0.8540** | **322 ms** | **0 of 500** |
| Teacher, Qwen3.5-35B-A3B | n/a by construction | n/a | 782 ms | 0 |

The student reproduces its teacher's judgement on **85.4%** of held-out headlines at **2.42%**
of the list cost, **41.3x cheaper**, and **2.4x lower latency**. It wins all eight classes on
F1 and loses exactly one on recall.

**The teacher has no quality score on purpose.** Gold is the teacher's own output, so scoring
it against itself would read 100% by construction. The hand audit's **84%** strict agreement
with a human is reported instead, and that is the ceiling on everything.

## ⚠️ What is missing from disk

**`models/student-merged/`, 7.9 GB, was deleted on 2026-08-16** with Bruno's authorisation
during a storage migration, and the base HuggingFace weights went with it. The `models/`
directory is now empty and `~/.cache/huggingface/hub` does not exist.

**The trained LoRA adapter survives**: `runs/current/best/adapters.safetensors`, **3.67 MB**,
with the SHA-256 that `results/summary.json` records. Rebuilding the merged model therefore
needs an **~8.5 GB re-download and a few minutes of compute**, not a re-training run. A
re-training run is only required if the adapter is also lost, and it would take about **64
minutes** on this machine. Read [[(Note) The Deleted Student Weights]] before doing anything.

**The repo still runs, mostly.** Tests, the regex arm, statistics, cost arithmetic and all five
charts regenerate with no model on disk. Nothing that loads the student or calls the teacher
works. **No published number depends on re-running anything**, because every result is
committed under `results/`.

## Key numbers

| | |
|---|---|
| Commits | **19**, 2026-08-14 to 2026-08-15. **0** tags |
| Tracked files | **85** · **124** on disk outside `.git`, `.venv` and caches |
| On disk | **484 MB**, of which `.venv` is **380 MB** and `runs/` is **49 MB** |
| Source | **4,363** lines across **25** Python modules |
| Tests | **90** test functions across **9** files, which the repo counts as **139** after parametrisation |
| Corpus | **3,706** labelled headlines from **54** outlets and **63** production feeds |
| Split | **3,206** train pool · **500** held out, frozen on first run |
| Unparseable outputs | **0.00%**, across 3,706 teacher labels and 500 student predictions |
| Training | **1,200** iterations, **~64 minutes**, peak **43.9 GB** unified memory, **0.918M** trainable parameters, **0.022%** of 4.21B |
| Shipped checkpoint | iteration **800**, not the final 1,200. Worth **+8.0** macro-F1 points |
| Working tree | ✅ clean · **0** unpushed |

## Top risks

1. ⚠️ **The only copy of the trained adapter is an untracked local file.** `*.safetensors` and
   `runs/*/adapters/` are gitignored, so `runs/current/best/adapters.safetensors` exists on this
   Mac and nowhere else. The GitHub remote does not have it. Losing it means a re-training run.
2. ⚠️ **The only copy of the corpus is also untracked.** All of `data/` is gitignored, **5.1 MB**
   on local disk. The `.gitignore` calls it "regenerable from `src/harvest.py`", and the repo's
   own measurements say otherwise: RSS feeds do not refill, a second pass fifteen minutes later
   yields **7** rows, and GDELT returns 429 on every request after the first. **The corpus is a
   snapshot of August 2026 and cannot be re-harvested.**
3. 🟡 **Two owner gates are open.** Publishing the labelled dataset, and an optional paid
   ablation on a larger hosted teacher. The Hugging Face push was **deferred**, not declined.
4. 🟡 **`CLAUDE.md` and the README both say "nothing is published" and "no remote exists".**
   Both are false: commit `86b43ee` records the public-repo gate as approved and executed, and
   `origin` is `br9704/distillation`.
5. **One run, one seed, one machine, one 500-example draw.** There is no variance estimate on
   0.840. The repo says so plainly and recommends a second seed as the best next spend.

## Next 5 actions

- [ ] Back up `runs/current/best/adapters.safetensors` and `data/` off this machine. They are the two artefacts the remote does not have #task [project:: Distillation] [priority:: high] ^t-db0tumxq
- [ ] Correct `CLAUDE.md` and the README's Status section, which still claim nothing is published and no remote exists #task [project:: Distillation] [priority:: high] ^t-e1p2yxtt
- [ ] Answer the two open owner gates: publish the labelled dataset or keep it local, and whether to run the paid teacher-strength ablation #task [project:: Distillation] ^t-9zpmxnse
- [ ] Run a second training seed. It costs local GPU time only and closes the single-sample limitation, which is the one gap a reviewer can legitimately attack #task [project:: Distillation] ^t-ri9bwb36
- [ ] Take the six regex defects and the missing `politics` class back to the Sentinel product as actionable work #task [project:: Distillation] [priority:: high] ^t-5zqv45ew

## The ten links that matter

[[(Map) Master Map]] · [[(Note) The Deleted Student Weights]] ·
[[(Note) What Distillation Is]] · [[(Note) Honest State]] · [[(Note) Results Reference]] ·
[[(Note) The Training Pipeline]] · [[(Note) Evaluation and Scoring]] ·
[[(Note) The Corpus and Splits]] · [[(Note) Teacher and Student Models]] ·
[[(Report) Gaps & Questions]]

## Related

[[(Guide) BRUNO HQ]] · [[(Map) BRUNO HQ]] · [[(System) Flint Init]] ·
[[(Report) Folder Audit]] · [[(Report) Build Log]]
