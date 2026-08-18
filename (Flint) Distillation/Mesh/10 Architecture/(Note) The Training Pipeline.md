---
id: 2cdc5fe0-371e-4fc3-aed1-e87eccefef55
title: "The Training Pipeline"
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

# The Training Pipeline

**One LoRA run, 1,200 iterations, about 64 minutes, and the shipped weights are from iteration
800.** Everything is pinned: the base model by revision SHA, the datasets by SHA-256, the seed,
and the library versions, all copied into `runs/current/hyperparams.json` at run time so a
result produced from an unpinned model is impossible.

## The configuration

| Setting | Value | Why |
|---|---|---|
| Base model | `mlx-community/Qwen3.5-4B-bf16` | A bf16 conversion of `Qwen/Qwen3.5-4B`, Apache-2.0 |
| Revision | `491fdc7c087ba7fb48adcb1253f8e76d011db783` | Pinned. Upstream is `Qwen/Qwen3.5-4B` at `851bf6e8...` |
| Fine-tune type | `lora`, **not QLoRA** | At 4B in bf16 the memory is available on 48 GB unified, so QLoRA buys nothing, and Unsloth advises against it for Qwen3.5 due to quantization artifacts |
| Rank | **16** | Decision D9 |
| Target modules | `self_attn.q_proj`, `self_attn.v_proj` | |
| Scale | 20.0 · Dropout | 0.0 |
| `num_layers` | **16** of 32 | mlx-lm's default. The smoke probe reached a valid-class output on **8** layers with **20** examples, so this task does not need depth, it needs coverage |
| Batch size | 8 |
| Iterations | **1,200** | About **3.2 epochs** over 3,046 examples at 381 steps per epoch |
| Learning rate | `1e-5` · Optimizer | adamw |
| `max_seq_length` | 128 | Lean prompts render to ~32 tokens, so this is ample headroom |
| `mask_prompt` | **true** | Train on the answer only. Without it the model spends capacity learning to regenerate a system prompt it will always be given |
| `steps_per_report` | **1** | Every step's loss into `runs/current/loss.jsonl`. The first run's 25-step cadence gave 48 points for a 1,200-step curve, which is not a curve. Logging cadence only, it changes no training arithmetic |
| `steps_per_eval` | 100 · `val_batches` | 20 · `save_every` | 200 |
| Seed | `20260814` |

## What the run actually cost

| | Measured |
|---|---|
| Wall clock | **3,833.9 s**, about **64 minutes** |
| Throughput | median **0.313** iterations per second |
| Peak memory | **43.911 GB** unified. This needs the 48 GB machine |
| Trained tokens | **61,910** |
| Trainable parameters | **0.918M** of **4,205.75M**, which is **0.022%** |
| First train loss | 5.334 → final **0.196** |
| First validation loss | 5.604 → final **0.280**, minimum **0.075** |
| NaN report windows | **4**, at iterations 85, 100, 423 and 949. Recorded rather than hidden |
| Completed | ✅ true |

Provenance recorded alongside: Python 3.12.13, MLX 0.32.0, mlx-lm 0.31.3, mlx-metal 0.32.0,
transformers 5.15.0, numpy 2.5.2, on Darwin 25.5.0 arm64, at git commit `39333c7` with
`"dirty": true`.

## The checkpoint decision, worth +8.0 macro-F1 points

**mlx-lm's default is to hand you the final weights. The final weights were 8.0 macro-F1 points
worse.**

| Checkpoint | Validation loss | macro-F1 |
|---|---|---|
| **iteration 800** ✅ shipped | **0.075** | **0.8400** |
| iteration 600 | 0.077 | |
| iteration 200 | 0.080 | |
| iteration 400 | 0.093 | |
| iteration 1000 | 0.276 | |
| iteration 1200, mlx-lm's default | 0.280 | **0.7599** |

**The selection was made on the 160-example validation split alone.** `src/select_checkpoint.py`
never opens the held-out file, and `runs/current/best/selection.json` records that fact in
prose alongside the ranking. Choosing a checkpoint on the held-out set would leak it. **The guard
is that the module cannot read the test set, not that somebody remembered the rule.**

`selection.json` also lists **seven unselectable evaluations** where the validation loss was
recorded but no checkpoint was saved, including iteration 500 which tied the winner at 0.075.
`save_every: 200` is why. That is a genuine, documented cost of the config.

**The last 200 iterations were an optimisation excursion, not overfitting.** Validation loss went
0.075 to 0.280 **and mean training loss rose with it**, 0.072 to 0.26. Both moving together is
not the overfitting signature. **1,200 iterations was simply too many.**

And the unflattering evaluation is published: `results/summary_final_checkpoint.json` sits next
to `results/summary.json`, so a reader does not have to wonder what the other checkpoints looked
like.

## The training run that died

The first full run died at roughly **iteration 1,170 of 1,200** in a **macOS GPU-driver kernel
panic**, and took its stdout log with it.

It was **retrained from scratch** rather than resumed from a checkpoint, because resuming
restarts the iteration counter and yields a curve that cannot honestly be plotted. The second
run wrote its log inside the repo at `runs/current/train.log`, **176,649 bytes**.

The dead run's six checkpoints are still on disk at `runs/interrupted-panic-20260815/adapters/`,
gitignored like everything else under `adapters/`.

## The silent failure the probe caught

**S5 was a real gate, not a formality.** Qwen3.5-4B's chat template opens a `<think>` block at
inference while the training data carries a closed one, so the adapter returned "Thinking
Process:" for all five test cases and **0 of 5** predictions parsed. The obvious conclusion,
that the fine-tune had failed, would have been wrong.

`enable_thinking=False` reproduces the training prefix byte for byte, and **the same adapter then
scored 5 of 5**. That single flag is why the final student has **0 unparseable outputs in 500**.

## Related

[[(Note) System Architecture]] · [[(Note) Evaluation and Scoring]] ·
[[(Note) Teacher and Student Models]] · [[(Note) The Deleted Student Weights]] ·
[[(Note) Results Reference]] · [[(Index) 10 Architecture]]
