# SYNC.md — aethereum sync ledger

The sync verbs (`share_intent`, `declare_contract`, `record_decision`, `ask_human`,
`record_verification`) are **MCP tools**. `aethereum init` has wired the server into
`.mcp.json`, but an MCP server cannot be hot-added to a running session — the tools become
callable from the **next** session.

So every sync event is recorded here, in canonical verb form with a timestamp, and replayed
through the real tools once the server is live. This mirrors aethereum's own design: all its
handlers fail soft with an `OFFLINE` sentinel and never throw. A local ledger is the same
contract. Blocking the project on an MCP reconnection would be the wrong call.

**Room:** `distillation` (room id and join code deliberately not committed — the join code
grants room access and this repo is a candidate for going public at S9. Recover them locally
with `aethereum status`.)

**Replay status:** `PENDING` — no entry below has been pushed to the room yet.

---

## S0 — Foundation

**2026-08-14 · `share_intent`**
> Standing up the distillation repo: constitution, masterplan, Python 3.12 toolchain via uv,
> MLX verified on Metal, ccline statusline, aethereum room. No ML yet — S0 is foundation only.

**2026-08-14 · `record_decision` — D1 · task lock**
> Distilling 8-class wire topic classification (`geopolitics · finance · tech · sports ·
> entertainment · science · consumer · general`), the class set used verbatim by
> `classifyWireItem()` in Sentinel's production backend.
> **Why:** the brief's selection rule is non-negotiable — crisp right answer, auto-scorable
> against ground truth. This is a closed label set on a live production feature, so it scores
> automatically via macro-F1 and carries a real incumbent to compare against. Significance
> scoring was rejected as too fuzzy to have a defensible ceiling; the Poke AI vision fallback
> was rejected because verifying its data would have burned the first hour, which the brief
> forbids.

**2026-08-14 · `record_decision` — D2 · teacher**
> Teacher is `Qwen/Qwen3.5-35B-A3B` at Q4_K_M (`unsloth/Qwen3.5-35B-A3B-GGUF`, Apache-2.0),
> run locally via Ollama.
> **Why:** the ENGINEERPROMPT locks the teacher to open weights — training on Anthropic,
> OpenAI or Gemini output and then publishing weights would breach their terms, and the
> published-weights deliverable is the point. MoE with ~3B active params makes a 35B-class
> teacher fast on an M4 Pro. Costs nothing, needs no owner gate, and the cost story survives
> intact because a 35B-class model served via API is still 20–50× the price of a 4B.

**2026-08-14 · `record_decision` — D3 · corpus**
> Corpus rebuilt from the 61 public RSS feeds hardcoded in Sentinel's `_shared/wire.ts`,
> backfilled via GDELT. **Zero credentials, zero user data.**
> **Why:** reproduces the production distribution exactly without touching the production
> Supabase or any user-generated content. No privacy disclosure burden, no credential
> handling, and nothing in the plan can block waiting for a key.

**2026-08-14 · `record_decision` — D4 · three arms, not two**
> Reporting regex · teacher · student, not just teacher · student.
> **Why:** the regex is the actual incumbent in production. Comparing only against the
> teacher would be choosing the flattering baseline — precisely the credibility failure the
> brief warns about. If the student cannot beat a keyword regex, that is the finding and it
> leads the README.

**2026-08-14 · `record_decision` — D5 · cost is arithmetic, latency is measured**
> Cost figures are list-price arithmetic and are labelled as such in every surface; latency is
> genuinely measured on one machine with one harness.
> **Why:** everything runs locally at $0, so presenting a dollar figure as measured spend
> would be dishonest. The two must never be blurred.

**2026-08-14 · `record_decision` — D6 · MLX for training**
> Training via `mlx-lm` 0.31.3, not Unsloth or TRL.
> **Why:** Unsloth and bitsandbytes are CUDA-only; this is an Apple M4 Pro. TRL/peft on MPS
> is slow and flaky. MLX is the native path and is verified running on Metal.

**2026-08-14 · `record_decision` — D7 · macro-F1 is the headline metric**
> **Why:** `general` is a catch-all that will dominate the distribution. Accuracy would
> flatter every arm equally and hide tail-class failure, which is exactly where a distilled
> small model is expected to lose.

**2026-08-14 · `record_decision` — D8 · all owner gates deferred to S9**
> **Why:** owner instruction. S0–S8 run free and unattended with no interruption; every
> money, publication, and irreversible external action is batched into the final sprint.

**2026-08-14 · `record_decision` — D9 · LoRA r=16 bf16, no QLoRA**
> **Why:** at 4B in bf16 the memory is available on 48 GB unified, so QLoRA buys nothing, and
> Unsloth explicitly advises against QLoRA for Qwen3.5 due to quantization artifacts.

**2026-08-14 · `record_decision` — S0 · disk sequencing**
> The teacher is deleted at the end of S4, before the student base model is pulled.
> **Why:** 34 GB free disk is the binding constraint. Naïve ordering needs 37 GB. Sequencing
> holds the peak at ~21 GB. Teacher latency is therefore measured in S4 *before* deletion,
> sequentially on the held-out 500 — batched labelling throughput is not latency.

**2026-08-14 · `record_verification` — S0 gate**
> - `uv` 0.12.4 installed; venv on **Python 3.12.13** (system 3.14.6 is too new for the wheels) — PASS
> - `mlx-lm` 0.31.3, `transformers` 5.15.0; MLX matmul verified on `Device(gpu, 0)` — PASS
> - ccline statusline installed to `.claude/settings.json`, merge-only — PASS
> - aethereum room `distillation` created and wired; MCP available next session — PASS
> - `CLAUDE.md` + `masterplan.md` authored (S0–S9 + backlog) — PASS
> - Evidence: this file, `pyproject.toml`, `uv.lock`, foundation commit.

---

## S1 — Contracts and scoring

**2026-08-14 · `share_intent`**
> Freezing the label schema, the results schema and the scoring function before any label
> exists, plus a faithful port of the production regex as the incumbent arm. The brief is
> explicit that this ordering is not optional.

**2026-08-14 · `declare_contract` — `Example` v1**
> `{id: sha256(url)[:16], headline, outlet, url, published_at?, source, split: train|heldout}`
> Produced by `src/harvest.py` and `src/gdelt.py`. `id` is the key that S2's disjointness
> assertion runs on.

**2026-08-14 · `declare_contract` — `Label` v1**
> `{id, label: TopicClass|UNPARSEABLE, teacher_model, teacher_revision, prompt_version,
> latency_ms, raw_output}`
> Produced by `src/teacher.py`. `raw_output` is retained so any parse decision can be
> re-audited. `UNPARSEABLE` is **not** a ninth class — consumers filter, never coerce.

**2026-08-14 · `declare_contract` — `Prediction` v1**
> `{id, arm: regex|teacher|student, pred, gold, latency_ms}` — the results JSONL row shape.
> `gold` is the teacher's label. Calling it gold is a convenience, not a claim: it is a
> model's opinion, and S4's hand-audit measures the distance between the two.

**2026-08-14 · `record_decision` — macro-F1 averaging convention**
> Macro-F1 averages over **all eight** classes in `TOPIC_CLASSES`, not over the classes
> present in the data.
> **Why:** scikit-learn's default averages over labels present in `y_true ∪ y_pred`, which
> silently forgives a class the model never learned. On the S1 fixture that default reads
> 0.7222 against our 0.2708 — nearly 3× flattering. A distilled small model dropping a tail
> class entirely is precisely the failure this project exists to surface, so it must count
> as a zero rather than vanish from the mean. Implemented from first principles rather than
> imported, so the choice is visible in this repo instead of inherited from a library.

**2026-08-14 · `record_decision` — the incumbent is ported with its bugs intact**
> `src/regex_baseline.py` reproduces `classifyWireItem()` behaviourally, including five
> defects that follow from "first `if` that matches wins":
> `amazon` in the tech rule makes the consumer rule's `amazon prime` keyword dead code ·
> `spacex` appears in both tech and science, so the science occurrence never fires ·
> any country name forces `geopolitics` regardless of subject · `target` is unreachable in
> practice · everything unmatched falls to `general`, which is a catch-all rather than a class.
> **Why:** silently fixing them would make the incumbent arm a strawman in the opposite
> direction — it would no longer be the thing running in production, and the comparison
> would measure nothing. Each defect is pinned by a passing test so a future "fix" fails loudly.

**2026-08-14 · `record_decision` — ASCII word-boundary semantics**
> The port compiles every rule with `re.ASCII`.
> **Why:** JavaScript's `\b` is defined over ASCII word characters; Python's is Unicode-aware
> by default. Verified divergence: on `"iraníes protest in the capital"` the geopolitics rule
> matches under `re.ASCII` (production behaviour) and does **not** match under Python's
> default. The corpus includes DW, France24, SCMP and Haaretz, so accented text is not
> hypothetical. Without this flag the incumbent arm would be quietly weaker than production.

**2026-08-14 · `record_verification` — S1 gate**
> - `pytest`: **38 passed** in 0.32s — PASS
> - Scorer verified against a hand-computed fixture: accuracy 4/6, macro-F1 0.270833 — PASS
> - Averaging convention pinned by a test asserting the result is *not* the flattering 0.7222 — PASS
> - All five incumbent defects pinned by passing tests — PASS
> - ASCII-vs-Unicode divergence verified empirically, so the test is not vacuous — PASS
> - Evidence: `tests/test_scoring.py`, `tests/test_regex_baseline.py`, S1 commit.

---

## S2 — Corpus

**2026-08-14 · `share_intent`**
> Rebuilding the corpus from the production RSS catalog with zero credentials, then splitting
> a 500-example held-out set before any labelling exists.

**2026-08-14 · `record_decision` — same-outlet section expansion**
> Added `EXPANSION_FEEDS`: 84 live section feeds drawn only from outlets already in the
> production catalog.
> **Why:** measurement killed the original volume plan. One pass over the 63 production feeds
> yields ~1,800 unique headlines; a second pass fifteen minutes later yields **7**, because
> the feeds carry a rolling window that has not moved. Volume comes from breadth or from
> hours, not from more passes. Section feeds preserve the thing that actually defines the
> distribution — the outlets — since BBC's technology feed is the same newsroom as BBC's
> front page. An `assert` in `feeds.py` and a test in `tests/test_corpus.py` enforce that no
> outlet outside the production catalog is ever introduced; `skysports.com` was probed,
> worked, and was dropped solely for failing that rule. It also fixed the tail-class problem
> at its source: the production catalog has 3 sports and 4 science feeds against 16 general,
> and the expansion adds 11 sports and 17 science.

**2026-08-14 · `record_decision` — proportional sampling, not class-balanced**
> The held-out 500 is sampled proportionally within section, not balanced across classes.
> **Why:** balancing would guarantee a full complement of every class, but it would make the
> held-out set unrepresentative of what the product's ingest actually sees, and every number
> measured on it would then describe a distribution that does not exist. Macro-F1 already
> weights classes equally, so buying tail coverage by distorting the sample pays twice for
> the same thing and misdescribes the traffic. The cost is accepted openly: thin classes get
> reported in the limitations section rather than padded by synthesis or over-sampling.

**2026-08-14 · `record_decision` — held-out membership is frozen on first split**
> Re-running `src/split.py` preserves the existing held-out ids exactly and routes everything
> new to the training pool.
> **Why:** the background harvester keeps adding rows after the split. Growing the training
> pool can never leak into the held-out set; re-drawing the held-out set once labelling had
> begun absolutely could. Freezing makes the bad case impossible by construction instead of
> depending on someone remembering the rule.

**2026-08-14 · `record_decision` — GDELT abandoned as a backfill source**
> `src/gdelt.py` is kept but is not used to build this corpus.
> **Why:** it throttles far beyond its documented 1-req/5s. One request succeeds and every
> subsequent request returns HTTP 429 regardless of spacing — verified at 20s and at 65s —
> and it contributed **zero** rows across 20 minutes of patient trickling. It also
> under-delivers when it does answer: 52 articles against a requested 250. The code is
> correct and a fresh IP or a later day would work, so it stays; the corpus does not depend
> on it. Politeness stays a sleep, never a retry-on-429 — hammering a free public service
> until it relents is not something this repo does.

**2026-08-14 · `record_decision` — design system inherited wholesale**
> `src/charts.py` transcribes `hive/apps/web/styles/tokens.css`; the `--id-ring-1..8`
> agent-identity palette is used for the eight topic classes.
> **Why:** owner instruction is to inherit, not design. The id-ring palette is an exact fit —
> eight tokens for eight classes, built to be mutually distinguishable, and deliberately
> excluding green and amber because both are load-bearing signal colours in that system.
> Amber `#FF9500` is reserved for collision alerts and appears in no chart in this repo.
> Geist TTFs vendored under SIL OFL-1.1 with the licence, so charts reproduce without
> depending on the hive repo's path.

**2026-08-14 · `record_verification` — S2 gate**
> - Corpus: **3,706 unique** headlines, 54 live outlets, 146 feeds attempted — PASS (target amended, A1)
> - Held-out: exactly **500**, disjoint by id AND by headline, both asserted in code — PASS
> - Held-out spans 53 outlets; sections entertainment 51 · sports 44 · science 68 — PASS
> - `charts/class_distribution.png` committed — PASS
> - `pytest`: **59 passed** — PASS
> - **Finding: the incumbent regex sends 74.2% of the corpus to `general`.** It places only a
>   quarter of real headlines into a real class. This is the project's premise, measured.
> - Feed bitrot: 6 of 146 feeds return 4xx, 5 parse to zero items. All five hand-checked and
>   correct — including **`nhk.or.jp`, which is a podcast feed** whose items are episode
>   titles with no article link. That is a live defect in the production catalog.
> - `[⏭]` all-8-classes-in-held-out deferred to S4: the regex proxy assigns zero held-out
>   examples to `consumer`, which is a fact about the regex, not about the corpus.
> - Evidence: `data/corpus.jsonl`, `data/heldout.jsonl`, `charts/class_distribution.png`, S2 commit.

---

## S3 — Teacher setup and pilot

**2026-08-14 · `share_intent`**
> Pulling the Qwen3.5-35B-A3B teacher, designing and freezing the labelling prompt, and
> piloting 100 labels before committing the full run to it.

**2026-08-14 · `record_decision` — JSON-schema-constrained decoding**
> The request carries a schema whose `topic` field is an enum over the eight classes.
> **Why:** the planned approach — ask for one word, parse the reply — spends label quality on
> an avoidable problem. Constraining the sampler makes an invalid class impossible.
> `UNPARSEABLE` is retained rather than removed, because a request can still fail at the
> transport layer, and those failures must surface instead of quietly becoming `general`.
> Measured result: **0% unparseable across the 100-example pilot.**

**2026-08-14 · `record_decision` — prompt frozen at `v1`, unchanged**
> **Why:** the pilot passed on first contact — 100/100 parsed, all eight classes used, labels
> sound on inspection. Iterating a prompt that works would invalidate the pilot that
> validated it. `prompt_version` is written into every `Label` row, so a mixed-prompt dataset
> would be detectable after the fact rather than silently averaged.

**2026-08-14 · `record_decision` — latency measured warm, with warm-up discarded**
> `latency_run` throws away three calls before timing anything.
> **Why:** measured on this machine, a cold first call costs 19.6 s against ~800 ms warm —
> that is weight-loading, not inference. Including it in p95 would report the cost of
> *starting* a server rather than of serving a request, and both arms in this comparison are
> served warm. Stated in METHODOLOGY rather than buried in the code.

**2026-08-14 · `record_verification` — S3 gate**
> - Teacher pulled: `hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M`, **22 GB**, Apache-2.0 — PASS
> - Pilot: 100 labels, **0% unparseable**, all 8 classes present — PASS (bar was ≥98%)
> - Self-consistency **temp 0: 100/100 unanimous** — labelling is exactly reproducible — PASS
> - Self-consistency **temp 0.7: 86/100 unanimous** — reported — PASS
> - Throughput **1.24 labels/s** ⇒ S4 ≈ 43 min (train) + 7 min (held-out) — PASS
> - `pytest`: **93 passed** — PASS
> - Disk: **12 GB free**, 98% used. Watch until S4 deletes the teacher.
>
> **Findings that change the write-up:**
> - The 14% temp-0.7 disagreement is **genuine multi-label ambiguity, not model noise**.
>   Every case inspected honestly belonged to two classes. This is a soft ceiling on *every*
>   arm and belongs in S8 limitations — the task forces one label onto two-class headlines.
> - Teacher and regex **disagree on 60 of 100** pilot examples, with the teacher right in
>   nearly all of them.
> - Regex sends **74.2%** of the corpus to `general`; the teacher sends **28%** of the pilot.
> - **Sixth regex defect, the most consequential yet:** every keyword is a bare noun and `\b`
>   demands a non-word character after it, so `Russian`/`Chinese`/`Israeli`/`Ukrainian`/
>   `Korean` never match `russia`/`china`/`israel`/`ukraine`/`korea`. Headlines use the
>   adjectival form constantly and every one lands in `general`. Verified over five pairs,
>   pinned by a test, and a large part of the 74%.
> - **A teacher error, recorded not hidden:** *"New Zealand breaks ranks and withdraws
>   Infantino support"* → `geopolitics`, but Infantino is FIFA's president and this is sports
>   governance. The S4 audit exists to put a number on how often this happens.
> - Evidence: `/tmp/pilot_labels.jsonl`, consistency log, `tests/test_regex_baseline.py`, S3 commit.

---

## S4 — Label, audit, measure, reclaim disk

**2026-08-14 · `share_intent`**
> Labelling the held-out 500 and the 3,206-example training pool, hand-auditing 50 to fix the
> ceiling, measuring teacher latency sequentially, then deleting the 22 GB teacher.

**2026-08-14 · `record_decision` — `num_ctx` pinned to 2048 mid-run**
> Ollama defaulted the teacher to a 32,768-token context for ~250-token prompts. That KV
> cache, on top of 22 GB of resident weights on a 48 GB machine, drove the system into swap
> (7.7 GB, 290k pageouts) and took free disk from 12 GB to 4 GB during the run.
> **Why 2048:** still 8× headroom over the longest prompt, and it stopped the bleed
> immediately. **Why not the alternatives:** dropping to a smaller quant would degrade the
> teacher, and the teacher is the ceiling for every number downstream; deleting the 9.6 GB of
> pre-existing `llama3` models would have freed plenty but they are Bruno's, and this project
> does not delete a user's models to make room for itself. A watchdog was armed to abort
> labelling below 2 GB — the run is checkpointed every 50, so an abort would have cost one
> batch. It never fired.

**2026-08-14 · `record_decision` — the mid-run config change is verified, not assumed**
> Re-labelled 60 randomly sampled examples from the first 1,000 (written under the old
> 32,768 context) using the new 2,048 setting: **60/60 identical**.
> **Why it mattered:** the first 1,000 labels and the remaining 2,206 were produced under
> different runtime configuration. At temperature 0 with prompts that fit comfortably in both
> windows the output *should* be identical — but "should be" is not evidence, and a dataset
> silently split across two configs would be a real defect. Now measured.

**2026-08-14 · `record_decision` — the teacher arm is not scored against its own labels**
> Gold *is* the teacher, so "teacher accuracy vs gold" is 100% by construction and means
> nothing. S7 will instead report the **hand-audit 84%** as the teacher's estimated true
> accuracy, and will state plainly that student-vs-gold measures agreement with the teacher
> rather than correctness.
> **Why:** reporting a constructed 100% next to a real student number would be the single
> most misleading thing this project could publish.

**2026-08-14 · `record_verification` — S4 gate**
> - Labels: **3,206 train + 500 held-out = 3,706**, **0.00% unparseable** — PASS
> - Hand audit: **84% strict** (6% disagree, 10% genuinely ambiguous; 93% excluding ambiguous)
>   — recorded in `results/audit_50.md` **before any student exists**, so it cannot be tuned
>   to flatter one — PASS
> - Teacher latency, sequential and warm, n=500: **p50 782 ms · p95 868 ms** (min 562, max 1061) — PASS
> - Disk reclaimed: **6.1 GB → 27 GB** (21 GB), Bruno's models untouched — PASS
> - `charts/label_distribution.png` committed — PASS
>
> **Reproducibility, evidenced three ways:**
> - 100/100 unanimous at temp 0 (S3 consistency probe)
> - **60/60 identical** across the `num_ctx` change
> - **500/500 identical** on a fully independent re-prediction of the held-out set
>
> **Findings:**
> - Of the 375 held-out headlines the regex calls `general`, the teacher reassigns **310
>   (82.7%)**. The catch-all is wrong five times out of six.
> - On the same 500: regex `general` 75%, teacher `general` 13.2%.
> - On the 3,206 training pool: teacher `general` 426 (13.3%) vs regex `general` **2,374
>   (74%)**; teacher `consumer` 191 vs regex `consumer` **6**. The teacher yields a balanced
>   training set where the incumbent yields rubble.
> - Evidence: `data/train_labels.jsonl`, `data/heldout_labels.jsonl`,
>   `data/teacher_latency.jsonl`, `results/audit_50.md`, `charts/label_distribution.png`.

---

## S5 — Base-model architecture probe

**2026-08-15 · `share_intent`**
> Probing whether mlx-lm can actually LoRA-tune Qwen3.5-4B on 20 examples before committing
> the training sprint to it.

**2026-08-15 · `record_decision` — base model is `Qwen/Qwen3.5-4B`, no fallback used**
> Via `mlx-community/Qwen3.5-4B-bf16` @ `491fdc7c087ba7fb48adcb1253f8e76d011db783`.
> **Why:** it is option 1 on the ladder and it passed. The model loads (4.21B params,
> multimodal wrapper included), LoRA attaches at 0.096% trainable (4.058M of 4,205.75M),
> loss fell 2.594 -> 0.051 over 20 iterations, peak memory 18.6 GB. The three fallbacks stay
> documented but unused.

**2026-08-15 · `record_decision` — `enable_thinking=False` is MANDATORY at inference**
> The eval harness must pass it to `apply_chat_template`. This is not a preference.
> **Why:** Qwen3.5-4B is a reasoning model whose chat template opens a `<think>` block by
> default. mlx-lm renders *training* examples from the full conversation, producing a
> **closed** block — `...assistant\n<think>\n\n</think>\n\nfinance<|im_end|>`. A plain
> `add_generation_prompt=True` at inference produces an **open** `<think>\n` instead, and the
> model reasons rather than answering. Measured: without the flag **0/5 valid classes**
> (every output began "Thinking Process:"); with it, **5/5 valid and 5/5 correct**. Without
> this decision the student would have scored near zero in S7 and the obvious reading —
> "the fine-tune failed" — would have been entirely wrong.

**2026-08-15 · `record_decision` — student keeps the teacher's full system prompt**
> Training examples carry the same system prompt, same `Outlet:/Headline:` user turn, same
> frozen `PROMPT_VERSION` the teacher saw.
> **Why:** a shorter student prompt would be a legitimate further optimisation and would
> improve the cost story, but changing the prompt between arms would confound quality with
> prompt engineering. Holding it constant keeps the quality comparison clean; the shorter
> prompt is noted in S7's cost section as available headroom rather than taken here.

**2026-08-15 · `record_verification` — S5 gate**
> - Base model chosen and revision pinned — PASS
> - Smoke fine-tune completes, loss decreases 2.594 -> 0.051 — PASS
> - Adapter loads standalone and produces valid classes — PASS (**5/5 valid, 5/5 correct**)
> - Training data built: 3,046 train / 160 valid / 500 test, smallest class `consumer` = 182,
>   leakage assertion passes (500 held-out ids absent from train+valid) — PASS
> - `configs/lora.yaml` committed, fully specifying the S6 run — PASS
> - Evidence: `/tmp/smoke_adapter/adapters.safetensors`, `configs/lora.yaml`, S5 commit.

---

## S6 — Train

> Ledger note: the first S6 working session produced two commits (`61af2e3`, `39333c7`) and
> no ledger entries. These four are written retroactively, dated to when the decision was
> actually taken, and the omission is recorded rather than papered over.

**2026-08-15 · `share_intent`**
> LoRA fine-tuning Qwen3.5-4B on the 3,046 teacher-labelled training examples, then merging
> the adapter and running 20 sanity predictions. Produces `runs/current/loss.jsonl`,
> `runs/current/hyperparams.json` and `charts/training_curve.png`.

**2026-08-15 · `record_decision` — the student gets a lean prompt (REVERSES the S5 decision above)**
> The student is trained and evaluated on `Outlet:/Headline:` alone, with no system block.
> Recorded in full as `AMENDMENT A3` in `masterplan.md`. **This supersedes the S5 entry
> "student keeps the teacher's full system prompt"** three entries up, which should be read as
> closed, not current.
> **Why:** the trigger was runtime — 299 tokens per example with the system block against 32
> without, i.e. the same 262-token instruction repeated 3,046 times per epoch, projecting a
> ~10 h run against the brief's 1 h cap; lean runs at 0.30 it/s ≈ 70 min. But the design
> argument is the stronger one and stands on its own: **a distilled student is supposed to
> stop needing the instructions** — that is what "the task is in the weights" means. Making it
> re-read 262 tokens per call would understate the distillation win in exactly the place this
> project measures it, input tokens per request. Both arms still see identical information
> (outlet + headline) and the identical held-out 500, so the quality comparison is untouched.
> The 9.3x input-token drop is a **result for the S7 cost table, not a confound to suppress**.
> The shape lives in one function, `student_messages()` in `src/prepare_training.py`, which
> `src/evaluate.py` imports so training and eval cannot drift.

**2026-08-15 · `record_decision` — cost is priced on published per-parameter-tier rates**
> Fireworks serverless list price: **$0.10/1M under 4B**, **$0.50/1M for MoE up to 56B**, flat
> across input and output, retrieved 2026-08-15. Cross-checked against Together's list
> (Qwen3.5-9B $0.17/$0.25; Qwen3.5-397B-A17B $0.60/$3.60).
> **Why:** it is the rare case where a published rate applies to a *specific open model* by
> tier rather than requiring a guess, so both arms land in a tier without interpretation.
> Token counts are **measured with the real tokeniser on the real rendered prompts**, not
> estimated. Two sensitivity rows are reported *because they cut against the headline*: had
> the student kept the teacher's full prompt it would be 5.1x cheaper rather than 45.4x (A3 is
> worth 9x of the 45x), and Qwen3.5-4B is 4.21B params — just over the sub-4B tier boundary —
> so billed one tier up it is 9.1x cheaper, which is the pessimistic read and is published as
> such. **No money changed hands: every arm ran locally at $0**, and that disclaimer travels
> with the number into `results/summary.json` and the README.

**2026-08-15 · `record_decision` — loss is reported every step, not every 25**
> `steps_per_report` lowered from 25 to 1 in `configs/lora.yaml` for the re-run.
> **Why:** masterplan S6 asks for "every step's loss" in `runs/<id>/loss.jsonl`, and a 25-step
> cadence yields 48 points for a 1,200-step curve. Logging cadence only — it changes no
> training arithmetic, and the seed, data, and all hyperparameters are otherwise identical.

**2026-08-15 · `record_decision` — the interrupted run is discarded and retrained from scratch**
> The first full run died at ~iter 1170 of 1200 when the machine **kernel-panicked in the GPU
> driver** (`IOGPUGroupMemory::remove_memory_object()`, `IOGPUGroupMemory.cpp:323`; panicked
> task `python3.12`, 25 GB resident) at 05:02:41. Adapters through iter 1000 are preserved at
> `runs/interrupted-panic-20260815/` and are not used.
> **Why:** the run logged to `/tmp/train.log` and the reboot cleared `/tmp`, so the loss
> history for iters 1–1000 is **unrecoverable**. `mlx-lm` can resume from a checkpoint, but it
> restarts the iteration counter and does not checkpoint optimiser state, so a resumed run is
> neither an uninterrupted run nor one whose curve can be honestly plotted. A curve assembled
> from a lost log would violate the honest-claims rule. Retraining costs ~70 minutes and is
> the only path to a defensible `loss.jsonl`. **The re-run logs to `runs/current/train.log`,
> inside the repo, so a reboot cannot take it again.**

---

## Sprint D — Documentation

**2026-08-15 · `share_intent`**
> Making the repo read well to a stranger on GitHub: README rewritten to the
> `DOCS-ENGINEERPROMPT.md` structure, `PROJECT.json` for the portfolio to consume, LICENSE, CI,
> and a committed artifact behind every number. Documentation only — no engineering scope, and
> no model loads, because a parallel session owns the live S6 training run.

**2026-08-15 · `ask_human` — four questions, all answered**
> 1. *S6/S7 are unfinished and there are no student results. Document now, or finish first?*
>    → **Document now, results pending.** The student row stays empty rather than estimated.
> 2. *Which S9 owner gates are done?* → **None.** No GitHub remote, no HF repo. Every
>    `links.*` in `PROJECT.json` is `null` and nothing is published.
> 3. *Any number to hold back or soften?* → **Publish everything**, including the six named
>    defects in the production regex and the NHK podcast-feed defect in the live catalog.
> 4. *Hero visual?* → `charts/label_distribution.png`.

**2026-08-15 · `record_decision` — a committed stats artifact, because `data/` is gitignored**
> Added `src/stats.py`, which recomputes every corpus and teacher figure from the JSONL and
> writes `results/corpus_stats.json`.
> **Why:** the honest-claims rule says no number in the README that a committed artifact cannot
> back. `data/` is correctly gitignored — it is large and regenerable — but that left the
> corpus counts, the 74.2%, the 82.7% reassignment and the teacher's p50/p95 backed only by
> prose in `masterplan.md` and this ledger. Prose is a claim; a regenerable JSON file is a
> receipt. It also served as a check on the ledger: every figure reproduced, and the 74.2% was
> confirmed to be measured on the 3,706 labelled rows rather than the 3,812 now in
> `corpus.jsonl`, which the artifact now states explicitly.

**2026-08-15 · `record_decision` — no student number is published while the student is unevaluated**
> The results table carries four `pending` cells for the student's quality and latency.
> **Why:** the training run that produced the adapter on disk died in a kernel panic, S7 has
> never run, and `results/summary.json` carries `student_evaluated: false`. A projected number
> is not a number. Cost is the one exception and is published — it is arithmetic over token
> counts measured on the rendered prompts, so it does not depend on the student having been
> evaluated, and the README says so in a footnote rather than letting a reader assume the whole
> row is measured.

**2026-08-15 · `record_verification` — the cost model was wrong and is now artifact-backed**
> Writing the cost section required checking `src/cost.py`'s four hardcoded token constants.
> Re-tokenising all 500 held-out prompts through each arm's real prompt builder found **all
> four wrong, in both directions**:
>
> | | hardcoded | measured (mean, n=500) |
> |---|---|---|
> | teacher input | 299 | **302.98** |
> | teacher output | 10 | **6.51** |
> | student input | 32 | **35.98** |
> | student output | 2 | **1.51** |
>
> - Root cause: the student's 32 was A3's **training-example** figure (user turn + answer),
>   which is a different quantity from an inference-time input. — CONFIRMED
> - Published headline moves **45.4× → 41.3×** cheaper; 2.20% → **2.42%** of teacher cost. Both
>   sessions measured the student's output independently and agreed at **1.51**. — CONFIRMED
> - `src/cost.py` now reads `results/token_counts.json` and raises if it is absent, so it can
>   no longer silently fall back to a constant. — CONFIRMED
> - **A3's `9.3×` is superseded** for cost purposes: the measured per-request token ratio is
>   **8.26×**. A3 remains correct for the training-example quantity it describes.
> - Caveat that travels with the number: the teacher's weights were deleted in S4, so its
>   prompts are tokenised with the **student's** tokeniser — same Qwen family, not the same
>   file. Recorded in `results/token_counts.json`.

**2026-08-15 · `record_verification` — the incumbent arm, scored end to end**
> `src/evaluate.py --skip-student` loads no model, so it ran safely alongside the live training
> job. On the held-out 500, gold = teacher label:
> - **macro-F1 0.3372 · accuracy 0.3420 · 0 invalid outputs** — PASS
> - **`consumer` F1 0.000 on 34 held-out examples.** The rule never fires once, because
>   `amazon` is matched by the tech branch above it — dead code in production, now measured
>   rather than inferred from reading the source.
> - Precision is high where it fires and recall is not: entertainment P 1.000 / R 0.129,
>   sports P 0.929 / R 0.250, geopolitics P 0.826 / R 0.196. `general` inverts it at
>   P 0.173 / R 0.985.
> - All five top confusions are the same confusion, `X → general`: geopolitics 78, science 59,
>   entertainment 50, sports 39, finance 31.
> - Evidence: `results/summary.json`, `results/predictions.jsonl`.

**2026-08-15 · `record_verification` — Sprint D gate**
> - `pytest`: **138 passed** — PASS (93 at sprint start; the parallel S6/S7 session
>   added the chart-guard and provenance suites mid-sprint)
> - Every local link, image and anchor in `README.md` resolves — PASS (checked mechanically)
> - Every README number checked against its artifact programmatically: per-class table vs
>   `summary.json`, scalars vs `corpus_stats.json`, section counts vs `src/feeds.py` — PASS
> - `PROJECT.json` validates; all 8 `metrics[].source` paths and `headline.source` exist;
>   `honest` non-empty — PASS
> - No badge that 404s: static badges only, and the CI badge is withheld until the repo has a
>   remote — PASS
> - `.github/workflows/ci.yml` committed, including a gate asserting the reserved amber
>   `#FF9500` never reaches a chart. Gate verified locally — PASS
> - **Two stale counts corrected:** the production catalog is **63** feeds, not the 61 in
>   `CLAUDE.md` and the old README; committed `EXPANSION_FEEDS` is **83**, not 84 (86 probed,
>   84 returned items, `skysports.com` then dropped for introducing a new outlet).
> - Evidence: `README.md`, `PROJECT.json`, `results/corpus_stats.json`, `results/summary.json`,
>   `LICENSE`, `.github/workflows/ci.yml`, Sprint D block in `masterplan.md`.

**2026-08-15 · `record_decision` — `METHODOLOGY.md` is deferred, not forgotten**
> **Why:** it is an S8 deliverable and S8 has not run. Writing the corpus, split, prompt and
> audit protocol now would mean writing it twice, because it has to be revised the moment the
> student's numbers land. `README.md` links `masterplan.md` and this ledger for the protocol
> until then, and says so explicitly rather than leaving a dead link.

**2026-08-15 · `record_decision` — AMENDMENT A4, three feed counts corrected**
> `masterplan.md` A4 records that "61 public RSS feeds" (this appeared in the masterplan's
> one-paragraph version and D3, in `CLAUDE.md` twice, and in the old README) should be **63**;
> that the committed `EXPANSION_FEEDS` is **83**, not the 84 the S2 delta implies; and that the
> expansion adds **15** science feeds, not 17.
> **Why an amendment rather than an edit:** `masterplan.md` is append-only, and A2 is the
> precedent — it corrected a planning figure (19 GB → 22 GB) the same way. `CLAUDE.md` and the
> README are not append-only and were corrected in place.
> **Why nothing measured moves:** every downstream number is computed from the harvested corpus
> or from `feeds.ALL_FEEDS` at runtime, never from these prose counts. `63 + 83 = 146`, which
> matches the "146 feeds attempted" already in S2's `record_verification` — the ledger was
> internally consistent and only the prose was ambiguous, because "84 live" was a probe result
> and 83 is what shipped after `skysports.com` was dropped for introducing a new outlet.
> **The rule it suggests:** a count that exists in code should be cited from code. That is what
> `src/stats.py` → `results/corpus_stats.json` now does for the figures backing the write-up.

---

## S6 — Train (close)

**2026-08-15 · `record_decision` — `num_layers: 16` trains FOUR layers, not sixteen**
> Read off the adapter's own safetensors header, no model load required: 16 tensors,
> **917,504 params (0.918M)**, touching layers **19, 23, 27, 31** only, `self_attn.q_proj` and
> `self_attn.v_proj` on each.
> **Why it happens:** Qwen3.5-4B is a hybrid architecture — `full_attention_interval: 4`, so 24
> of its 32 layers are `GatedDeltaNet` linear-attention blocks with no `self_attn.q_proj` to
> attach to. `num_layers: 16` selects the last 16 layers, of which exactly four carry the
> targeted modules. The config reads as though sixteen layers are tuned; four are.
> **Why it is recorded rather than fixed:** the run is valid and the result is strong. It also
> reconciles the discrepancy with S5's recorded `0.096% (4.058M)`, which came from the probe
> under a different key set. The authoritative figure for S6 is **0.022% (0.918M of
> 4,205.75M)**. "The student learns this task with 0.022% of its parameters trainable" is a
> stronger claim than the one the plan assumed, not a weaker one.

**2026-08-15 · `record_decision` — the student ships from iter 800, not the final iter 1200**
> Validation loss bottomed at **0.075** (iters 500 and 800) and blew out to **0.280** across
> the last 200 iterations; train loss rose with it (0.127 → 0.219), so this is an optimisation
> excursion rather than overfitting. `src/select_checkpoint.py` materialises the chosen
> checkpoint as a loadable adapter directory, which `mlx-lm` does not otherwise provide.
> **Why:** measured at **+8.0 macro-F1** — 0.8400 at iter 800 versus **0.7599** at iter 1200.
> Shipping mlx-lm's default final weights would have discarded a tenth of the model's quality.
> **The leak this could have been, and was not:** selection reads ONLY the 160-example
> validation split carved from the training pool. The held-out 500 take no part — the module
> never opens that file, and it refuses any iteration with no checkpoint on disk (iter 500 also
> hit 0.075 but had none, so it was not selectable). Selecting on the test set would have made
> the project's headline number worthless.
> **Both are published:** `results/summary.json` (iter 800) and
> `results/summary_final_checkpoint.json` (iter 1200), with the full ranking in
> `runs/current/best/selection.json`.

**2026-08-15 · `record_verification` — S6 gate**
> - Loss decreases: train 5.334 → 0.196; val 5.604 → **0.075** at the selected checkpoint — PASS
> - Curve committed: `charts/training_curve.png`, 1,200 train + 13 val points, 4 nan report
>   windows (iters 85, 100, 423, 949) drawn as marked gaps rather than dropped — PASS
> - Adapter loads standalone: 500 held-out predictions, **0 unparseable** — PASS
> - 20 sanity predictions parse: **20/20 valid**, 17/20 agree with the teacher, run against the
>   **merged** weights — PASS
> - Hyperparams + dataset hash recorded: `runs/current/hyperparams.json` — pinned revision,
>   sha256 per split, mlx 0.32.0 / mlx-lm 0.31.3, git commit + dirty flag — PASS
> - Runtime: 1,200 iters at 0.313 it/s ≈ **64 minutes**, inside the brief's 2 h cap — PASS
> - Merged: `models/student-merged`, 7.9 GB, gitignored — PASS
> - Evidence: `runs/current/{train.log,loss.jsonl,hyperparams.json,best/selection.json}`,
>   `charts/training_curve.png`, `results/sanity_20.json`.
> - **Third attempt.** Run 1 died at ~iter 300 (pre-A3). Run 2 reached ~iter 1170/1200 and was
>   killed by a macOS GPU-driver kernel panic that rebooted the machine and cleared `/tmp`,
>   taking its entire loss log. Run 3 logged inside the repo. **Peak memory 43.911 GB of 48 GB.**

---

## S7 — Evaluate (close)

**2026-08-15 · `record_decision` — the cost model reads a measured artifact or refuses to run**
> `src/cost.py` hardcoded four token constants beneath a docstring claiming they were "measured
> with the real tokeniser". They were not. Two were wrong in the direction that flattered the
> headline: student input **32** against a measured **35.98** (the 32 was A3's figure for a
> whole training *example*, a different quantity), and teacher output **10** against a measured
> **6.51**. `src/measure_tokens.py` now derives all four from the real tokeniser over all 500
> held-out rows into `results/token_counts.json`; `cost.py` reads it and raises
> `FileNotFoundError` if it is absent rather than falling back.
> **Why it matters:** the corrected headline is **41.3x cheaper / 2.42% of teacher cost**, not
> the **45.4x / 2.20%** previously committed. A ~9% overstatement of the project's headline
> claim, caught only because the number was checked against the tokeniser it claimed to come
> from. Output counts are weighted by the actual gold label distribution rather than counting
> each class once, since the classes are not equally likely.
> **Disclosed limitation:** the teacher's weights were deleted in S4, so its token counts are
> measured with the student's tokeniser (same Qwen family). That caveat is a field inside
> `token_counts.json`, so it travels with the number.

**2026-08-15 · `record_decision` — the outlet-TIER breakdown is not shipped, and nothing is invented**
> S7 asks for a headline-length and outlet-tier breakdown of student error. Length shipped.
> **Tier did not, because no tier taxonomy exists in this repo** — `Feed` is
> `(outlet, url, section)` and `data/heldout.jsonl` has no `tier` field, so the column would
> have read `unknown` for all 500 rows while looking like a result.
> **Why not just author one:** ranking 54 outlets by editorial prestige would be fabricating
> data to satisfy a checkbox, and every downstream sentence would inherit it. Shipped instead:
> per-outlet agreement (real) and a **volume band** cut on held-out counts, labelled inside the
> artifact as a stated proxy for prominence rather than an editorial judgement.

**2026-08-15 · `record_verification` — S7 gate**
> - Three arms x three metrics — PASS
>   `student macro-F1 0.8400 · accuracy 0.8540 · p50 327.1 ms · p95 402.4 ms · 0 unparseable`
>   `regex   macro-F1 0.3372 · accuracy 0.3420`
>   `teacher quality n/a by construction (84% hand audit) · p50 781.8 · p95 867.7`
>   `cost: teacher $0.1547/1k · student $0.0037/1k · regex $0 — 41.3x, list price, $0 spent`
> - Confusion matrices committed: `charts/confusion_regex.png`, `charts/confusion_student.png` — PASS
> - Error taxonomy in prose: `results/error_analysis.md` — PASS
> - Every number traceable to a committed artifact — PASS
> - **The student loses one class and it leads:** `general` recall 68.2% vs the regex's 98.5%.
>   The regex reaches that at **17.3% precision**, answering `general` for 375 of 500. On F1 the
>   ordering reverses (0.698 vs 0.295) and the student loses no class. Both flags are reported
>   separately so neither framing swallows the other.
> - The student's genuine weakness: **`consumer` recall 52.9%**, most often called `tech` — a
>   milder inheritance of the `Amazon Prime Day → tech` bug this project opens with.
> - Student right where the regex is wrong: **285**. Regex right where the student is wrong: **29**.
> - Evidence: `results/{summary.json,summary_final_checkpoint.json,predictions.jsonl,
>   error_analysis.json,error_analysis.md,token_counts.json,sanity_20.json}`. 139 tests green.

---

## S8 — Writeup (close)

**2026-08-15 · `record_decision` — invented terminal output is a distinct honest-claims failure**
> The rule as written forbids stating a number no committed artifact can back. It does not
> obviously forbid **plausible-looking terminal output that was never captured**, which is a
> different failure with the same shape. It occurred: a Usage block was drafted with
> `[eval] student 100/500` progress lines labelled "captured verbatim" for a run that session
> had never performed. It was caught and replaced before publication, by its own author.
> **Rule adopted:** anything resembling a transcript is reproduced from a committed artifact
> and labelled as reproduced, or it does not appear. `METHODOLOGY.md` contains no transcripts.
> **Why it is recorded rather than quietly fixed:** the near-miss is the useful part. A number
> that cannot be backed is easy to challenge; fabricated output looks like evidence.

**2026-08-15 · `record_verification` — S8 gate**
> - `README.md` passes the brief's five rules — PASS
> - `METHODOLOGY.md` written: task · corpus · split protocol · teacher and prompt · the 84%
>   noise ceiling · what gold-is-a-model costs · training · evaluation · error analysis ·
>   limitations · artifact index — PASS
> - Every number traceable to a committed artifact — PASS. 29 README numbers re-verified
>   against artifacts with zero mismatches; every figure in `METHODOLOGY.md` re-checked against
>   its artifact before close (`consumer` n=34 / F1 0.679 / recall 52.9%; `general` F1 0.698 vs
>   0.295; regex `general` precision 17.3%; 63 feeds; the 0.7222-vs-0.2708 scoring convention).
> - Limitations prominent, not appended — PASS. "Where the student loses" sits directly under
>   the results table, ahead of any material about the incumbent.
> - No amber in any chart — PASS, and now enforced by `tests/test_charts_guard.py` over both
>   source and committed pixels. `charts.py` had claimed "a test asserts this" while no such
>   test existed; the claim is now true.
> - The student loses `general` on recall and it leads the README — PASS
> - Evidence: `README.md`, `METHODOLOGY.md`, `PROJECT.json`, `charts/*.png`, `results/*`.
>   139 tests green.

**2026-08-15 · `share_intent` — S9 is Bruno's alone**
> S0–S8 are closed. Everything remaining requires money, publication, or an irreversible
> external action, and per D8 none of it runs without the owner: pushing weights or the dataset
> to Hugging Face, making the repo public, and the optional paid teacher-strength ablation.
> Nothing has been published. No remote exists. `git-lfs` and `huggingface-cli` are still
> uninstalled, deliberately — S9 installs them if and only if a gate is approved.

---

## S9 — Owner gates (in progress — 2 of 4 answered)

**2026-08-15 · `ask_human` — make the GitHub repo public? → APPROVED, and executed**
> **https://github.com/br9704/distillation** is public. Five commits, CI green on `macos-14`
> in 32 s, licence detected as MIT.
> **Pre-publication scan, run before the irreversible step:** no `.env`, no `.mcp.json`, no
> credential patterns in tracked content, nothing sensitive ever added in history, and the
> aethereum room id and join code correctly absent — the two hits that looked sensitive were
> false positives on the word *token* (`results/token_counts.json`, `src/measure_tokens.py`,
> both about tokeniser tokens). Every Supabase mention is a path reference or a statement that
> the key was deliberately not used.
> **Two defects found and fixed before publishing:** `LICENSE` was valid MIT with eleven lines
> of third-party attribution appended, which GitHub's detector cannot parse past — the repo
> published as licence "Other" until the notices moved to `NOTICE.md`. And the README still
> told readers `METHODOLOGY.md` "is deliberately not written yet" while that file sat committed
> beside it, a staleness introduced by the S8 commit itself.
> **Disclosed to the owner:** the commit history carries `jaamaabruno@gmail.com` publicly and
> is irreversible without a history rewrite. It matches the `br9704` GitHub identity.

**2026-08-15 · `ask_human` — push weights to Hugging Face? → DEFERRED**
> Bruno: "we defer it." Deferred rather than declined, so it stays available at any time.
> **What deferring costs, stated plainly so the decision is on the record:** exactly one thing —
> third-party corroboration. An adapter repo with `base_model:` metadata makes HF render
> "finetuned from Qwen3.5-4B" and list it in that model's family tree, which is evidence of
> training that lives somewhere other than a repo the author wrote himself. **No claim in the
> README or `METHODOLOGY.md` depends on it**, and nothing is blocked.
> **Recommendation on file, independent of the deferral:** if it is ever done, publish the
> ~4 MB adapter only. The 7.9 GB merged weights save a reader a single `mlx_lm fuse` command
> and are a maintenance liability rather than a contribution.
> `git-lfs` and `huggingface-cli` remain deliberately uninstalled.

**2026-08-15 · `ask_human` — publish the labelled dataset? → STILL OPEN**
> Deliberately **not** inferred from the Hugging Face deferral: they are separate gates and
> were not asked together. Recommendation on file is to keep it local — `data/` being gitignored
> keeps the repo reviewable, and the labels regenerate from `src/harvest.py` + `src/teacher.py`.

**2026-08-15 · `ask_human` — optional paid teacher-strength ablation (~$5–15)? → STILL OPEN**
> Cannot proceed by inference in any case: it needs an account and API key the agent does not
> hold. **Counter-recommendation:** a second training seed is the better spend. It costs only
> local GPU time and closes the single-sample limitation — currently the one gap in the write-up
> a reviewer can legitimately attack, since the +8.0 checkpoint-selection delta and every
> per-class figure rest on one run.
