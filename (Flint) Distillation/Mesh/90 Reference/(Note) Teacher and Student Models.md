---
id: 1c5e8b60-d0f1-42fe-b6f6-fd6598e39508
title: "Teacher and Student Models"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/configs/lora.yaml"
---

# Teacher and Student Models

**A 35B open teacher, a 4B open student, both Apache-2.0, both run locally, both now deleted from
this machine.** The adapter that connects them survives.

## The teacher

| | |
|---|---|
| Model | **Qwen3.5-35B-A3B**, a mixture-of-experts model |
| Distribution | `hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M` |
| Served by | **Ollama**, locally, over HTTP |
| Licence | **Apache-2.0** |
| On-disk size | **22 GB**, not the budgeted 19 GB. Amendment **A2** |
| Decoding | JSON-schema-constrained, temperature 0, `num_ctx` pinned to **2048** |
| Latency | p50 **782 ms**, p95 **868 ms**, sequential and warm. Cold first call **19.6 s** |
| Quality score | **n/a by construction.** Gold is its own output |
| Estimated accuracy | **84%** strict agreement with a human, from the 50-headline hand audit |
| State on disk | ⚫ **deleted in S4**, by the project's own plan, to reclaim 21 GB. `~/.ollama` is now **12 KB** |

**Why an open teacher.** Training on a closed frontier model's output and then publishing the
resulting weights would breach its terms. An open teacher makes the deliverable clean, costs
**$0**, and needs no owner gate. That single decision is why the Hugging Face publication gate is
a **choice** rather than a legal problem.

**The `num_ctx` incident.** Ollama defaulted the teacher to a **32,768-token context** for
~250-token prompts, driving a 48 GB machine into **7.7 GB of swap** and taking free disk from
12 GB to 4 GB mid-run. Pinning `num_ctx: 2048` stopped it. **60 examples from before the change
were re-labelled to prove it altered no label**: 60 of 60 identical.

## The student

| | |
|---|---|
| Base model | **Qwen3.5-4B**, **4.21B** parameters |
| Distribution | `mlx-community/Qwen3.5-4B-bf16`, a bf16 conversion |
| Pinned revision | `491fdc7c087ba7fb48adcb1253f8e76d011db783` |
| Upstream | `Qwen/Qwen3.5-4B` at `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` |
| Licence | **Apache-2.0** |
| On-disk size | **~8 GB** base, **7.9 GB** merged |
| Fine-tune | **LoRA r=16 in bf16**, no QLoRA, on `q_proj` and `v_proj`, 16 of 32 layers |
| Trainable parameters | **0.918M**, **0.022%** of the total |
| Adapter size | **3,672,013 bytes**, 3.67 MB |
| Result | macro-F1 **0.8400**, accuracy **0.8540**, **0** unparseable in 500 |
| State on disk | ⚫ **base and merged weights deleted 2026-08-16.** ✅ **The adapter survives** |

**The pin is load-bearing.** `configs/lora.yaml` carries the revision SHA, and every value in it
is copied into `runs/*/hyperparams.json` at run time, **so a result produced from an unpinned
model is impossible**. `results/summary.json` independently records the base model, the revision,
and the adapter's SHA-256.

**`num_layers: 16` trains four layers, not sixteen.** `METHODOLOGY.md` has a section on exactly
that, and it is the kind of detail that silently invalidates a comparison if it is not written
down.

**The `<think>` block.** Qwen3.5-4B's chat template opens a `<think>` block at inference while
the training data carries a closed one. Without `enable_thinking=False` the adapter emits
"Thinking Process:" instead of a class and scores near zero. **The same adapter, with the flag,
scores 5 of 5 on the probe and 0 unparseable on all 500.** This is the single most important
operational fact about running this student.

## The prompts

| Arm | Prompt | Tokens measured |
|---|---|---|
| Teacher | Full class definitions, prompt version `v1` | **302.98** in, **6.51** out |
| Student | **Lean, ~32 tokens** | **35.98** in, **1.51** out |

**Amendment A3 reversed an earlier decision to hold the prompt constant.** The original reasoning
was backwards: a distilled student is supposed to **stop needing** the instructions, and making
it re-read 262 tokens of class definitions would have understated the distillation win in the one
place the project measures it. Both arms still see identical information and the identical
held-out 500, so quality is unaffected. It is worth the difference between **5.1x** and
**41.3x**.

## Where the weights are now

Nowhere on this machine. See [[(Note) The Deleted Student Weights]] for what a rebuild costs and
what still runs without them. Short version: the adapter is here, so restoring the merged model
is an **~8.5 GB download and minutes of compute**, not a training run.

## Related

[[(Note) The Deleted Student Weights]] · [[(Note) The Training Pipeline]] ·
[[(Note) Results Reference]] · [[(Note) External Services]] · [[(Index) 90 Reference]]
