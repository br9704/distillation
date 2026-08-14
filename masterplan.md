# masterplan.md — distillation

> **Current sprint: S3 — Teacher setup and pilot** _(S0–S2 closed 2026-08-14)_
>
> Work only the active sprint. Mark tasks live: `[ ]` not started · `[~]` in progress ·
> `[x]` complete · `[⏭]` deferred (one-line reason). **Never delete or rewrite content in
> this file — expand it in place.** A sprint is not done until its **Acceptance** block
> passes, its **As-shipped delta** and **Deferred** blocks are filled, the Current-sprint
> pointer above has moved, and `CLAUDE.md`'s Current-state line is updated.

---

## The one-paragraph version

Sentinel (Bruno's live iOS news-intelligence product) classifies every ingested news
headline into one of eight topic classes. In production that classifier is a keyword
regex — `classifyWireItem()` in `AI REPORTING APP MVP/supabase/functions/_shared/wire.ts:353`
— and it is structurally broken in ways visible in its own source. We rebuild that corpus
from the same 61 public RSS feeds the product reads, label ~5,000 headlines with a large
open-weight teacher running locally, LoRA fine-tune a ~4B open model on those labels, and
report quality, cost and latency for **three** arms — regex, teacher, student — on 500
headlines that were held out before a single label was generated.

The deliverable is the trade-off curve, not parity.

---

## Locked decisions (do not relitigate)

| # | Decision | Why |
|---|---|---|
| D1 | **Task: 8-class wire topic classification.** Classes exactly as in `wire.ts`: `geopolitics` · `finance` · `tech` · `sports` · `entertainment` · `science` · `consumer` · `general` | Crisp right answer, auto-scorable, real production feature. The brief's selection rule is non-negotiable and this passes it. |
| D2 | **Teacher: open-weight, `Qwen/Qwen3.5-35B-A3B` Q4_K_M, run locally.** | ENGINEERPROMPT §Decisions-locked mandates open weights (zero ToS risk, publishable). MoE with ~3B active ⇒ fast on M4 Pro. Apache-2.0. $0, no owner gate. |
| D3 | **Corpus: rebuilt from the 61 production RSS feeds + GDELT backfill.** | Same distribution as production with **zero credentials and zero user data**. No privacy disclosure burden, nothing blocks on a key. |
| D4 | **Three arms, not two.** regex · teacher · student. | The regex is the real incumbent. Benchmarking only against the teacher would pick the flattering baseline — the exact credibility failure the brief warns about. |
| D5 | **Cost is list-price arithmetic, explicitly labelled as such.** | Everything runs locally at $0. Asserting a measured dollar figure would be dishonest. Latency *is* genuinely measured. |
| D6 | **Training framework: MLX (`mlx-lm`).** | Unsloth and bitsandbytes are CUDA-only. MLX is the native Apple-silicon path. TRL/peft on MPS is slow and flaky. |
| D7 | **Macro-F1 is the headline metric, not accuracy.** | `general` is a catch-all and will dominate. Accuracy would flatter every arm equally and hide tail-class failure. |
| D8 | **All owner-gated work is deferred to S9.** | Bruno's instruction. S0–S8 run free and unattended. |
| D9 | **No QLoRA.** LoRA r=16, bf16. | Brief: Unsloth recommends against QLoRA for Qwen3.5 (quantization artifacts); at 4B/bf16 the memory is available anyway, so it buys nothing. |

## Non-goals (hard boundaries, from the brief)

No full fine-tune (LoRA only) · no multi-task model (one narrow task) · no serving
infrastructure or deployment · no RLHF/DPO/preference alignment · **do not try to beat the
teacher** · do not chase parity.

---

## Verified facts (Aug 2026 — re-verify anything load-bearing at the sprint that uses it)

- `Qwen/Qwen3.5-4B` — Apache-2.0, sha `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`,
  `Qwen3_5ForConditionalGeneration`, **multimodal** (image+video preprocessors),
  hybrid attention (`linear_attention` ×3 : `full_attention` ×1, 32 layers),
  hidden 2560, head_dim 256, 262K ctx, 7.5M downloads.
- Qwen3.5 family: dense `0.8B · 2B · 4B · 9B · 27B`; MoE `35B-A3B · 122B-A10B · 397B-A17B`;
  plus FP8 and GPTQ-Int4 variants. `-Base` variants exist for 0.8B/2B/4B/9B/35B-A3B.
- Teacher quants: `unsloth/Qwen3.5-35B-A3B-GGUF` (Apache-2.0) ships
  `Q3_K_S · Q3_K_M · Q4_K_M · Q5_K_M · Q8_0 · UD-Q3_K_XL · UD-Q4_K_XL · UD-Q8_K_XL`.
  Also `bartowski/Qwen_Qwen3.5-35B-A3B-GGUF`.
- MLX conversions exist: `mlx-community/Qwen3.5-4B-bf16`, `mlx-community/Qwen3.5-4B-8bit`.
- `mlx` 0.32.0 · `mlx-lm` 0.31.3 (requires_python >=3.8).
- Fallback base models, all confirmed to exist: `Qwen/Qwen3.5-2B`,
  `Qwen/Qwen3-4B-Instruct-2507` (standard text-only arch), `HuggingFaceTB/SmolLM3-3B`,
  `google/gemma-4-E2B-it`, `mistralai/Ministral-3-3B-Instruct-2512`.
- GDELT DOC 2.0 API is reachable and free; **rate limit is 1 request / 5 seconds** and it
  says so in the error body. Respect it.
- RSS smoke test: BBC 36 items · Guardian 45 · CNBC 30 · Axios 3. Expect ~30–45/feed.

### Machine (the constraints that actually bind)

| | |
|---|---|
| CPU / RAM | Apple M4 Pro, 14 cores, **48 GB unified** — ample |
| **Free disk** | **34 GB** — this is the binding constraint on the whole project |
| System Python | 3.14.6 — **too new for the ML wheels**; S0 pins 3.12 via `uv` |
| Node | v24.12.0 |
| Already installed | `ollama` (models: `llama3:8b-instruct-q4_K_M`, `dolphin-llama3:8b` — both too weak to be the teacher) |
| Missing | `uv` · `git-lfs` · `huggingface-cli` · `modal` · `pnpm` |

### Disk sequencing — load-bearing, drives the sprint boundaries

Naïve ordering overflows: 19 (teacher) + 8 (base) + 8 (merged) + 2 (env) = **37 GB > 34 GB**.

```
S2  harvest corpus                        ~0.1 GB
S3  pull teacher Q4_K_M                   +19 GB     peak ≈ 21 GB
S4  label 5,000 · teacher latency run
S4  DELETE teacher                        −19 GB     labels are on disk; teacher re-pullable
S5  pull student base bf16                 +8 GB
S6  train LoRA (+adapter ~50 MB) · merge   +8 GB     peak ≈ 18 GB
```

**Teacher latency is measured before deletion**, in a dedicated sequential single-request
run over the held-out 500 — never inferred from batched labelling throughput.

---

# S0 — Foundation

**Goal:** the repo is a repo, the rules exist, and the toolchain runs. No ML yet.

- [x] `git init` (done pre-sprint) · `.gitignore` covering `.venv/`, `data/`, `models/`, `runs/`, `*.gguf`, `.env*`, `__pycache__/`
- [x] Author `CLAUDE.md` — constitution, modelled on `ctxbench/CLAUDE.md` and `mcpaudit/CLAUDE.md`
- [x] Author this file (`masterplan.md`)
- [x] ccline statusline into `./.claude/settings.json` (`npx ccline-cli install`) — **project scope, merge-only, preserve every other key**
- [x] Install `uv`; create `.venv` on **Python 3.12** (not system 3.14) → `uv` 0.12.4, Python 3.12.13
- [x] `pyproject.toml` — deps pinned: `mlx`, `mlx-lm`, `httpx`, `pydantic`, `matplotlib`, `pytest`
- [x] `SYNC.md` — the aethereum sync ledger (see below)
- [x] `README.md` stub — one sentence + "results pending", so the repo is never nameless
- [x] Directory skeleton (see Architecture index in `CLAUDE.md`)

### aethereum sync — how it actually works here

The sync verbs (`share_intent`, `declare_contract`, `record_decision`, `ask_human`,
`record_verification`) are **MCP tools**, served by the aethereum MCP server. They are
**not connected in this session** — an MCP server cannot be hot-added mid-session.

Resolution, chosen deliberately over blocking:
- [x] `npx aethereum@0.9.9 init` in the repo root; join/create the project room
      → room `distillation`. Room id and join code are **not committed** — the join code grants
      room access and this repo is a candidate for going public at S9. `aethereum status`
      recovers them locally.
- [x] Every sync event is written to `SYNC.md` as a timestamped ledger entry **now**, in the
      canonical verb form, and replayed through the real tools once the server is live
- [x] Rationale: aethereum's own handlers all fail soft (`OFFLINE` sentinel, never throw).
      A local ledger is the same contract. Blocking the whole project on an MCP
      reconnection would be the wrong call.

**Acceptance:** `uv run python -c "import mlx"` succeeds on 3.12 · ccline renders a line ·
`SYNC.md` holds the S0 `share_intent` and D1–D9 `record_decision` entries · `git log` has
one clean foundation commit. — **PASSED**

**As-shipped delta:**
- `uv` 0.12.4; venv on Python **3.12.13**. MLX verified executing on `Device(gpu, 0)` —
  a real Metal check, not just an import. `mlx-lm` 0.31.3, `transformers` 5.15.0.
- `aethereum init` wired far more than expected: `.mcp.json` (aethereum + aethereum-channel,
  pre-approved), Claude Code hooks, Cursor/Codex/opencode/Copilot configs, `AGENTS.md`,
  `GEMINI.md`, and a `.git/hooks/pre-commit` running `aethereum check` (advisory). It
  detected ccline's statusline and **kept it** rather than overwriting — no conflict.
- Those generated MCP config files carry a room token, so they were added to `.gitignore`.
  `AGENTS.md` and `GEMINI.md` are safe to commit.
- **Confirmed the plan's assumption:** the aethereum MCP tools are wired but not callable
  until the next session, so `SYNC.md` is the live ledger with `Replay status: PENDING`.
- Added `configs/` to the skeleton (S6 needs `configs/lora.yaml`).

**Deferred:**
- `[⏭]` Global `npm i -g aethereum` + `aethereum listen --install-service` — init warned the
  npx-cached login service will not survive a reboot. Delivery works while a session is open,
  which is all this project needs; installing globally is a machine-level change and is not
  S0's business.
- `[⏭]` `git-lfs` and `huggingface-cli` — not needed until the S9 publish gate. Installing
  them now would be preparing for a gate that may be declined.

---

# S1 — Contracts and scoring, before a single label exists

**Goal:** the label schema and the scoring function are frozen *before* any labelling. The
brief is explicit that this ordering is not optional.

- [x] `src/schema.py` — `TOPIC_CLASSES`, the 8 exact strings, copied verbatim from `wire.ts:350–380`
- [x] `Example` — `{id, headline, outlet, url, published_at, source_feed, split}`
- [x] `Label` — `{id, label, teacher_model, teacher_revision, prompt_version, latency_ms, raw_output}`
- [x] `Prediction` / results JSONL — `{id, arm, pred, gold, latency_ms}`; `arm ∈ {regex, teacher, student}`
- [x] `src/scoring.py` — accuracy · **macro-F1** · per-class P/R/F1/support · confusion matrix
- [x] `src/regex_baseline.py` — a faithful Python port of `classifyWireItem`, **including its
      ordering bug** (the `if` chain returns on first match). Port the behaviour, not the intent.
- [x] `tests/test_scoring.py` — hand-built confusion fixture with a known macro-F1
- [x] `tests/test_regex_baseline.py` — parity cases pinning the known quirks:
      `"Amazon Prime Day"` → `tech` (not `consumer`, because `amazon` matches the tech rule first),
      `"SpaceX launch"` → `tech` (not `science`), any headline containing `china` → `geopolitics`
- [x] `declare_contract` for `Example`, `Label`, `Prediction`

**Acceptance:** `pytest` green · macro-F1 verified by hand against the fixture ·
the three regex quirks are pinned by passing tests · contracts in `SYNC.md`. — **PASSED**
(38 tests, 0.32s)

**As-shipped delta:**
- **Two extra defects found while porting**, beyond the three the plan anticipated, so five
  are now pinned: `target` in the consumer rule is unreachable in practice, and `general` is
  structurally a catch-all rather than a class — the second is the standing justification
  for D7 (macro-F1 over accuracy).
- **`re.ASCII` is required for a faithful port** and this was not anticipated. JavaScript's
  `\b` is ASCII-based; Python's is Unicode-aware by default. Verified empirically:
  `"iraníes protest in the capital"` matches the geopolitics rule under `re.ASCII` and does
  not under Python's default. Without the flag the incumbent arm would have been quietly
  weaker than the thing actually running in production. The corpus includes DW, France24,
  SCMP and Haaretz, so this is a live concern rather than a curiosity.
- **Macro-F1 averaging convention made explicit and test-pinned.** Averaging over present
  classes only would read 0.7222 on the S1 fixture against our 0.2708. Scoring is implemented
  from first principles (~60 lines, no scikit-learn) specifically so this choice is visible
  in the repo rather than inherited from a library default.
- Added `UNPARSEABLE` to `schema.py` with the scorer raising if it ever reaches it — the
  no-silent-coercion rule is now enforced by code, not just documented.
- Added `percentile()` (nearest-rank) and `confusion_pairs()` to `scoring.py` now rather
  than in S7, since both are contracts the later sprints consume.
- Added `CLASS_DEFINITIONS` beside `TOPIC_CLASSES` with an `assert` tying them together, so
  the S3 teacher prompt cannot drift from the label space.

**Deferred:**
- `[⏭]` Chart styling helpers (`src/charts.py`) — first needed by S2's class-distribution
  chart. Building the Aethereum-token matplotlib theme with no data to render would be
  guesswork.

---

# S2 — Corpus (zero credentials, zero user data)

**Goal:** ≥5,500 unique headlines matching production distribution, with 500 held out
**before** anything is labelled.

- [x] `src/feeds.py` — all 63 feed URLs extracted from `wire.ts:34–115`, with outlet + section
- [x] `src/harvest.py` — async RSS fetch, `SentinelBot/1.0` UA, per-feed failure is
      logged and skipped (never fatal); parse `<item>` → title, link, pubDate
- [x] `src/rss.py` — RSS 2.0 + Atom parser ported from `wire.ts:213–299`
- [x] `src/store.py` — URL normalisation, stable ids, JSONL persistence
- [x] Dedup: exact URL, then normalised title (lowercase, strip punctuation/whitespace)
- [x] `src/gdelt.py` — backfill filtered to the same outlet domains, politeness by sleep,
      never retry-on-429 → **written and working, but `[⏭]` in practice: see Deferred**
- [x] `src/feeds.py::EXPANSION_FEEDS` — same-outlet section feeds (**not in the plan**; see delta)
- [x] Repeat harvest passes over the build window; append-and-dedup into `data/corpus.jsonl`
- [x] **Split first, label never:** `src/split.py` writes `data/heldout.jsonl` (500) and
      `data/train_pool.jsonl`. Assert disjointness on URL hash and fail loudly if violated.
- [x] Split membership is **frozen on first run** — re-running extends the training pool only
- [x] `src/charts.py` — Aethereum design tokens as a matplotlib theme; Geist vendored (OFL-1.1)
- [x] `charts/class_distribution.png` — regex-label distribution, Aethereum tokens
- [x] `tests/test_corpus.py` — 21 tests: catalog integrity, parsing, dedup keys, split disjointness
- [x] Record: per-feed yield, dedup rate, final counts

**Acceptance:** ≥5,500 unique rows _(**amended → ≥3,500**, see AMENDMENTS A1)_ · held-out is
exactly 500 and provably disjoint (asserted) · all 8 classes present in held-out
_(**deferred to S4** — only the teacher's labels can settle this; the regex is a weak proxy
and assigns zero held-out examples to `consumer`)_ · distribution chart committed · counts in
`SYNC.md` `record_verification`. — **PASSED as amended**

**Risks:** tail classes (`consumer`, `sports`, `entertainment`) may be genuinely rare in
these hard-news feeds. If a class has <20 held-out examples, say so in the limitations
section rather than synthesising examples to pad it.

**As-shipped delta:**
- **The headline number: the incumbent regex sends 74.2% of the corpus to `general`.**
  It puts only a quarter of real headlines into a real class. This was the sprint's most
  valuable finding — it is the project's premise, measured, and it retroactively justifies
  D7 (macro-F1 over accuracy) far more strongly than the argument that produced D7.
- **`EXPANSION_FEEDS` was not in the plan and is the reason the corpus works.** One pass
  over the 63 production feeds yields ~1,800 unique headlines and a second immediate pass
  yields **7** — the feeds simply have not cycled. Three options were weighed and option 3
  chosen (full reasoning in `src/feeds.py`): GDELT backfill, many passes over hours, or
  section feeds from outlets already in the catalog. The expansion preserves what actually
  defines the distribution — the outlets — and an `assert` in `feeds.py` plus a test
  enforce that no new outlet is ever introduced. One working candidate (`skysports.com`)
  was dropped solely for failing that rule. 86 candidates probed, 84 live, +1,890 rows.
- **The expansion also fixed the tail-class problem at its source.** The production catalog
  carries 3 sports and 4 science feeds against 16 general; the expansion adds 11 sports and
  17 science. Held-out section coverage: entertainment 51 · sports 44 · science 68.
- **Split membership is frozen on first run** — not in the plan, added because harvest keeps
  running after the split. Growing the training pool can never leak into the held-out set;
  re-drawing the held-out set after labelling had begun could. Now impossible by
  construction rather than by remembering not to. A second leakage assert catches identical
  headlines appearing in both splits under different URLs.
- **`src/charts.py` built here rather than deferred**, since the chart needed it. Every value
  is transcribed from `hive/apps/web/styles/tokens.css` — nothing invented. The `--id-ring-1..8`
  agent-identity palette turned out to be an exact fit for the eight classes: eight tokens,
  mutually distinguishable by design, and deliberately excluding green and amber because both
  are load-bearing signal colours. Geist TTFs vendored into `assets/fonts/` (SIL OFL-1.1,
  licence included) so charts reproduce without depending on the hive repo's path.
- **Feed bitrot measured**: of 146 feeds, 6 return 4xx (`haaretz` 403, `ctvnews` 404,
  `yahoo` 403, `bleacherreport` 404, `scientificamerican` 404, `theverge` tech 404) and 5
  parse to zero items. All five were checked by hand and are **correct behaviour, not parser
  bugs**: `usatoday` and `rferl` now serve HTML/an error, `huffpost`'s channel is empty, and
  **`nhk.or.jp` is a podcast feed** whose items are episode titles with no article link —
  a live defect in the production catalog worth reporting back to the product.
- Corpus: **3,706 unique** from 54 live outlets. Held-out 500 spanning 53 outlets, disjoint.

**Deferred:**
- `[⏭]` **GDELT backfill — written, tested, and unusable on this network.** It throttles far
  beyond its documented 1-req/5s: one request succeeds, then every subsequent request returns
  HTTP 429 regardless of spacing, including at 65s. Zero rows contributed over 20 minutes of
  patient trickling. It also under-delivers when it does answer (52 articles against a
  requested 250). `src/gdelt.py` is kept because the code is correct and a fresh IP or a
  later day would work — the failure is a rate-limit penalty box, not a bug. The corpus does
  not depend on it.
- `[⏭]` All-8-classes-in-held-out check → re-verified at S4 against teacher labels. The regex
  proxy assigns zero held-out examples to `consumer`, which is a fact about the regex, not
  about the corpus.

---

# S3 — Teacher setup and pilot

**Goal:** a teacher that answers with one of eight strings, reliably, at a known speed.

- [~] `ollama pull hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M` (verify actual on-disk size against
      the 19 GB budget before committing to it; drop to `Q3_K_M` only if it does not fit)
      → **actual size is 22 GB, not the budgeted 19 GB.** Against 31 GB free that leaves
      ~9 GB headroom, which is enough (labels are kilobytes) but tighter than planned. See A2.
- [x] `src/teacher.py` — prompt v1: the 8 classes with the one-line definition each, the
      headline, the outlet; instruction to answer with exactly one class string
- [x] Constrained output: parse strictly, retry once with a stricter prompt, then mark
      `UNPARSEABLE` — never silently coerce to `general` (that would bias the teacher toward
      the majority class and corrupt the ceiling)
      → upgraded to **JSON-schema-constrained decoding** with an enum over the 8 classes, so
      the sampler cannot emit anything else. `UNPARSEABLE` is retained for transport-level
      failures and is still reported.
- [x] `tests/test_teacher.py` — 21 tests on prompt integrity and the parser's refusal to guess
- [x] HTTP path smoke-tested end-to-end against `llama3:8b` before the teacher landed, so the
      API contract (`/api/chat`, `format` schema, `think: false`) was proven independently
- [x] **Cold-start discovered and handled**: first call 5,184 ms vs ~500 ms warm — pure
      weight loading. `latency_run` now discards 3 warm-up calls, because including cold start
      in p95 measures the cost of *starting* a server, not of serving a request, and both arms
      in the comparison are served warm.
- [ ] Self-consistency probe: 100 headlines × 3 samples at temp 0 and temp 0.7 → report agreement
- [ ] Pilot 100 labels; eyeball them; iterate the prompt; **freeze `prompt_version`**
- [ ] `record_decision`: final prompt version, quant, decoding params

**Acceptance:** ≥98% of pilot outputs parse to a valid class · self-consistency reported ·
prompt frozen and versioned · throughput measured so S4's runtime is predictable, not a guess.

**As-shipped delta:** _(fill at close)_
**Deferred:** _(fill at close)_

---

# S4 — Label, audit, measure, then reclaim the disk

**Goal:** ~5,000 training labels, a known noise ceiling, and the teacher's real latency —
captured before the weights are deleted.

- [ ] Label `data/train_pool.jsonl` (~5,000) — unattended, resumable (checkpoint every 100,
      keyed by id, so a crash costs one batch not the run)
- [ ] Label the held-out 500 → `data/heldout_labels.jsonl` (this is the gold set for every arm)
- [ ] **Hand-audit 50 held-out labels.** I adjudicate; disagreements are itemised, not just counted.
      This number is the ceiling — the student cannot meaningfully exceed it.
- [ ] **Teacher latency run:** held-out 500, sequential, one request at a time, no batching.
      Record p50 and p95. This is the honest measurement; batched throughput is not latency.
- [ ] `charts/label_distribution.png` — teacher labels vs regex labels, side by side. The
      divergence here is itself a finding.
- [ ] Confusion matrix: regex vs teacher on the held-out 500 → the incumbent's error profile
- [ ] `ollama rm` the teacher; verify reclaimed space with `df`
- [ ] `record_verification`: counts, audit agreement, p50/p95, disk before/after

**Acceptance:** ≥4,800 valid labels · `UNPARSEABLE` rate reported (not hidden) · 50-example
audit agreement reported as an explicit ceiling · teacher p50/p95 recorded · ≥18 GB reclaimed.

**As-shipped delta:** _(fill at close)_
**Deferred:** _(fill at close)_

---

# S5 — Base-model architecture probe (a real gate, not a formality)

**Goal:** find out whether `mlx-lm` can LoRA-tune `Qwen3.5-4B` *before* committing the
training sprint to it.

`Qwen3.5-4B` is `Qwen3_5ForConditionalGeneration` — multimodal, with hybrid
linear/full attention. `mlx-community` conversions exist, which is encouraging but not proof
that `mlx_lm.lora` handles the arch.

- [ ] 20-example smoke fine-tune. Success = the run completes, loss decreases, the adapter
      loads, and 5 predictions parse to valid classes.
- [ ] Fallback ladder — take the first that passes, `record_decision` on the choice:
  1. `Qwen/Qwen3.5-4B` (preferred — matches the brief)
  2. `Qwen/Qwen3.5-2B` (same family, smaller)
  3. `Qwen/Qwen3-4B-Instruct-2507` (**standard text-only arch — the safe option**)
  4. `HuggingFaceTB/SmolLM3-3B`
- [ ] Pin the exact revision SHA of whichever wins
- [ ] If the winner is not #1, note in the README why — the reason is interesting, not embarrassing

**Acceptance:** one base model chosen, revision pinned, smoke run reproducible from a
committed command · decision and rationale in `SYNC.md`.

**As-shipped delta:** _(fill at close)_
**Deferred:** _(fill at close)_

---

# S6 — Train

- [ ] `src/train.py` / `configs/lora.yaml` — LoRA **r=16**, bf16, 3 epochs, lr + schedule logged
- [ ] Chat-formatted examples using the frozen `prompt_version` from S3 — **the student must see
      the same prompt shape the teacher saw**, or the comparison is not clean
- [ ] Train/valid split inside the training pool (held-out is never touched)
- [ ] Log every step's loss to `runs/<id>/loss.jsonl`
- [ ] `charts/training_curve.png` — committed. The brief calls a missing loss curve the first
      thing a reviewer notices.
- [ ] `runs/<id>/hyperparams.json` — every hyperparameter, base-model revision, dataset hash,
      prompt version, mlx/mlx-lm versions
- [ ] Merge adapter → `models/student-merged/`
- [ ] Runtime target ~15–60 min. If it heads past 2 h, stop and reduce — the brief caps this.

**Acceptance:** loss decreases and the curve is committed · adapter loads standalone ·
20 sanity predictions parse to valid classes · hyperparams + dataset hash recorded.

**As-shipped delta:** _(fill at close)_
**Deferred:** _(fill at close)_

---

# S7 — Evaluate (this is what separates a training script from an evaluation)

**Goal:** all three metrics, all three arms, one harness, every number regenerable.

- [ ] `src/evaluate.py` — one harness, three arms, the same 500 held-out examples,
      the same machine, gold = teacher labels (with the audit-derived ceiling stated alongside)
- [ ] **Quality** — accuracy, **macro-F1**, per-class P/R/F1, confusion matrix per arm
- [ ] **Latency** — p50 **and** p95, measured by this harness, sequential, single request.
      Student measured here; teacher's numbers come from the S4 run on the identical set.
- [ ] **Cost** — per 1,000 requests, arithmetic shown line by line, **explicitly labelled
      list-price** (all local runs cost $0). Show the token counts the arithmetic uses.
- [ ] **Error analysis, the part most people skip:**
  - [ ] Confusion matrix → the top 5 confused pairs
  - [ ] Error taxonomy by cause, not just by class
  - [ ] Prose: *where and why* the student loses. "It confuses `tech` and `science` on
        space-launch headlines" beats any aggregate number.
  - [ ] The inverse: cases where the **student beats the regex badly** — that is the product argument
  - [ ] Headline-length and outlet-tier breakdowns of student error
- [ ] `results/summary.json` — every number the README will cite
- [ ] One command regenerates all of it

**Acceptance:** three arms × three metrics, all present · confusion matrices committed ·
error taxonomy written in prose · every README number traceable to `results/summary.json`.

**As-shipped delta:** _(fill at close)_
**Deferred:** _(fill at close)_

---

# S8 — Writeup

- [ ] `README.md` per the brief's five rules: one sentence · **results table above the fold** ·
      one-line run command · architecture · **prominent limitations**
- [ ] Charts in the inherited Aethereum design system (`hive/apps/web/styles/tokens.css`):
      Geist / Geist Mono, `#34C759` accent, near-black field, 0.5px hairlines.
      **Amber `#FF9500` is reserved for collision alerts and must not appear.**
      Bruno designs nothing — this is inherited, not invented.
- [ ] `METHODOLOGY.md` — corpus construction, split protocol, prompt, teacher noise audit,
      why gold is teacher-labelled and what that costs us
- [ ] **Limitations, prominent and honest:**
      teacher-label noise ceiling (with the measured number) · single task · 500-example
      held-out set · headline-only, no article body · English-only · distribution shift
      (feeds move) · gold labels come from the teacher, so student-vs-teacher agreement is
      not the same as correctness · list-price cost arithmetic, not measured spend
- [ ] Honest-claims rule: **no number in the README that a committed artifact cannot back**
- [ ] If the student loses to the regex on any class, that leads — it does not get buried

**Acceptance:** README passes all five rules · every number traceable · limitations section
is above the fold-adjacent, not appended at the bottom · no amber in any chart.

**As-shipped delta:** _(fill at close)_
**Deferred:** _(fill at close)_

---

# S9 — [ALL OWNER GATES] — nothing here runs without Bruno

Everything requiring money, publication, or an irreversible external action lives here and
nowhere else. S0–S8 complete without a single gate.

- [ ] `ask_human` — push weights to Hugging Face?
  - [ ] Adapter repo (few MB) with `base_model:` metadata so HF renders the lineage widget
  - [ ] Merged weights repo
  - [ ] Model card YAML: `license`, `base_model`, `pipeline_tag`, `tags`, `datasets`, `library_name`
  - [ ] **Disclose the labelling source** — teacher model, revision, prompt version
  - [ ] Requires `git-lfs` + `huggingface-cli` (not yet installed — S9 installs them)
- [ ] `ask_human` — make the GitHub repo public?
- [ ] `ask_human` — publish the labelled dataset, or keep it local? (It is derived from public
      RSS headlines, so this is a choice rather than a constraint.)
- [ ] `ask_human` — optional paid ablation: re-label on a hosted `Qwen3.5-122B-A10B` /
      `397B-A17B` (~$5–15) to produce a **teacher-strength curve**. Strictly better story if
      approved, entirely skippable if not.

**Acceptance:** every gate explicitly answered by Bruno — approved or declined — and the
answer recorded. A declined gate is a completed task, not a failure.

**As-shipped delta:** _(fill at close)_
**Deferred:** _(fill at close)_

---

## BACKLOG (explicitly not this project)

- Teacher-strength ablation curve beyond the single S9 point
- Enriching the corpus with the real `wire_items` production history (needs a Supabase key
  and a provenance disclosure — deliberately avoided in D3)
- Shipping the student as a `ccline` segment or hook — **violates the no-serving-infrastructure
  non-goal.** Noted only.
- RIPPLE sequel: same pipeline, civic imagery, EfficientNet-Lite0 → int8 `.tflite` on-device
  (flagged in ENGINEERPROMPT §Decisions-locked as a natural follow-on, not this project)
- Article-body classification instead of headline-only
- Multilingual — the feeds include DW, France24, NHK, SCMP, Haaretz

## AMENDMENTS

> Append-only. Every material change to a locked decision lands here with a date and a why.

**A1 · 2026-08-14 · Corpus target lowered from ≥5,500 to ≥3,500 unique headlines.**

The 5,500 figure was set during planning, before any feed had been measured, on an estimate
of "61 feeds × ~35 items × repeat passes". Measurement changed the picture: a first pass
yields ~1,800 unique, and a second pass fifteen minutes later yields **7**, because RSS
feeds carry a rolling window that has not moved. Volume therefore comes from breadth (more
feeds) or from patience (hours), not from more passes.

Breadth was exploited as far as it honestly could be — `EXPANSION_FEEDS` added 84 live
section feeds from outlets already in the catalog, worth +1,890 rows. The remaining lever
was GDELT, which turned out to be unusable (see S2 Deferred).

Landing at **3,706**: the brief asks for "3,000–5,000 labels" plus "~500 held out", so
3,206 training + 500 held out satisfies it as written. The alternative — spending several
more hours harvesting for a target this repo set for itself rather than one the brief set —
would buy a larger number and nothing else.

A background harvester continues opportunistically. Because split membership is frozen on
first run, every row it adds goes to the training pool and none can reach the held-out set,
so growth after this point is safe by construction.

**What this costs, stated plainly:** ~3,200 training examples rather than ~5,000 is a
smaller distillation set, and the honest expectation is a slightly weaker student —
particularly on the tail classes. That is a limitation for S8 to report, not a number to
quietly round up.

**A2 · 2026-08-14 · Teacher on-disk size is 22 GB, not the budgeted 19 GB.**

The disk-sequencing plan assumed ~19 GB for `Qwen3.5-35B-A3B` at Q4_K_M. The actual Ollama
pull is **22 GB**, leaving ~9 GB free rather than ~13 GB during S3–S4.

This does not break the plan, because the sequencing is what protects the budget rather than
the specific number: labels are kilobytes, so nothing else grows while the teacher is
resident, and S4 still ends by deleting it before the student is pulled. Revised peaks:

```
S3-S4  teacher resident              22 GB   → ~9 GB free   (was ~13 GB)
S4     DELETE teacher               −22 GB   → ~31 GB free
S5-S6  student base + merged + adapter 16 GB → ~15 GB free
```

Two options were available and neither was taken. Dropping to `Q3_K_M` (~17 GB) would buy
headroom by degrading the teacher, and the teacher is the ceiling for everything downstream —
a worse teacher is a worse project. Deleting the two pre-existing Ollama models
(`llama3:8b`, `dolphin-llama3:8b`, 9.6 GB together) would free plenty, but they are Bruno's
and this project does not delete a user's models to make room for itself. If the disk does
become binding, that is the option to raise with him rather than act on.
