# CLAUDE.md — distillation
# LoRA-distilling a live production news classifier from a large open teacher into a ~4B model

Read this file at the start of every session. It is the constitution for this repo.
`masterplan.md` is the execution plan and the single source of truth for sequencing.

---

## What this is

Sentinel — Bruno's live iOS news-intelligence product — classifies every ingested headline
into one of eight topic classes. In production that classifier is a **keyword regex**
(`classifyWireItem()`, `~/Desktop/AI REPORTING APP MVP/supabase/functions/_shared/wire.ts:353`)
and it is structurally broken in ways visible in its own source: the `if` chain returns on
first match, so `"Amazon Prime Day"` is `tech` rather than `consumer`, `"SpaceX launch"` is
`tech` rather than `science`, and any headline containing `china` is `geopolitics` forever.

This repo rebuilds that corpus from the same 61 public RSS feeds the product reads, labels
~5,000 headlines with a large open-weight teacher running locally, LoRA fine-tunes a ~4B
open model on those labels, and reports quality, cost and latency for **three** arms —
regex, teacher, student — on 500 headlines held out before a single label was generated.

**This is the project that demonstrates actual ML: training, not inference.**

The editorial rule, inherited from the brief: **the deliverable is the trade-off curve, not
parity.** 94% of teacher quality at 3% of the cost is a better and more believable story
than a tie. If you catch yourself tuning to close the last four points, stop and write up
the curve instead. And if the student loses to the regex anywhere, that leads the README.

---

## Owner

| | |
|---|---|
| Name | Bruno Jaamaa · jaamaabruno@gmail.com · GitHub `br9704` |
| Source product | Sentinel Intelligence (iOS + web). Repos: `~/Desktop/AI REPORTING APP MVP` (iOS + backend), `~/Desktop/sentinel-web`, `~/Desktop/sentinel-dashboard` — **all read-only reference. Never modify them from here.** |
| This repo | Separate. Never a subfolder of a product repo. |
| Sibling sprint projects | `~/Desktop/ctxbench`, `~/Desktop/mcpaudit` — same workflow discipline, same README rules |

---

## Source of truth — read this first

1. **`masterplan.md`** — sequencing, sprints, acceptance criteria. Work only the active sprint.
2. **`ENGINEERPROMPT.md`** — the original brief. Authored, not to be rewritten.
3. This file — rules and architecture index.

Precedence when they disagree: **masterplan (sequencing) > this file (rules) > engineerprompt (brief)**.

### Masterplan discipline (the contract)

- At session start: open `masterplan.md`, find the **Current sprint** pointer at the top,
  work only that sprint.
- Mark every task as you go: `[ ]` not started · `[~]` in progress · `[x]` complete ·
  `[⏭]` deferred (with a one-line reason).
- **Never delete or rewrite masterplan content.** Expand in place: add sub-tasks, file paths,
  edge cases, findings. Deepen, don't replace. Material changes to locked decisions go in
  the append-only **AMENDMENTS** block.
- At sprint end: fill that sprint's **As-shipped delta** and **Deferred** blocks, move the
  Current-sprint pointer, update the Current-state line at the bottom of this file.
- A sprint is not done until its **Acceptance** block passes. Never skip. Never partially
  complete and move on.
- **Stop and report to Bruno at every sprint close** before starting the next.

---

## Aethereum sync — required workflow

- `share_intent` **before starting any sprint** — one line, what you're about to do.
- `declare_contract` for every schema other code consumes: `Example`, `Label`, `Prediction`,
  the results JSONL shape. Bump on change.
- `record_decision` at every fork — task lock, teacher choice, base model, quant, prompt
  version, publish-or-gate — with a `why`.
- `ask_human` for anything that is Bruno's call: spending money, publishing weights, making
  the repo public. **Per Bruno's instruction, all of these are deferred to S9** — do not
  scatter gates through the plan.
- `record_verification` at each sprint gate with pass/fail + evidence.
- Marking a masterplan task `[x]` without having shared intent for that sprint is a
  workflow violation.

**How the verbs actually reach the server here.** They are MCP tools and the aethereum MCP
server is **not connected in this session** (it cannot be hot-added mid-session). So every
sync event is written to `SYNC.md` as a timestamped ledger entry in canonical verb form,
and replayed through the real tools once the server is live. This mirrors aethereum's own
design — all its handlers fail soft with an `OFFLINE` sentinel and never throw. A local
ledger is the same contract. Blocking the project on an MCP reconnection would be wrong.

---

## Locked decisions (do not relitigate — full table in `masterplan.md`)

- **Open-weight teacher only.** `Qwen/Qwen3.5-35B-A3B` Q4_K_M, Apache-2.0, run locally.
  The ENGINEERPROMPT's entire "legal trap" section is resolved by this and **closed
  teachers are not revisited.** Publishing weights trained on Anthropic/OpenAI/Gemini
  output would breach their terms; an open teacher makes the headline deliverable clean.
- **One narrow task**: 8-class wire topic classification. The class strings are copied
  verbatim from `wire.ts` and are not to be "improved".
- **Three arms, not two**: regex · teacher · student. Benchmarking only against the teacher
  would be choosing the flattering baseline — the exact credibility failure the brief warns
  about.
- **Corpus rebuilt from public RSS + GDELT. Zero credentials, zero user data.** Do not
  reach for the production Supabase key; D3 in the masterplan exists precisely to avoid it.
- **Cost figures are list-price arithmetic, labelled as such.** Everything runs locally at
  $0. Latency is genuinely measured; cost is genuinely arithmetic. Never blur the two.
- **Macro-F1 is the headline metric**, not accuracy — `general` is a catch-all that would
  flatter every arm.
- **MLX for training.** Unsloth and bitsandbytes are CUDA-only; this is an M4 Pro.
- **LoRA r=16, bf16, no QLoRA.** At 4B the memory is there, and Unsloth advises against
  QLoRA for Qwen3.5 (quantization artifacts).
- **All owner gates live in S9.** S0–S8 run free and unattended.

## Non-goals (hard boundaries)

No full fine-tune (LoRA only) · no multi-task model · no serving infrastructure or
deployment · no RLHF/DPO/preference alignment · **do not try to beat the teacher** ·
do not chase parity.

---

## The constraint that shapes everything: 34 GB free disk

Not RAM — 48 GB unified is ample. Disk is what binds, and the naïve ordering overflows it
(19 GB teacher + 8 GB base + 8 GB merged + 2 GB env = 37 GB). The fix is sequencing, and it
is why S4 ends by deleting the teacher:

```
harvest corpus         ~0.1 GB
pull teacher Q4_K_M   +19 GB   peak ≈ 21 GB
label + measure teacher latency on the held-out 500
DELETE teacher        −19 GB   labels are on disk; the teacher is re-pullable from HF
pull student base      +8 GB
train + merge          +8 GB   peak ≈ 18 GB
```

**Measure teacher latency before deleting it.** Sequential, one request at a time, on the
held-out 500. Batched labelling throughput is not latency and must never be reported as it.

---

## Architecture index

```
distillation/
├── masterplan.md · CLAUDE.md · ENGINEERPROMPT.md · SYNC.md
├── README.md                  # results table above the fold; limitations prominent
├── METHODOLOGY.md             # corpus, split protocol, prompt, teacher-noise audit
├── pyproject.toml             # uv-managed, Python 3.12 (system 3.14 is too new)
├── src/
│   ├── schema.py              # TOPIC_CLASSES, Example, Label, Prediction  (CONTRACTS)
│   ├── regex_baseline.py      # faithful port of classifyWireItem, bugs included
│   ├── feeds.py               # the 61 production feed URLs + outlet + tier
│   ├── harvest.py             # async RSS fetch, dedup
│   ├── gdelt.py               # historical backfill, 1 req/5s enforced
│   ├── split.py               # held-out 500, stratified, disjointness asserted
│   ├── teacher.py             # local Qwen3.5-35B-A3B labelling, strict parse, resumable
│   ├── train.py               # mlx-lm LoRA r=16 bf16
│   ├── evaluate.py            # ONE harness, three arms, quality + latency + cost
│   ├── scoring.py             # accuracy, macro-F1, per-class P/R/F1, confusion matrix
│   └── charts.py              # Aethereum design tokens applied to matplotlib
├── data/        # corpus.jsonl · heldout.jsonl · train_pool.jsonl · *_labels.jsonl (gitignored)
├── runs/        # <run-id>/loss.jsonl · hyperparams.json
├── results/     # summary.json — every number the README cites
├── charts/      # class_distribution · label_distribution · training_curve · confusion (committed)
└── tests/       # pytest
```

## Build conventions and guardrails

- Python 3.12 via `uv`. **Not** system 3.14 — the ML wheels do not exist for it yet.
- Every model reference is **pinned by revision SHA** and recorded in every artifact.
  A result produced from an unpinned model is not reproducible and does not count.
- The teacher's unparseable outputs are marked `UNPARSEABLE` and reported. **Never silently
  coerce to `general`** — that biases the teacher toward the majority class and corrupts the
  very ceiling the whole project is measured against.
- Labelling is checkpointed every 100 examples, keyed by id, so a crash costs one batch.
- The held-out 500 is split **before** any labelling and never enters training. Disjointness
  is asserted in code on URL hash, not assumed.
- The student sees the **same prompt shape** the teacher saw, or the comparison is not clean.
- Latency comes from this repo's own monotonic timer around a single sequential request.
- **Honest-claims rule** (inherited from the Aethereum repo): never state a number in the
  README or METHODOLOGY that a committed artifact cannot back. Verified counts only.
- Respect rate limits with sleeps, not retry-on-429. GDELT asks for 1 req/5 s and says so.
- Read-only toward every product repo. If something seems to need a backend change, it
  doesn't — this project is deliberately decoupled from the product.

## Design system — inherited, not invented

Charts and README follow the Aethereum tokens at
`~/Desktop/hive/apps/web/styles/tokens.css`. **Bruno designs nothing for this project.**

- Type: **Geist** (body) / **Geist Mono** (code, terminal output, numerals in tables only)
- Field: near-black. Not flat grey, not a light theme.
- Accent: green `#34C759`
- **Amber `#FF9500` is RESERVED for collision alerts and must not appear in any chart.**
  For warnings use `--accent-yellow #FFD60A`; for errors `--accent-red #FF3B30`.
- Hairline `0.5px` · radius ladder 8 / 12 / 16 · 4px spacing rhythm
- Restrained, data-dense, deliberate. The design background is an edge most AI engineers
  don't have; don't waste it — and don't decorate.

## README rules (apply to all three sprint projects)

1. One sentence: what this does and why it exists
2. Results table or chart **above the fold**
3. A live link or one-line run command
4. Architecture description
5. **Honest limitations section** — prominent, not buried

---

## Money and external actions (owner-gated — all deferred to S9)

Per Bruno's instruction, no gate interrupts S0–S8. Everything below waits for S9:

- Pushing weights or the dataset to Hugging Face
- Making the GitHub repo public
- Any paid compute or API spend (including the optional hosted-teacher ablation)

---

## Current state

> Update this line at the end of every sprint.

**Current state:** **S0 closed.** Constitution and masterplan authored (S0–S9 + backlog).
Toolchain live: `uv` 0.12.4, Python 3.12.13, `mlx-lm` 0.31.3 verified executing on Metal
(`Device(gpu, 0)`). ccline statusline installed; aethereum room `distillation` created and
wired (MCP callable next session — `SYNC.md` is the ledger until then). Research verified:
task locked to 8-class wire topic classification, corpus is public RSS + GDELT with zero
credentials, teacher is local `Qwen3.5-35B-A3B` Q4_K_M, training path is MLX. Binding
constraint is 34 GB free disk, resolved by sequencing. **S1 closed:** contracts (`Example`, `Label`, `Prediction`) and
the scorer are frozen, the incumbent regex is ported with its five defects pinned by tests
(38 passing). **Next: S2 — corpus.**
