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
