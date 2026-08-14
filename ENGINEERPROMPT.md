# Engineer Prompt — Frontier→Small Model Distillation
# Day 3 of the AI-engineering portfolio sprint. Competency demonstrated: **actual ML** (training, not inference).

> **Tooling note:** data prep + writeup suit Cowork; the training script suits Claude Code. Run the phases in whichever surface fits — the phase boundaries below are designed for that split.

---

## The objective

Take one narrow task currently served by a frontier model. Generate ~3,000–5,000 labels with that model. LoRA fine-tune a small (~3B) open model on them. Prove the small model gets close to frontier quality at a fraction of cost and latency — and show exactly where it fails.

**The headline you're aiming for:**
> *"94% of baseline quality at 3% of the cost, p95 latency 340ms vs 2100ms."*

This is the project that moves the portfolio from "builds with LLM APIs" to "understands the model layer" — the line most AI-engineering candidates never cross. It is also the most commercially legible of the three: *"cut inference cost 30× on a production feature"* is a sentence a hiring manager converts directly into budget.

---

## READ FIRST: the legal trap that shapes the whole project

The deliverable includes **public model weights on Hugging Face**. That collides with frontier-model terms of service, and this is not hypothetical — it's in the contracts:

- **Anthropic Commercial Terms §D.4:** customers "may not… access the Services to build a competing product or service, **including to train competing AI models**." No classifier carve-out.
- **OpenAI Services Agreement §3.3(e):** bans using output to develop competing models, **except** models "primarily intended to categorize, classify, or organize data (e.g., embeddings or classifiers), **if these models are not distributed or made commercially available to third parties**." Publishing weights to HF **is** distribution — so the exception does not cover the headline deliverable.
- **Google Gemini API Terms:** "You may not use the Services to develop models that compete with the Services." Free and paid tiers alike.

**Therefore — the recommended path, and it costs you nothing:**

> **Use an open-weight teacher.** Qwen (Apache 2.0), DeepSeek (MIT), or similar impose no restriction on training from their outputs. The cost story survives completely intact: a large open model served via API is still 20–50× the price of a 3B, and you get a *cleanly publishable* artifact.

If Bruno insists on a closed frontier teacher, the fallback options — in descending order of safety — are: (a) publish evals + code but keep weights private/gated; (b) argue a single-task classifier doesn't "compete" (plausible, untested, **risk acceptance not compliance**); (c) at absolute minimum, disclose the labeling source in the model card. **`ask_human` on this before generating a single label.** It determines the teacher, the budget, and whether the headline deliverable exists.

---

## Phase 0 — Lock the task (first hour, hard deadline)

**Task selection is the whole ball game.** Get it wrong and the day is gone.

**Primary candidate — Sentinel** (live AI news intelligence iOS app, real corpus, real classification/summarisation already running). Real data from a real product beats every synthetic dataset in the portfolio pile.

Pick the **narrowest possible sub-task**: topic tagging · significance/newsworthiness scoring · entity extraction.

**Fallback — Poke AI** (card recognition). Arguably *better*: vision evals are rarer than text evals in portfolios, and if there's user-correction data from real scans, that's a labelled dataset almost nobody else can obtain.

**The selection rule, non-negotiable:** distil something with a **crisp right answer**. Classification, extraction, or scoring on a fixed scale. If it can't be scored automatically against ground truth, it is the wrong task. Do NOT distil "summarise this article well" — open-ended generation does not distil cleanly at 3B on 5k examples, there's no crisp metric, and it will eat the entire day.

- [ ] Decide within the first hour. Do not spend half the day cleaning data.
- [ ] Write the task definition + label schema + scoring function BEFORE labelling anything.

---

## Phase 1 — Data (budget ~60% of the time; this is where the day actually goes)

- [ ] Assemble the source corpus from the product's real data
- [ ] Label 3,000–5,000 examples with the teacher. **Use the batch API** — roughly half price. Budget check: 5,000 × (~1,000 in + 60 out) tokens ≈ **$6–14** depending on teacher. Labelling is cheap; don't over-engineer around cost here.
- [ ] Hold out **~500 examples, never seen in training.** Split before any labelling round so there's no leakage.
- [ ] Sanity-audit ~50 teacher labels by hand. The teacher is your ceiling — if it's noisy at 8%, the student can't beat that, and you need to know before you interpret results.
- [ ] Commit the data pipeline. Commit label distributions (a class-imbalance chart costs nothing and pre-empts an obvious reviewer question).

## Phase 2 — Train (~20%)

| Item | Recommendation (verified Aug 2026) |
|---|---|
| Base model | **`Qwen/Qwen3.5-4B`** (Apache 2.0, 262K ctx) — the strongest small open model as of now. Latency-optimised alternative: `google/gemma-4-E2B-it` (Gemma 4 switched to **Apache 2.0**). Other Apache options: `mistralai/Ministral-3-3B-Instruct-2512`, `HuggingFaceTB/SmolLM3-3B`. |
| Avoid | Llama 3.2 3B (two generations stale, license friction). **Torchtune is dead** (maintenance-only since Jul 2025) — don't use it. |
| Method | **LoRA, bf16, r=16.** Note: Unsloth explicitly recommends *against* QLoRA for Qwen3.5 (quantization artifacts) — and at 4B/bf16 you only need ~10GB VRAM, so QLoRA buys nothing. |
| Framework | **Unsloth** (fastest, lowest VRAM) or **TRL** — note TRL hit **v1.0 in Apr 2026**, so most tutorials online use the old API. Current is v1.10.x; `SFTConfig` now inherits from `TrainingArguments`. |
| Compute | **Modal** ($2.50/h A100-80GB, per-second billing, **$30/mo free credit covers the whole run**). Cheaper raw: RunPod L40S $0.99/h. |
| Runtime | 5,000 × ~500 tok × 3 epochs ≈ 7.5M training tokens → **~15–25 min on A100/H100**. One hour maximum, as the brief says. |
| Alternative path | Managed LoRA (Together $0.48/M, Fireworks $0.50/M training tokens) ≈ **$3.60–3.75** total. Both let you download the adapter. Simpler, barely cheaper — take it if GPU wrangling is eating time. |

- [ ] Save and commit the **training curve** — it's a deliverable, and a missing loss curve is the first thing a reviewer notices.
- [ ] Log hyperparameters and the exact base-model revision.

## Phase 3 — Evaluate (~20%) — this is what separates a training script from an evaluation

Report all three, **both arms**:

1. **Quality** — accuracy / macro-F1 on the held-out 500, student vs teacher baseline
2. **Cost** — per 1,000 requests, both ways, **with the arithmetic shown** (not asserted)
3. **Latency** — **p50 and p95**, both ways, measured by you with the same harness. Published p95s for frontier models are unreliable; measure them.

**Cost arithmetic that makes the headline honest** (a 1,000-in / 50-out classification call):
- Frontier mid-tier teacher (Sonnet-class, $2/$10 per M): **$0.0025/call**
- Student on serverless <4B (Fireworks $0.10/M flat): **$0.000105/call** → **4.2% of teacher cost**
- Against a flagship ($5/$25): ~1.6%

> **Pin the baseline to the model actually used in production**, not the cheapest frontier option. Against a cheap small frontier model (Gemini Flash-Lite, GPT-5.6-luna) the student is only ~2.5× cheaper and the story collapses. State which baseline you chose and why — a reviewer will check this, and choosing the flattering baseline silently is the credibility failure mode.

**Error analysis — the part most people skip:**
- [ ] Break failures down by category. Confusion matrix or an error taxonomy.
- [ ] Answer *where and why* the small model loses, in prose. "It confuses `policy` and `regulation` on short articles" is worth more than any aggregate number.

---

## The two traps

1. **Do not distil the whole task.** Covered in Phase 0. If it can't be auto-scored, it's wrong.
2. **Do not chase parity.** The interesting result is the **trade-off curve**, not a tie. 94% quality at 3% cost is a *better* story than 100% parity — more believable, and more useful to anyone making a build decision. If you find yourself tuning to close the last 4 points, stop and write up the curve instead.

## Non-goals (hard boundaries)

No full fine-tune (LoRA only) · no multi-task model (one narrow task) · no serving infrastructure or deployment (measurement is enough) · no RLHF/DPO/preference alignment (supervised distillation only) · do not try to beat the teacher.

## Deliverables — done when

- [ ] Task selected and locked within the first hour
- [ ] 3,000+ labelled training examples, 500 held out and never trained on
- [ ] LoRA fine-tune completed, training curve saved and committed
- [ ] Quality, cost, latency reported for both arms
- [ ] Error analysis with breakdown by category
- [ ] Weights on Hugging Face with a model card — **push both the adapter repo** (few MB, with `base_model:` metadata so HF renders the lineage widget) **and the merged weights**. Model card YAML: `license`, `base_model`, `pipeline_tag`, `tags`, `datasets`, `library_name`. Disclose the labelling source.
- [ ] Cost arithmetic shown explicitly in the README
- [ ] Results table above the fold
- [ ] Honest limitations section (teacher-label noise ceiling, single task, held-out set size, distribution shift risk)

## Workflow discipline (same as the other projects)

Once the repo exists, run it the same way as ctxbench and mcpaudit: **aethereum sync** — `share_intent` at the start of each phase, `declare_contract` for the label schema and the eval-result shape, `record_decision` at every fork (teacher choice, task lock, base model, publish-or-gate the weights), `ask_human` before spending money on compute/labelling and before pushing weights publicly, `record_verification` at each phase gate with evidence. If the project runs longer than a day, promote the phases in this document into a `masterplan.md` with the standard status keys (`[ ]`/`[~]`/`[x]`/`[⏭]`) and work it from there.

## README rules (apply to all three sprint projects)

1. One sentence: what this does and why it exists
2. Results table or chart **above the fold**
3. A live link or one-line run command
4. Architecture description
5. **Honest limitations section** — prominent, not buried

Charts and README should look deliberate: monospace, restrained palette, data-dense. The design background is an edge most AI engineers don't have; don't waste it.

---

## Decisions locked (Aug 2026)

- **Teacher: OPEN-WEIGHT.** Bruno's call. Qwen or DeepSeek as the labelling teacher — zero ToS risk, weights publishable on HF, and the cost story survives (a large open model served via API still costs 20–50× a self-hosted 3B). The entire "legal trap" section above is thereby resolved; do not revisit closed teachers.
- **Source task: Sentinel** (Bruno delegated; this is the call). News corpus already flows through a live product; topic tagging or significance scoring distils cleanly and evaluates automatically. Poke AI (vision) remains the documented fallback if Sentinel's data can't be extracted in the first hour. Note for later: the same pipeline with civic imagery could produce RIPPLE's on-device classifier (EfficientNet-Lite0 → int8 .tflite) — a natural sequel project, not this one.
