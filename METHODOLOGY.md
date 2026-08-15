# Methodology

How the corpus was built, how it was split, what the teacher was asked, how noisy its answers
are, and what it costs the project that "gold" is a model's opinion rather than a human's.

Every number here is reproduced from a committed artifact, named inline. Nothing is quoted
from memory or from a commit message. Where a number cannot be backed, this document says so
instead of rounding to something that sounds right.

Regenerate everything below the training run with one command:

```bash
uv run python -m src.reproduce
```

---

## 1. The task, and why this one

Sentinel, a live iOS news product, routes every ingested wire headline into one of eight
topic channels. In production that router is a keyword regex, `classifyWireItem()`. It is
broken in ways visible in its own source rather than inferred from its behaviour: the `if`
chain returns on first match, so `"Amazon Prime Day"` resolves to `tech` before `consumer` is
ever considered, `"SpaceX launch"` resolves to `tech` rather than `science`, and any headline
containing `china` is `geopolitics` forever.

The eight classes are copied verbatim from that function and were not "improved":

```
geopolitics · finance · tech · sports · entertainment · science · consumer · general
```

Leaving the taxonomy alone matters for the comparison. If the class set were redesigned, the
regex would be measured against a target it was never written for, and its poor score would be
partly an artefact of the redesign. `src/regex_baseline.py` is a faithful port **including the
bugs**: the first-match ordering and the `china` rule are reproduced, not fixed.

The taxonomy also has a real flaw that no arm can escape: **there is no `politics` class.**
Domestic political headlines have no correct home, and every arm disagrees about where they
land. This is an irreducible floor on the numbers, not a model weakness (§5).

---

## 2. Corpus construction

**Source: the same 63 public RSS feeds the product reads, plus a same-outlet section
expansion. Zero credentials, zero user data.**

The production `wire_items` table was deliberately not touched. Reading it would have needed a
Supabase service key and would have put user-adjacent data into a repo intended for
publication; the RSS feeds are public and reproduce the same distribution. That decision is
recorded as D3 in `masterplan.md`.

| | value | source |
|---|---|---|
| Headlines harvested | 3,812 | `results/corpus_stats.json` |
| Split and labelled | **3,706** | same |
| Late arrivals, unused | 106 | same |
| Distinct outlets | 54 | same |
| Training pool | 3,206 | same |
| Held out | **500** | same |

Deduplication is on `sha256(url)[:16]`, which is also the `id` every downstream artifact joins
on. `data/` is gitignored (the corpus is derived from public headlines and is large), so
`src/stats.py` recomputes these figures into `results/corpus_stats.json`, which **is**
committed. This is why the README cites an artifact rather than a ledger entry.

### What did not work

**GDELT was abandoned as a backfill source.** The plan called for it to deepen the corpus
historically. It was reachable, free, and correctly rate-limited at 1 request / 5 s, but the
returned records did not yield usable headline/outlet pairs at the volume needed. The corpus
target was lowered from ≥5,500 to ≥3,500 in `AMENDMENT A1` rather than padding the count with
material that would have degraded it.

**The honest cost of that:** a smaller distillation set, and an expected weaker student on the
tail classes. That prediction is borne out. `consumer` is the smallest class in the training
pool at 191 examples and is the student's weakest class at 0.679 F1 (§6). A1 called it before
the result existed, which is the only reason it counts as a prediction rather than a
rationalisation.

---

## 3. The split protocol

**The held-out 500 were separated before a single label was generated.** This ordering is the
part that makes every downstream number meaningful, so it is enforced in code rather than
trusted:

1. `src/split.py` draws a stratified 500 from the harvested corpus and writes
   `data/heldout.jsonl`. Membership is frozen on first split and never redrawn.
2. Disjointness is **asserted on the id**, not assumed. It is checked in `split.py` at split time, and
   again in `src/prepare_training.py` when the training files are built:
   `assert not (fit_ids & test_ids), "LEAKAGE: a held-out example reached the training data"`.
3. The teacher then labels both sets. It has no knowledge of which is which.

The training pool is split again into fit and validation, 95/5, seeded (`SEED = 20260814`) and
sorted by id before shuffling so the split is deterministic regardless of file order:

| split | rows | sha256 (first 12) | role |
|---|---|---|---|
| train | 3,046 | `64a416017167` | gradient updates |
| valid | 160 | `7636ec663f2c` | **checkpoint selection only** |
| test | 500 | `a368c5be5802` | reported results, never trained on |

Full hashes are in `runs/current/hyperparams.json`. They are recorded so that a result can be
tied to the exact bytes that produced it. Renaming a file cannot hide a swap.

**The validation split earns its keep in §7.** It is the only thing that chose the shipped
checkpoint, and the held-out 500 played no part in that choice.

---

## 4. The teacher and the prompt

**Teacher: `Qwen/Qwen3.5-35B-A3B` at Q4_K_M (`unsloth/Qwen3.5-35B-A3B-GGUF`, Apache-2.0), run
locally via Ollama.** An open-weight teacher was mandatory, not a preference: publishing
weights trained on a closed model's output would breach that provider's terms, and published
weights are the headline deliverable. `prompt_version` is frozen at `v1`.

The teacher receives a system block defining all eight classes (262 tokens, measured) plus a
user turn:

```
Outlet: {outlet}
Headline: {headline}
```

Three details that materially affect the label quality:

- **Constrained decoding.** The request carries a JSON schema whose `topic` field is an enum of
  the eight classes. This is why the unparseable rate is 0.00% and not merely low.
- **`num_ctx` pinned to 2048.** Ollama defaulted to a 32,768-token context for ~300-token
  prompts, which drove a 48 GB machine into swap and free disk from 12 GB to 4 GB. Changing
  this mid-run is a methodological risk, so it was **verified rather than assumed**: 60 examples
  from before the change were re-labelled after it, and 60/60 were identical.
- **Unparseable output is never coerced.** It is marked `UNPARSEABLE` and reported. Silently
  mapping it to `general` would bias the teacher toward the majority class and corrupt the very
  ceiling the project is measured against.

**Result: 3,706 labels, 0 unparseable, 0.00%** (`results/corpus_stats.json`).

### The student's prompt is deliberately different

`AMENDMENT A3` reverses an earlier decision to hold the prompt identical across arms. The
student is trained and evaluated on the user turn **only**, with no system block:

| | teacher | student |
|---|---|---|
| input tokens (mean, n=500) | 302.98 | **35.98** |
| output tokens (mean) | 6.51 | **1.51** |

Measured, not estimated: `src/measure_tokens.py` writes `results/token_counts.json`.

The runtime trigger was that 88% of every training example was the same 262-token instruction
block repeated 3,046 times, projecting a ~10-hour run against a 1-hour cap. **But the design
argument is the one that stands on its own: a distilled student is supposed to stop needing
the instructions.** That is what "the task is in the weights" means. Forcing it to re-read 262
tokens per call would understate the distillation win in exactly the place this project
measures it, input tokens per request.

**Both arms still see identical information** (outlet + headline) and the identical held-out
500, so the quality comparison is unaffected. Only the token count differs, and that is a
result reported in the cost table rather than a confound suppressed.

The shape lives in one function, `student_messages()` in `src/prepare_training.py`: which
`src/evaluate.py` imports, so training and evaluation cannot drift apart.

---

## 5. Teacher noise: the ceiling on everything

**The student is trained on the teacher's labels and scored against them. It therefore cannot
be meaningfully more right than they are.** Measuring that ceiling is not optional.

50 held-out examples were sampled stratified (seed 4242, up to 7 per teacher-assigned class so
every class is actually audited rather than only the large ones) and adjudicated by hand
against the same `CLASS_DEFINITIONS` the teacher was given.

| verdict | count | rate |
|---|---|---|
| AGREE | 42 | **84%** |
| DISAGREE | 3 | 6% |
| AMBIGUOUS | 5 | 10% |

**Strict agreement 84%. Excluding genuinely ambiguous headlines, 42/45 = 93%.**
(`results/audit_50.md`, with the full sample in `results/audit_50_sample.json`.)

Ambiguous cases are counted separately rather than folded into either side: calling them errors
overstates teacher noise, calling them agreements understates the task's difficulty. Most of
them are the missing-`politics` problem from §1.

**This number was recorded before any student existed**, so it cannot have been tuned to
flatter one. That ordering is the only thing that makes it a ceiling rather than a
justification.

### Reproducibility of the labels

Evidence in three forms, all from S3–S4:

- 100/100 identical on a temperature-0 re-run.
- 60/60 identical across the `num_ctx` change.
- **500/500 identical** on an independent re-prediction of the entire held-out set.

---

## 6. What "gold" is, and what it costs this project

**Gold is a model's opinion.** Three consequences are load-bearing and are stated everywhere
the numbers appear, not just here:

**1. The teacher arm cannot be scored for quality.** Scoring the teacher against its own output
returns 100% by construction and means nothing. `src/evaluate.py` refuses to compute it and
prints `n/a`; the README reports the audit's 84% as the teacher's estimated accuracy instead.
A harness that quietly reported 100% would look better and be worthless.

**2. Student and regex numbers are *agreement with the teacher*, not correctness.** A student
prediction that disagrees with the teacher may be right. The 85.4% and the 84% are different
kinds of number and must not be read as a comparison, the teacher's audited accuracy is a
*ceiling* on the student's true accuracy, not a rival figure.

**3. Macro-F1 is the headline metric, not accuracy.** `general` is a catch-all; accuracy would
flatter every arm and hide tail-class collapse. Macro-F1 here averages over **all eight**
classes rather than only those present in the data, scikit-learn's default would silently
forgive a class the model never learned, and reads 0.7222 against this repo's 0.2708 on the
same fixture. A distilled model dropping a tail class entirely is precisely the failure this
project exists to surface, so it counts as a zero rather than vanishing from the mean.

---

## 7. Training

`mlx-lm` LoRA on `mlx-community/Qwen3.5-4B-bf16`, pinned at revision
`491fdc7c087ba7fb48adcb1253f8e76d011db783`. MLX because Unsloth and bitsandbytes are CUDA-only
and this is an M4 Pro. No QLoRA: at 4B in bf16 the memory is available, and quantization
artifacts are a known issue for this family.

```bash
uv run python -m mlx_lm lora -c configs/lora.yaml > runs/current/train.log 2>&1
```

r=16 · bf16 · batch 8 · lr 1e-5 constant · 1,200 iters (~3.2 epochs) · `mask_prompt: true`
(loss on the answer tokens only, so capacity is not spent regenerating a prompt the model is
always given) · seed 20260814. Full record in `runs/current/hyperparams.json`.

### `num_layers: 16` trains four layers, not sixteen

Read directly off the adapter's own safetensors header, no model load required:

```
16 tensors · 917,504 params · layers [19, 23, 27, 31] · self_attn.{q,v}_proj
```

Qwen3.5-4B is a **hybrid** architecture: `full_attention_interval: 4`, so 24 of its 32 layers
are `GatedDeltaNet` linear-attention blocks with no `self_attn.q_proj` to attach to.
`num_layers: 16` selects the last 16 layers, of which exactly four carry the targeted modules.
The config reads as though sixteen layers are tuned; four are.

This is documented rather than corrected because the run is valid and the result is strong. It
also makes the claim stronger than the plan assumed: **the student learns this task with 0.022%
of its parameters trainable**: 917,504 of 4,205,750,000.

### The last 200 iterations made the model worse

Validation loss, from `runs/current/loss.jsonl`:

```
iter    1  100  200  300  400  500  600  700  800  900  1000  1100  1200
val  5.604 .095 .080 .079 .093 .075 .077 .083 .075 .076  .276  .279  .280
```

Validation bottomed at **0.075** and ended at **0.280**. Train loss rose alongside it
(0.127 → 0.219), which rules out overfitting, that would show train falling while validation
rises. This is an optimisation excursion. Either way the effect on quality is real:

| checkpoint | val loss | macro-F1 | accuracy | artifact |
|---|---|---|---|---|
| **iter 800 (shipped)** | **0.075** | **0.8400** | **0.8540** | `results/summary.json` |
| iter 1200 (final) | 0.280 | 0.7599 | 0.7820 | `results/summary_final_checkpoint.json` |

**Selecting the best checkpoint is worth +8.0 macro-F1 points.** Shipping `mlx-lm`'s default
final weights would have discarded a tenth of the model's quality.

**The leak this could have been, and is not.** Selection reads *only* the 160-example
validation split. `src/select_checkpoint.py` never opens the held-out file, and it refuses any
iteration with no checkpoint on disk, iter 500 also reached 0.075 but had no checkpoint saved,
so it was not selectable. Selecting on the test set would have made the headline number
worthless. Both evaluations are committed, not only the flattering one.

**3.2 epochs was too many for this task.** That is a finding, and it is why the loss curve is a
deliverable rather than a diagnostic.

### Run conditions worth recording

1,200 iters at 0.313 it/s ≈ **64 minutes**. **Peak memory 43.911 GB of 48 GB**: 91% of unified
memory, which is why no other model was loaded for the duration.

This was the third attempt. The first died at ~iter 300 (pre-A3, 299 tokens/example). The
second reached ~iter 1170 of 1200 and was killed by a **macOS GPU-driver kernel panic**
(`IOGPUGroupMemory.cpp:323`) that rebooted the machine and cleared `/tmp`: where it had been
logging. That destroyed the entire loss history and forced a full retrain rather than a resume:
`mlx-lm` restarts the iteration counter on resume and does not checkpoint optimiser state, so a
resumed run yields neither an uninterrupted model nor an honestly plottable curve.
Reconstructing a curve from a lost log would have broken the honest-claims rule outright. The
third run logs inside the repo.

---

## 8. Evaluation

One harness, `src/evaluate.py`, all arms, the same 500 rows, the same machine.

**Latency** is `time.perf_counter()` around a single sequential `generate()` call, three warm-up
calls discarded, no batching. The regex is timed identically, faintly absurd for a function
call, and done anyway so all three numbers come from one instrument. The teacher's numbers come
from the S4 run over the identical 500 rows, measured before its 22 GB of weights were deleted.
**Batched labelling throughput is not latency and is never reported as it.**

**`enable_thinking=False` is mandatory**, not stylistic. Qwen3.5-4B's chat template opens a
`<think>` block by default; `mlx-lm` renders *training* examples from the full conversation,
producing a **closed** block. Without the flag, inference opens one and the model reasons
instead of answering: measured at **0/5 valid classes** during the S5 probe, against 5/5 with
it. The obvious reading, "the fine-tune failed", would have been completely wrong.

**Cost is list-price arithmetic and is labelled as such everywhere it appears.** Every arm ran
locally at $0. Token counts are measured; prices are published Fireworks serverless tiers
(retrieved 2026-08-15). The two must never be blurred.

> A note on how one of these numbers was wrong. `src/cost.py` hardcoded four token constants
> beneath a docstring claiming they were measured with the real tokeniser. They were not, and
> two were wrong in the direction that flattered the headline, student input 32 against a real
> 35.98 (the 32 was A3's figure for a whole training *example*, a different quantity), and
> teacher output 10 against a real 6.51. The published figure moved from 45.4× to **41.3×**, a
> ~9% overstatement, caught only by checking the number against the tokeniser it claimed to come
> from. `cost.py` now reads `results/token_counts.json` and raises rather than falling back.

**Disclosed limitation:** the teacher's weights were deleted in S4, so its token counts are
measured with the *student's* tokeniser (same Qwen family). That caveat is a field inside
`token_counts.json`, so it travels with the number.

**Provenance.** `results/summary.json` records `evaluated_at`, base model, **pinned revision**,
adapter path, **adapter sha256**, held-out file hashes, git commit and a **dirty flag**. The
harness previously recorded none of this and did not pass the revision to `load()`, so it
resolved whatever snapshot the cache held. A result from an unpinned model is not reproducible
and does not count.

---

## 9. Error analysis

`results/error_analysis.md` and `.json`. Three choices worth stating:

**Errors are bucketed by cause, not by class.** `tech` predicted for a SpaceX launch and `tech`
predicted for an Amazon sale are the same confusion pair and two different mistakes. The regex's
buckets are mechanical and checkable against its own source, catch-all fall-through, the
`china` rule firing before every later branch, first-match-wins. The student's are deliberately
coarser: inventing fine-grained causes for a neural model's errors would be storytelling.

**Recall and F1 are reported separately, and neither is allowed to swallow the other.** The
student loses `general` on recall, 68.2% against the regex's 98.5%. The regex earns that by
answering `general` for **375 of 500 headlines**, at 17.3% precision. On F1 the ordering
reverses (0.698 vs 0.295) and the student loses no class at all. Reporting only recall would
invent a student weakness that is really the catch-all's artefact; reporting only F1 would bury
a real difference. `per_class_gap` carries `student_loses` and `student_loses_on_f1` as
distinct flags for exactly this reason.

**The outlet-tier breakdown was not shipped, and nothing was invented to fill it.** The plan
asked for one. No tier taxonomy exists in this repo, `Feed` is `(outlet, url, section)` and
`heldout.jsonl` has no `tier` field, so the column would have read `unknown` for all 500 rows
while looking like a result. Ranking 54 outlets by editorial prestige would be fabricating data
to satisfy a checkbox, and every sentence downstream would have inherited it. Shipped instead:
per-outlet agreement, which is real, and a **volume band** cut on held-out counts, labelled
inside the artifact as a stated proxy for prominence rather than an editorial judgement.

---

## 10. Limitations

Restated compactly. The README carries these prominently; they are not buried here.

- **Gold is teacher-labelled.** Student and regex figures are agreement, not correctness. The
  teacher's own audited agreement with a human is **84%**, and that is the ceiling on all of it.
- **The taxonomy has no `politics` class.** An irreducible floor no arm can clear.
- **One task, one language, headlines only.** No article body, English only, eight classes.
- **500 held-out examples.** Small enough that per-class figures on the tail classes,
  `consumer` has 34, carry real uncertainty. No confidence intervals are reported because a
  single run cannot support them honestly.
- **One training run.** No seed variance, so the +8.0 checkpoint-selection delta and the
  per-class figures are single-sample. A second seed would strengthen every claim here.
- **Cost is list-price arithmetic, not measured spend.** $0 changed hands. The 41.3× figure
  also assumes the sub-4B tier; Qwen3.5-4B is 4.21B params, just over the boundary. Billed one
  tier up it is **8.3× cheaper**: the pessimistic read, published alongside.
- **Distribution shift.** The feeds move. A corpus harvested next month differs.
- **`consumer` is weak**: recall 52.9%, F1 0.679, usually called `tech`. A milder inheritance
  of the exact bug this project opens with, and predicted by A1 before the result existed.

---

## Artifact index

| file | what it backs |
|---|---|
| `results/summary.json` | every headline number, plus provenance |
| `results/summary_final_checkpoint.json` | the unshipped iter-1200 comparison |
| `results/predictions.jsonl` | per-row predictions, all arms |
| `results/error_analysis.{json,md}` | taxonomy, head-to-head, per-class, breakdowns |
| `results/token_counts.json` | the measured inputs to the cost model |
| `results/audit_50.md` · `results/audit_50_sample.json` | the 84% teacher ceiling |
| `results/sanity_20.json` | 20/20 merged-model sanity predictions |
| `results/corpus_stats.json` | corpus and distribution figures (`data/` is gitignored) |
| `runs/current/loss.jsonl` | per-step train and validation loss, nan preserved |
| `runs/current/hyperparams.json` | hyperparameters, revision, dataset hashes, versions |
| `runs/current/best/selection.json` | which checkpoint was chosen, and on what evidence |
| `charts/*.png` | class and label distributions, training curve, confusion matrices |
