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

_(entries appended at sprint start)_
