# masterplan.md — distillation

> **Current sprint: S8 — Writeup** _(S0–S7 closed · Sprint D closed)_
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

- [x] `ollama pull hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M` (verify actual on-disk size against
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
- [x] Self-consistency probe: 100 headlines × 3 samples at temp 0 and temp 0.7 → report agreement
      → **temp 0: 100/100 unanimous · temp 0.7: 86/100 unanimous**
- [x] Pilot 100 labels; eyeball them; iterate the prompt; **freeze `prompt_version`**
      → **0% unparseable, all 8 classes present, prompt frozen at `v1` unchanged**
- [x] `record_decision`: final prompt version, quant, decoding params

**Acceptance:** ≥98% of pilot outputs parse to a valid class _(**100%**)_ · self-consistency
reported _(100% / 86%)_ · prompt frozen and versioned _(`v1`)_ · throughput measured so S4's
runtime is predictable, not a guess _(**1.24 labels/s**)_. — **PASSED**

**As-shipped delta:**
- **Prompt v1 needed no iteration.** 100/100 pilot labels parsed, all eight classes were used,
  and hand inspection found the labels sound. Frozen as `v1`.
- **Teacher determinism is perfect: 100/100 unanimous at temp 0.** The labelling run is
  exactly reproducible, which is what that probe existed to prove.
- **Teacher self-agreement at temp 0.7 is 86%, and the 14% is not noise — it is genuine
  multi-label ambiguity.** Every disagreement inspected was a headline that honestly belongs
  to two classes: *"Prabowo touts Indonesia's economic growth"* (finance/geopolitics),
  *"Micron: China probes US chip maker for cybersecurity risk"* (geopolitics/tech),
  *"Hundreds of millions at risk from Chinese shopping app malware"* (consumer/tech).
  **This is a soft ceiling on every arm, not a teacher weakness**, and it belongs in S8's
  limitations: the task forces one label onto headlines that carry two.
- **Teacher vs regex disagree on 60 of 100 pilot examples**, and inspection says the teacher
  is right in nearly all of them — `Arsenal express interest in signing Quansah` → sports,
  `I got an £89 refund - how to cancel unwanted subscriptions` → consumer,
  `Italian police recover stolen Renoir, Cézanne and Matisse paintings` → entertainment.
- **Distribution, the headline comparison:** the regex sends **74.2%** of the corpus to
  `general`; the teacher sends **28%** of the pilot there.
- **A sixth regex defect found via the pilot, and it is the most consequential one.**
  A teacher/regex disagreement on *"Russian drones kill a woman"* looked wrong until checked:
  every keyword is a bare noun and `\b` requires a non-word character after it, so
  **`Russian` does not match `russia`, `Chinese` does not match `china`, `Israeli` does not
  match `israel`, `Ukrainian` does not match `ukraine`, `Korean` does not match `korea`.**
  Headlines use adjectival forms constantly, and every one of them lands in `general`. This
  is a large part of the 74%. Verified across five pairs and pinned by a test.
- **A teacher error found by hand, recorded rather than hidden:** *"New Zealand breaks ranks
  and withdraws Infantino support"* → labelled `geopolitics`, but Infantino is the FIFA
  president and this is a sports-governance story. Exactly the kind of case the S4 audit
  exists to quantify.
- Throughput **1.24 labels/s** ⇒ S4 projects to ~43 min for the 3,206-example training pool
  plus ~7 min for the held-out 500. Cold start is ~19.6 s against ~800 ms warm.
- Disk after the pull: **12 GB free** (98% used). Enough — labels are kilobytes — but it is
  now the thing to watch until S4 deletes the teacher.

**Deferred:**
- `[⏭]` Prompt iteration — nothing to iterate. v1 passed on first contact, and changing a
  working prompt to look busy would only invalidate the pilot that validated it.

---

# S4 — Label, audit, measure, then reclaim the disk

**Goal:** ~5,000 training labels, a known noise ceiling, and the teacher's real latency —
captured before the weights are deleted.

- [x] Label `data/train_pool.jsonl` — unattended, resumable (checkpoint every 50,
      keyed by id, so a crash costs one batch not the run) → **3,206 labels, 0% unparseable**
- [x] Label the held-out 500 → `data/heldout_labels.jsonl` (this is the gold set for every arm)
      → **500 labels, 0% unparseable, all 8 classes, smallest class 34**
- [x] **Hand-audit 50 held-out labels.** I adjudicate; disagreements are itemised, not just counted.
      This number is the ceiling — the student cannot meaningfully exceed it.
      → **84% strict · 6% disagree · 10% ambiguous** → `results/audit_50.md`
- [x] **Teacher latency run:** held-out 500, sequential, one request at a time, no batching.
      Record p50 and p95. → **p50 782 ms · p95 868 ms** (min 562, max 1061)
- [x] `charts/label_distribution.png` — teacher labels vs regex labels, side by side. The
      divergence here is itself a finding.
- [x] Confusion matrix: regex vs teacher on the held-out 500 → the incumbent's error profile
      (right panel of the chart: where the regex's `general` pile actually belongs)
- [x] `ollama rm` the teacher; verify reclaimed space with `df` → **6.1 GB → 27 GB**
- [x] `record_verification`: counts, audit agreement, p50/p95, disk before/after
- [x] **Reproducibility verified three ways** (not planned; see delta)

**Acceptance:** ≥4,800 valid labels _(**3,706** — consistent with amendment A1, which lowered
the corpus target; every harvested example is labelled and none was dropped)_ · `UNPARSEABLE`
rate reported, not hidden _(**0.00%**)_ · 50-example audit agreement reported as an explicit
ceiling _(**84%**)_ · teacher p50/p95 recorded _(**782/868 ms**)_ · ≥18 GB reclaimed
_(**21 GB**)_. — **PASSED as amended**

**As-shipped delta:**
- **The result the project turns on:** of the 375 held-out headlines the regex calls
  `general`, the teacher reassigns **310 — 82.7%**. The incumbent's catch-all is wrong five
  times out of six. On the same 500, regex `general` = 75%, teacher `general` = 13.2%.
- **The teacher produces a genuinely balanced training set** where the regex produces rubble.
  On the identical 3,206-example pool: teacher `general` 426 (13.3%) vs regex `general`
  **2,374 (74%)**; teacher `consumer` 191 vs regex `consumer` **6**. Smallest teacher class is
  191, which is enough to learn from.
- **Reproducibility evidenced three ways rather than asserted** — none of this was planned,
  all of it was prompted by the mid-run config change:
  1. self-consistency probe, 100/100 unanimous at temp 0 (S3);
  2. **60/60 identical** across the `num_ctx` 32768→2048 change, so the config change
     provably altered no label;
  3. **500/500 identical** when the latency run independently re-predicted the entire
     held-out set and reproduced gold exactly.
- **A disk incident, diagnosed rather than survived.** Free space fell 12 GB → 4 GB mid-run.
  Cause: Ollama defaulted this model to a **32,768-token context** for ~250-token prompts,
  and that KV cache on top of 22 GB of resident weights drove the machine into swap (7.7 GB,
  290k pageouts) hard enough to consume the disk. Pinning `num_ctx: 2048` — still 8× headroom
  — stopped it immediately. The two obvious shortcuts were both declined: degrading the quant
  would degrade the ceiling every downstream number depends on, and the 9.6 GB of
  pre-existing Ollama models are Bruno's, not this project's to delete to make room for
  itself. A watchdog was armed to abort labelling below 2 GB; it never had to fire.
- **The teacher arm cannot be scored against its own labels.** Gold *is* the teacher, so a
  naive "teacher accuracy" would read 100% by construction and mean nothing. S7 reports the
  **hand-audit 84%** as the teacher's estimated true accuracy instead, and states plainly
  that student-vs-gold measures *agreement with the teacher*, not correctness.
- Labelling throughput held at ~1.22/s; the training pool took 29.7 min after the restart.
- The background harvester was stopped once labelling began: rows arriving after the split
  can never be labelled (the training pool is fixed), so it was consuming memory for nothing.
  The corpus file ends at 3,812 rows of which **3,706 are split and labelled**; the extra 106
  arrived late and are deliberately unused rather than quietly folded in.

**Deferred:**
- `[⏭]` Nothing deferred from this sprint.

---

# S5 — Base-model architecture probe (a real gate, not a formality)

**Goal:** find out whether `mlx-lm` can LoRA-tune `Qwen3.5-4B` *before* committing the
training sprint to it.

`Qwen3.5-4B` is `Qwen3_5ForConditionalGeneration` — multimodal, with hybrid
linear/full attention. `mlx-community` conversions exist, which is encouraging but not proof
that `mlx_lm.lora` handles the arch.

> **Pre-verified during S3's download wait (2026-08-14) — this risk is largely retired.**
> Inspected the installed `mlx-lm` 0.31.3 directly rather than waiting for S5:
> - `mlx_lm.models.qwen3_5` exists (118 architectures registered; the Qwen family includes
>   `qwen3_5`, `qwen3_5_moe`, `qwen3_next`, `qwen3_vl`).
> - It **explicitly handles the multimodal nesting**: `ModelArgs.from_dict` checks for
>   `text_config` and wraps a bare text config when absent, and `Model` builds its
>   `language_model` from `args.text_config`. That was the specific failure mode feared.
> - It implements `GatedDeltaNet`, i.e. the hybrid linear-attention layers are real, not
>   silently substituted with full attention.
>
> This cost nothing (no weights, no disk) and was done while the 22 GB teacher downloaded.
> The fallback ladder below stays in place — a registered architecture is not the same as a
> working LoRA run — but option 1 is now the expected outcome rather than a hope.

- [x] 20-example smoke fine-tune. Success = the run completes, loss decreases, the adapter
      loads, and 5 predictions parse to valid classes.
      → **loss 2.594 → 0.051 · adapter saved · 5/5 valid AND 5/5 correct**
- [x] Fallback ladder — take the first that passes, `record_decision` on the choice:
  1. **`Qwen/Qwen3.5-4B` — WINNER, no fallback needed** (via `mlx-community/Qwen3.5-4B-bf16`)
  2. `Qwen/Qwen3.5-2B` (unused)
  3. `Qwen/Qwen3-4B-Instruct-2507` (unused)
  4. `HuggingFaceTB/SmolLM3-3B` (unused)
- [x] Pin the exact revision SHA of whichever wins
      → `mlx-community/Qwen3.5-4B-bf16` @ `491fdc7c087ba7fb48adcb1253f8e76d011db783`
- [x] If the winner is not #1, note in the README why — n/a, #1 won
- [x] `src/prepare_training.py` — chat-format data with a leakage assertion
- [x] `configs/lora.yaml` — the S6 run, fully specified and committed

**Acceptance:** one base model chosen, revision pinned, smoke run reproducible from a
committed command · decision and rationale in `SYNC.md`. — **PASSED**

**As-shipped delta:**
- **The probe earned its place by catching a silent-failure bug that had nothing to do with
  the architecture risk it was designed for.** `Qwen3.5-4B` is a reasoning model, and its
  chat template opens a `<think>` block by default. The first adapter test returned
  `"Thinking Process:"` for all five cases — **0/5 valid classes** — which looked like a
  failed fine-tune. It was not:
  - mlx-lm renders *training* examples from the full conversation, which yields
    `…assistant\n<think>\n\n</think>\n\nfinance<|im_end|>` — a **closed, empty** think block.
  - Inference with a plain `add_generation_prompt=True` yields an **open** `<think>\n`,
    so the model does what any reasoning model does with an open think block.
  - `enable_thinking=False` at inference yields exactly `<think>\n\n</think>\n\n` — a
    byte-for-byte match with the training prefix. With that flag: **5/5 valid, 5/5 correct.**
  - **Consequence: `enable_thinking=False` is mandatory in the S7 eval harness.** Without it
    the student would have scored near zero and the obvious conclusion — "the fine-tune
    failed" — would have been completely wrong.
- **Architecture risk fully retired.** `mlx-community/Qwen3.5-4B-bf16` loads (4.21B params,
  multimodal wrapper and all), LoRA attaches, training converges. Trainable parameters:
  **0.096% (4.058M of 4,205.75M)**. Peak memory 18.6 GB — well inside 48 GB.
- **Five correct answers after twenty training examples** is a strong prior that the full run
  will work. It also means the eventual result will be about *how close* the student gets,
  which is the trade-off curve the brief actually wants — not whether it learns at all.
- The model load took 1,104 s on first fetch (8.5 GB download); subsequent loads are cached.
- Training data built: **3,046 train / 160 valid / 500 test**, balanced (smallest class
  `consumer` = 182), with a leakage assertion that the held-out 500 never reach the trainer.
- `--mask-prompt` adopted: without it the model spends capacity learning to regenerate a
  system prompt it is always given.

**Deferred:**
- `[⏭]` Nothing. The fallback ladder went unused and stays documented for reproducibility.

---

# S6 — Train

- [x] `src/train.py` / `configs/lora.yaml` — LoRA **r=16**, bf16, 3 epochs, lr + schedule logged
      → No `src/train.py` was written. Training runs off the `mlx-lm` CLI against the committed
      config, which is the same thing with less code to drift:
      `uv run python -m mlx_lm lora -c configs/lora.yaml > runs/current/train.log 2>&1`
      1,200 iters at batch 8 over 3,046 examples ≈ 3.2 epochs. lr 1e-5, constant (no schedule).
- [x] Chat-formatted examples using the frozen `prompt_version` from S3 — **the student must see
      the same prompt shape the teacher saw**, or the comparison is not clean
      → **Superseded by AMENDMENT A3.** The student gets the lean `Outlet:/Headline:` shape and
      no system block. Both arms still see identical *information* and the identical held-out
      500, so the quality comparison is clean; only the token count differs, and that is an S7
      result rather than a confound. The shape lives in `student_messages()`
      (`src/prepare_training.py`), which `src/evaluate.py` imports so the two cannot drift.
- [x] Train/valid split inside the training pool (held-out is never touched)
      → 3,046 train / 160 valid / 500 test, built in S5, leakage assertion on id passes.
- [x] Log every step's loss to `runs/<id>/loss.jsonl`
      → `steps_per_report` lowered 25 → 1 so the log is genuinely per-step. **1,213 records
      (1,200 train + 13 val)**, written by `src/record_run.py` — a producer that did not exist
      before this sprint. `nan` is preserved as an explicit `null` gap, never dropped.
- [x] `charts/training_curve.png` — committed. The brief calls a missing loss curve the first
      thing a reviewer notices.
      → 1,200 train points, 13 val points, 4 nan report windows (iters 85, 100, 423, 949)
      plotted as marked gaps and annotated.
- [x] `runs/<id>/hyperparams.json` — every hyperparameter, base-model revision, dataset hash,
      prompt version, mlx/mlx-lm versions
      → Also carries the git commit and a **dirty flag**, the sha256 of each dataset split, and
      the resolved run facts (peak memory, it/s, trainable parameters, completion status).
- [x] Merge adapter → `models/student-merged/`
      → 7.9 GB, gitignored. Fused with `mlx_lm fuse`, not a hand-rolled merge — a subtly wrong
      merge produces a model that loads, generates, and is quietly not the model trained.
      **Gotcha recorded:** `fuse` resolves models through
      `snapshot_download(local_files_only=True)` and aborted on a missing `.gitattributes`,
      a file carrying no weights. `src/merge_student.py` now resolves the local snapshot
      directory, which is named by the revision SHA — so the pin is kept, not weakened.
- [x] 20 sanity predictions parse to valid classes (Acceptance clause, listed here so it is tracked)
      → **20/20 valid, 17/20 agree with the teacher**, run against the MERGED weights rather
      than the adapter, because the merge is the step that could silently change behaviour.
      Raw outputs retained in `results/sanity_20.json` so any parse decision can be re-audited.
- [x] Runtime target ~15–60 min. If it heads past 2 h, stop and reduce — the brief caps this.
      → Observed 0.313 it/s sustained: **1,200 iters in ~64 minutes**. Inside the 60-minute
      target once val time is excluded, comfortably inside the 2 h cap.

**Finding — the last 200 iterations made the model measurably worse.** Validation loss:

```
iter    1  100  200  300  400  500  600  700  800  900  1000  1100  1200
val  5.604 .095 .080 .079 .093 .075 .077 .083 .075 .076  .276  .279  .280
```

Validation bottomed at **0.075** (iters 500 and 800) and blew out to **0.280** over the final
stretch. Train loss rose with it (0.127 → 0.219), so this is an optimisation excursion rather
than overfitting — but the effect on quality is real either way, and it is the reason
`src/select_checkpoint.py` exists:

- Selected **iter 800** (val 0.075) over the final iter 1200 (val 0.280).
- Worth **+8.0 macro-F1 points**: **0.8400** vs **0.7599**. Shipping mlx-lm's default final
  checkpoint would have discarded a tenth of the model's quality.
- **Selected on the 160-example validation split only.** The held-out 500 take no part —
  `select_checkpoint.py` never opens that file, and selection refuses any iteration with no
  checkpoint on disk (iter 500 also hit 0.075 but had none, so it was not selectable).
- Both evaluations are committed: `results/summary.json` (iter 800) and
  `results/summary_final_checkpoint.json` (iter 1200). The choice is recorded with its full
  ranking in `runs/current/best/selection.json`.
- `3.2 epochs was too many for this task` is a finding for METHODOLOGY, not a number to hide.

**Finding — `num_layers: 16` tunes FOUR layers, not sixteen.** Reconciles a discrepancy
between S5's recorded `0.096% (4.058M)` and this run's `0.022% (0.918M)`. Read directly off
the adapter's own tensor names (no model load required — the safetensors header is enough):

```
16 tensors · 917,504 params (0.918M) · F32
layers touched: [19, 23, 27, 31]          <- four, not sixteen
modules:        self_attn.q_proj x8, self_attn.v_proj x8   (A and B per module)
shapes:         (2560,16) x8 · (16,8192) x4 · (16,1024) x4
```

Qwen3.5-4B is a **hybrid** architecture: `full_attention_interval: 4`, so `layer_types` is
`[linear_attention, linear_attention, linear_attention, full_attention, ...]` — only 8 of its
32 layers are full attention, and the other 24 are `GatedDeltaNet`, which has no
`self_attn.q_proj`/`v_proj` to attach to. `num_layers: 16` selects the last 16 layers, of which
exactly four (19, 23, 27, 31) carry the targeted modules. The config reads as though sixteen
layers are being tuned; four are.

This is not a bug and the run is not invalidated — but it is the kind of thing that belongs in
METHODOLOGY rather than being quietly correct. **The student learns the task with 0.022% of
its parameters trainable, across 4 of 32 layers**, which strengthens rather than weakens the
distillation story. The authoritative figure for S6 is the run log's `0.022% (0.918M of
4,205.75M)`; S5's `4.058M` came from the probe under a different key set and is left in place
as the probe's record.

**Run history (expanded in place — the first two runs are part of the record):**
1. Pre-A3 run, killed at ~iter 300. 299 tokens/example projected ~10 h. Triggered A3.
2. Post-A3 run, 2026-08-15 03:53–05:02. Died at **~iter 1170 of 1200** — not a crash in the
   training code but a **macOS GPU-driver kernel panic** (`IOGPUGroupMemory.cpp:323`, panicked
   task `python3.12` at 25 GB resident). The reboot cleared `/tmp`, and the run had been
   logging to `/tmp/train.log`, so **the loss history for iters 1–1000 is unrecoverable**.
   Adapters through iter 1000 preserved at `runs/interrupted-panic-20260815/`, unused.
   Discarded rather than resumed: `mlx-lm` restarts the iteration counter on resume and does
   not checkpoint optimiser state, so a resumed run yields neither an uninterrupted model nor
   an honestly plottable curve. Reconstructing a curve from a lost log would break the
   honest-claims rule outright.
3. Re-run, 2026-08-15 19:46 →. Identical seed/data/hyperparameters except `steps_per_report`.
   **Logs to `runs/current/train.log`, inside the repo, where a reboot cannot take it.**

**Acceptance:** loss decreases and the curve is committed · adapter loads standalone ·
20 sanity predictions parse to valid classes · hyperparams + dataset hash recorded.
— **PASSED**
- Loss decreases: train 5.334 → 0.196, val 5.604 → 0.075 at the selected checkpoint — PASS
- Curve committed: `charts/training_curve.png`, 1,200 train + 13 val points — PASS
- Adapter loads standalone: 500 held-out predictions, **0 unparseable** — PASS
- 20 sanity predictions parse: **20/20 valid** against the merged weights — PASS
- Hyperparams + dataset hash: `runs/current/hyperparams.json`, sha256 per split — PASS

**As-shipped delta:**
- **The run this sprint had to survive was its third.** Run 1 died at ~iter 300 (pre-A3, 299
  tokens/example, ~10 h projected). Run 2 reached ~iter 1170 of 1200 and was killed by a macOS
  **GPU-driver kernel panic** (`IOGPUGroupMemory.cpp:323`), which rebooted the machine and
  cleared `/tmp` — where it had been logging. That cost the entire loss history and forced a
  full retrain rather than a resume: `mlx-lm` restarts the iteration counter on resume and does
  not checkpoint optimiser state, so a resumed run yields neither an uninterrupted model nor an
  honestly plottable curve. Run 3 logged to `runs/current/train.log`, inside the repo.
- **Peak memory 43.911 GB on a 48 GB machine.** That is 91% of unified memory, and it is why
  every other model load was held for the duration rather than run concurrently — the panic had
  already demonstrated what that headroom is worth. Documented so the next run budgets for it.
- **`num_layers: 16` trains four layers, not sixteen** (full finding above). 0.022% of
  parameters trainable — 917,504 of 4,205,750,000 — across layers 19, 23, 27 and 31.
- **The best checkpoint was not the final one**, worth +8.0 macro-F1 (full finding above).
- Two producers that the plan assumed existed and did not: `src/record_run.py` (loss.jsonl +
  hyperparams.json) and `src/select_checkpoint.py`. `mlx-lm` writes neither.
- No `src/train.py` was written. Training runs off the `mlx-lm` CLI against the committed
  config — the same thing with less code to drift out of sync with what actually ran.

**Deferred:**
- `[⏭]` Nothing deferred. Every S6 task closed.

---

# S7 — Evaluate (this is what separates a training script from an evaluation)

**Goal:** all three metrics, all three arms, one harness, every number regenerable.

- [x] `src/evaluate.py` — one harness, three arms, the same 500 held-out examples,
      the same machine, gold = teacher labels (with the audit-derived ceiling stated alongside)
      → Teacher quality is refused, not computed: gold IS its output, so any figure is 100% by
      construction. The harness prints `n/a` and carries the 84% hand audit instead.
- [x] **Quality** — accuracy, **macro-F1**, per-class P/R/F1, confusion matrix per arm
      → **student macro-F1 0.8400 · accuracy 0.8540 · 0 unparseable of 500**
        **regex   macro-F1 0.3372 · accuracy 0.3420**
- [x] **Latency** — p50 **and** p95, measured by this harness, sequential, single request.
      Student measured here; teacher's numbers come from the S4 run on the identical set.
      → **student p50 327.1 ms · p95 402.4 ms** (3 warm-up calls discarded, `perf_counter`
        around a single sequential `generate`). Teacher p50 781.8 · p95 867.7 from S4.
        The student is **2.4x faster** than the teacher it was distilled from.
- [x] **Cost** — per 1,000 requests, arithmetic shown line by line, **explicitly labelled
      list-price** (all local runs cost $0). Show the token counts the arithmetic uses.
      → teacher **$0.1547**/1k · student **$0.0037**/1k · regex $0. Student is **2.42% of
        teacher cost, 41.3x cheaper** = 5.0x price tier x 8.26x fewer tokens.
      → **The token counts were wrong and are now measured.** `cost.py` hardcoded four
        constants under a docstring claiming they were measured; two were wrong in the
        flattering direction (student input 32 vs a real 35.98 — that 32 was A3's figure for a
        whole training *example*; teacher output 10 vs a real 6.51). `src/measure_tokens.py`
        now derives all four from the real tokeniser over all 500 held-out rows into
        `results/token_counts.json`, and `cost.py` raises rather than falling back if it is
        absent. The corrected headline is **41.3x, not the 45.4x previously committed.**
- [x] **Error analysis, the part most people skip:**
  - [x] Confusion matrix → the top 5 confused pairs
        → student: `general`→`science` 7 · `consumer`→`tech` 7 · `general`→`geopolitics` 7 ·
          `general`→`entertainment` 5 · `consumer`→`general` 4
  - [x] Error taxonomy by cause, not just by class
        → regex buckets are mechanical and checkable against its own source (catch-all
          fall-through, the `china`-before-everything rule, first-match-wins). Student buckets
          are deliberately coarser — inventing fine-grained causes for a neural model's errors
          would be storytelling.
  - [x] Prose: *where and why* the student loses. "It confuses `tech` and `science` on
        space-launch headlines" beats any aggregate number.
        → `results/error_analysis.md`. The real weakness is **`consumer` recall 52.9%**
          (F1 0.679, its weakest class), most often called `tech` — a milder inheritance of
          the very `Amazon Prime Day → tech` bug this project opens with.
  - [x] The inverse: cases where the **student beats the regex badly** — that is the product argument
        → **student right where the regex is wrong: 285. Regex right where the student is
          wrong: 29.** Verbatim examples for both in `error_analysis.md`.
  - [x] Headline-length and outlet-tier breakdowns of student error
        → Length bands shipped. **Outlet TIER could not be shipped honestly: no tier taxonomy
          exists in this repo.** `Feed` is `(outlet, url, section)` and `heldout.jsonl` has no
          `tier` field, so a tier column would have read `unknown` for all 500 rows while
          looking like a result. Invented an editorial ranking? No — reported per-outlet
          (real) plus a **volume band** cut on held-out counts, labelled in the artifact as a
          stated proxy for prominence rather than an editorial judgement.
- [x] `results/summary.json` — every number the README will cite
      → Now also carries a `provenance` block: evaluated_at, base model + **pinned revision**,
        adapter path, **adapter sha256**, held-out file hashes, git commit and dirty flag. The
        harness previously recorded none of this and did not pass the revision to `load()`,
        so it resolved whatever snapshot the cache held — a direct CLAUDE.md violation.
- [x] One command regenerates all of it
      → `uv run python -m src.reproduce` (`--skip-student` for the GPU-free path, `--dry-run`
        to print the pipeline). Deliberately does **not** train.

**Acceptance:** three arms × three metrics, all present · confusion matrices committed ·
error taxonomy written in prose · every README number traceable to `results/summary.json`.
— **PASSED**
- Three arms x three metrics: quality + latency + cost for regex and student; latency + cost
  for the teacher, with quality refused on principle and the 84% audit reported instead — PASS
- Confusion matrices committed: `charts/confusion_regex.png`, `charts/confusion_student.png` — PASS
- Error taxonomy in prose: `results/error_analysis.md` — PASS
- Every number traceable: `results/summary.json` + `token_counts.json` + `error_analysis.json`
  + `sanity_20.json` + `hyperparams.json`, all committed — PASS

**As-shipped delta:**
- **The student loses to the regex on exactly one class, and it leads rather than hides.**
  `general` recall: student 68.2% vs regex 98.5%, a 30-point loss. The mechanism matters and is
  reported *after* the loss, never instead of it: the regex reaches 98.5% recall at **17.3%
  precision** by answering `general` for 375 of 500 headlines. On F1 the ordering reverses —
  student 0.698 vs regex 0.295 — and on F1 the student loses no class at all. `per_class_gap`
  therefore reports `student_loses` (recall) and `student_loses_on_f1` as separate flags, so
  neither framing can quietly swallow the other.
- **The regex never predicts `consumer`. Not once in 500.** Precision, recall and F1 are all
  0.000 for that class. The student reaches 0.679 F1 on it.
- Evaluated **two** checkpoints, not one, and committed both — the headline (iter 800) and the
  default final weights (iter 1200) that a less careful run would have shipped.
- `summarise()` now states in the artifact that quality is scored over parseable predictions
  only, with unparseable counted and reported separately. It is 0 here, so the distinction is
  currently moot — it is written down precisely so a future non-zero cannot be misread.

**Deferred:**
- `[⏭]` Outlet-**tier** breakdown — the data does not exist in this repo (see above). Shipped
  per-outlet and a labelled volume-band proxy instead. Adding a real tier taxonomy would mean
  authoring editorial judgements about 54 outlets, which is a new source of unbacked claims,
  not a breakdown.

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

# Sprint D — Documentation

**Goal:** the repo reads well to a stranger on GitHub — a picture and a number in the first
screen, the architecture from one diagram, and a findable receipt for every claim — plus a
machine-readable `PROJECT.json` the portfolio consumes. Driven by `DOCS-ENGINEERPROMPT.md`.

**Run out of sequence, deliberately.** The docs prompt says to run this after the engineering
is done. It is not: S6 was mid-flight and S7 had never run. Bruno's call was to document now
with the student's results marked pending rather than block the write-up on the training run.
That constraint is what the sprint is shaped around — see the As-shipped delta.

- [x] Read `CLAUDE.md`, all of `masterplan.md`, `SYNC.md`, the current `README.md`, and enough
      of `src/` to draw the architecture honestly
- [x] `uv run pytest` — **138 passed**, captured rather than quoted (93 at the start of the
      sprint; the parallel S6/S7 session added the chart-guard and provenance suites while it ran)
- [x] `AskUserQuestion` on the four things the repo could not decide: how to handle the
      unfinished S6/S7, which S9 gates are done (**none**), whether to soften any number
      (**publish everything**), and the hero visual (`charts/label_distribution.png`)
- [x] `src/stats.py` → `results/corpus_stats.json` — **not in the docs prompt, added because
      the honesty rule demanded it.** `data/` is gitignored, so every corpus and teacher figure
      in the write-up was backed only by prose in this file and `SYNC.md`. Now recomputed from
      the JSONL into a committed artifact.
- [x] Run the eval harness in its `--skip-student` mode to score the incumbent arm end to end —
      no model load, so it was safe to run alongside the live training job
- [x] Wire `cost.breakdown()` into `results/summary.json` so quality, latency and cost cite one
      artifact and the list-price disclaimer cannot be separated from the number
- [x] `README.md` rewritten to the docs prompt's structure: hook · hero chart · run command ·
      results table · badges · what it does · Mermaid architecture · how it was built ·
      evidence table · usage · limitations · status · licence
- [x] `PROJECT.json` — every `metrics[].source` and `headline.source` verified to exist
- [x] `LICENSE` (MIT, matching `ctxbench` and `mcpaudit`) with the vendored-Geist and
      model-licence notes
- [x] `.github/workflows/ci.yml` — macOS runner, because `mlx` has no Linux wheel and a ubuntu
      job could not even resolve the dependency set. Includes a grep gate asserting the
      reserved amber `#FF9500` never reaches a chart.
- [x] Verification pass: every local link and image resolves, every anchor exists, and every
      number in the README checked against its artifact programmatically
- [⏭] `METHODOLOGY.md` — it is an **S8 deliverable** and S8 has not run. Writing it now would
      mean writing the corpus/split/prompt protocol twice, since it has to be revised the
      moment the student's numbers land. The README links `masterplan.md` and `SYNC.md` for
      the protocol in the meantime.
- [⏭] CI badge in the README — the workflow is committed, but there is no GitHub remote, so
      the badge would 404. It goes in when the repo is published at S9.
- [⏭] `docs/media/` recorded terminal demo — the demo worth recording is the three-arm eval,
      which cannot run until S7.

**Acceptance:** every number in the README traceable to a committed artifact · `PROJECT.json`
validates and every source path exists · no badge that 404s · limitations prominent · no
student number published while the student is unevaluated. — **PASSED**

**As-shipped delta:**
- **The docs pass caught a live defect in the cost model, which is the sprint's most valuable
  finding.** Writing the cost section required checking `src/cost.py`'s token constants, and a
  parallel session re-tokenised all 500 held-out prompts through each arm's real prompt
  builder. **All four constants were wrong, in both directions:** student input understated at
  32 against a measured 35.98, teacher output overstated at 10 against 6.51. The 32 came from
  A3's *training-example* figure, which is a different quantity from an inference-time input.
  The published headline moves **45.4× → 41.3×**. `cost.py` now reads
  `results/token_counts.json` and raises if it is absent, so it cannot fall back to a constant.
  Both sessions measured the student's output token count independently and agreed at 1.51.
- **A3's `9.3×` is superseded.** The measured input ratio is 302.98 / 35.98 = **8.42×**, and
  the whole-request token ratio is **8.26×**. A3's 9.3× was computed from the training-example
  tokenisation and remains correct for what it describes; it is not the per-request figure the
  cost table needs. Recorded here rather than edited in place.
- **The incumbent arm is now scored end to end, which the plan had left to S7.** `--skip-student`
  needs no model, so it ran safely during training: **macro-F1 0.3372, accuracy 0.3420**, with
  `consumer` at **0.000 F1 on 34 held-out examples** — the rule never fires once, because
  `amazon` is matched by the tech branch above it. Precision is high where it fires
  (entertainment 1.000) and recall is not (0.129); `general` inverts it at precision 0.173,
  recall 0.985. All five top confusions are the same confusion, `X → general`.
- **A stale count corrected: the catalog is 63 production feeds, not 61.** `CLAUDE.md` and the
  old `README.md` both said 61; `src/feeds.py` and this file say 63, and `len(FEEDS)` is 63.
  The README now says 63. Likewise the committed `EXPANSION_FEEDS` is **83**, not the 84 this
  file records — 86 were probed and 84 returned items, but `skysports.com` was then dropped for
  introducing an outlet outside the production catalog, so 83 is what ships.
- **Two coordinating sessions, one repo.** A parallel session owned S6/S7 while this one owned
  documentation. It flagged an active training run peaking at 31.8 GB and asked for no model
  loads; every command run here was regex- or tokeniser-only. Shared-file writes to this file
  and `SYNC.md` were sequenced by explicit hand-off rather than by hoping.
- Also learned from that session: the **first full training run died at ~iter 1,170/1,200 in a
  macOS GPU-driver kernel panic** (`IOGPUGroupMemory.cpp:323`), taking its stdout log with it.
  That is why the last checkpoint on disk is iteration 1,000 and why there is no loss curve to
  commit yet. The README's Status section says so plainly rather than implying a clean run.
- Teacher token counts are measured with the **student's** tokeniser, because the teacher's
  22 GB were deleted in S4. Same Qwen family, not the same file. The caveat is written into
  `results/token_counts.json` so it travels with the number.
- **The tests badge carries no count, deliberately.** It went 93 → 132 → 133 → 138 inside this
  sprint as the parallel session added the chart-guard and provenance suites. A hand-maintained
  count in a README is stale the moment anyone writes a test, and a stale number in the one
  document that promises every number is backed is worse than no number. The badge reads
  `tests · pytest` and links the suite; the exact figure lives in `SYNC.md`'s Sprint D
  verification, where a point-in-time snapshot is the correct form. **When the repo goes public
  at S9 the badge should be swapped for the live CI status badge**, which is the only version
  that cannot drift.
- The README's run command is `uv run python -m src.reproduce --skip-student`, the pipeline the
  parallel session built during this sprint — one command that regenerates every result and
  chart in dependency order, and deliberately does not train.

- **Sprint D was reopened after S6/S7 landed, and the README was completed rather than left
  pending.** The four `pending` cells are filled: student **macro-F1 0.8400 · accuracy 0.8540 ·
  p50 327 ms · p95 402 ms · 0 invalid**. Three findings were added that did not exist when this
  sprint first closed:
  1. **The student loses exactly one class to the incumbent** — `general` recall 0.682 vs 0.985 —
     and per CLAUDE.md's rule it leads rather than being buried. It sits directly under the results
     table with the mechanism attached: the regex earns 0.985 by answering `general` for 75% of
     everything, at 0.173 precision, and loses the same class on F1 0.295 to 0.698. The rule was
     honoured without letting the mechanism delete the loss or the loss overstate itself.
  2. **Checkpoint selection is worth +8.0 macro-F1 points** (0.8400 at iter 800 vs 0.7599 at the
     final iter 1200), chosen on the 160-example validation split alone. Both evaluations are
     linked from the README, not just the flattering one.
  3. **A correction to this pass's own prose:** the end-of-run loss rise was first written up as
     "mild overfitting". Checking `runs/current/loss.jsonl` showed mean *training* loss rising too
     (0.072 → 0.26) alongside validation (0.075 → 0.280), which makes it an **optimisation
     excursion**, not overfitting. Corrected before publication.
- The README's hero stays `charts/label_distribution.png` per Bruno's choice;
  `confusion_regex.png`, `confusion_student.png` and `training_curve.png` are placed in the
  sections whose argument they carry.
- One process note worth keeping: a terminal transcript was drafted for the Usage section with
  plausible `[eval] student 100/500` progress lines that **had not actually been captured** — this
  session never ran the student eval. It was caught before publication and replaced with the arm
  table reproduced from `results/summary.json`. Inventing realistic-looking captured output is a
  failure mode the honest-claims rule does not explicitly name, and it should.

**Deferred:** the three `[⏭]` items above, all blocked on S7 or on the S9 publish gate.
`METHODOLOGY.md` remains S8's. The tests badge stays countless until CI can generate it.

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

**A3 · 2026-08-15 · The student gets a lean prompt. This reverses the S5 decision.**

S5 recorded that the student would keep the teacher's full system prompt, reasoning that
holding the prompt constant kept the quality comparison clean. **Measurement showed that was
wrong on two counts.**

*Runtime.* The first training run managed fewer than 25 iterations in 13 minutes, projecting
to roughly **ten hours** against the brief's one-hour cap. Tokenising the two shapes explains
it exactly:

| | tokens per example |
|---|---|
| full prompt (system + user + answer) | **299** |
| lean prompt (user + answer) | **32** |
| the system block alone | 262 |

**88% of every training example was the same instruction block, repeated 3,046 times.** With
lean prompts the same run does 0.30 it/s — about **70 minutes**, inside budget.

*Design.* The stronger objection is that the original reasoning was simply backwards. A
distilled student is supposed to stop needing the instructions — that is what "the task is in
the weights" means. Making it re-read 262 tokens of class definitions on every call would
have **understated the distillation win** in the one place the project is trying to measure
it: input tokens per request, which drive both cost and prefill latency.

*What this does and does not change.* Both arms still see exactly the same **information**
(outlet + headline) and exactly the same held-out 500. Nothing about the quality comparison
moves. What moves is that the student's per-call input drops 9.3×, and that belongs in the
S7 cost table as a result rather than being suppressed as a confound.

The shape lives in one function — `student_messages()` in `src/prepare_training.py` — which
`src/evaluate.py` imports, so training and evaluation cannot drift apart.

**A4 · 2026-08-15 · Three feed counts in this file and in `CLAUDE.md` were wrong. No measured
result moves.**

Found during the Sprint D documentation pass, while checking every number the README was about
to cite against the code that produces it. Recorded here rather than edited in place, per this
file's append-only rule.

| claim | where it appeared | ground truth (`src/feeds.py`) |
|---|---|---|
| "61 public RSS feeds" | this file ×2 (¶1 and D3), `CLAUDE.md` ×2, old `README.md` | **`len(FEEDS)` = 63** |
| "86 candidates probed, 84 live" → read as 84 shipped | S2 As-shipped delta | **`len(EXPANSION_FEEDS)` = 83** |
| "the expansion adds 11 sports and 17 science" | S2 As-shipped delta | 11 sports, **15 science** |

The 63 is a transcription slip that propagated. `src/feeds.py`'s own docstring says "63 feeds
across 9 editorial sections" and its S2 task line here says 63, but **the one-paragraph version
at the top of this file and D3 in the locked-decisions table both still say 61**, as did
`CLAUDE.md` and the old README. `CLAUDE.md` and the README have been corrected to 63; the two
occurrences in this file are left standing because this file is append-only, and this amendment
is the correction of record for them. A reader who hits the 61 in ¶1 or D3 should read it as 63.
Nothing about D3's actual decision — rebuild from the production catalog, zero credentials —
depends on the count.

The 84 is not a slip, it is two different quantities collapsed into one. 86 section-feed
candidates were probed and **84 returned items** — that is the number the S2 delta records, and
it is correct. But `skysports.com` was then dropped for introducing an outlet outside the
production catalog, so **83** is what ships. `63 + 83 = 146`, which is exactly the "146 feeds
attempted" already recorded in S2's `record_verification`, so the ledger was internally
consistent all along and only the prose was ambiguous.

**Why this changes nothing measured, stated so nobody has to take it on faith.** Every number
downstream is computed from the harvested corpus or from `ALL_FEEDS` at runtime — never from
these prose counts. `src/harvest.py` iterates `feeds.ALL_FEEDS`; `src/stats.py` recomputes the
distribution figures from `data/*.jsonl`; the `assert` in `src/feeds.py` and the test in
`tests/test_corpus.py` enforce the no-new-outlet rule against the tuple itself. The corpus is
still 3,706 headlines from 54 live outlets, the held-out 500 is unchanged, and no label,
score, latency or cost figure is touched. This is a documentation defect, not a data one.

**The rule it suggests, for the remaining sprints:** a count that appears in prose and also
exists in code should be cited from the code. That is the reasoning behind `src/stats.py` and
`results/corpus_stats.json`, added in the same pass — the figures that back the write-up are now
recomputed into a committed artifact rather than transcribed by hand into three files that can
each drift separately.
