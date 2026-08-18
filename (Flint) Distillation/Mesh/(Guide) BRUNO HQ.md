---
id: ecef8116-1f4f-4009-a99e-d48a4f789f6a
title: "BRUNO HQ"
type: "guide"
project: "Distillation"
tags:
  - "#guide"
  - "#project"
  - "#ld/living"
  - "#stack/python"
  - "#status/shipped"
  - "#cluster/personal"
status: shipped
created: "2026-08-17"
updated: "2026-08-17"
source_path: "/Users/brunojaamaa/Desktop/Main Vault/Main"
---

# BRUNO HQ

**This vault is a spoke. The hub is `BRUNO`.**

| | |
|---|---|
| Hub vault | `/Users/brunojaamaa/Desktop/Main Vault/Main` |
| Registered Flint name | `BRUNO` |
| Hub map | `/Users/brunojaamaa/Desktop/Main Vault/Main/Mesh/(Map) BRUNO HQ.md` |
| Hub bootstrap | `/Users/brunojaamaa/Desktop/Main Vault/Main/CLAUDE.md` |
| Hub contract | `/Users/brunojaamaa/Desktop/Main Vault/Main/Mesh/(System) Flint Init.md` |
| Hub entry point | `/Users/brunojaamaa/Desktop/Main Vault/Main/Mesh/(System) START HERE.md` |

Go up with `[[(Map) BRUNO HQ]]`. That target lives in the hub vault, not this one, so it
resolves only when both vaults are open.

## distillation is new to the hub

⚠️ **The hub has no project note for this repo.** Its project index was written on
**2026-08-06**; this repo's first commit is **2026-08-14**. This vault is the first record of
it anywhere in the knowledge system.

What the hub should gain:

| Hub artefact | What to add |
|---|---|
| `Mesh/Notes/Projects/` | A project note, sourced from [[(Report) Project Summary]] |
| `(Dashboard) Portfolio` | A row: shipped, public repo, solo build, ML rather than web |
| `(Dashboard) Stack` | The **first Python and ML project** in the portfolio. MLX, mlx-lm, LoRA, Qwen3.5, Ollama, uv, pytest |
| `(Dashboard) Repo Documentation` | A **1,121-line** masterplan, a **757-line** SYNC ledger, a **414-line** METHODOLOGY and a **606-line** README |
| `(Report) 004 Incidents and Postmortems` | Two entries: the macOS GPU-driver kernel panic that killed a training run at iteration ~1,170 of 1,200, and the Ollama `num_ctx` default that drove the machine into **7.7 GB** of swap and took free disk from 12 GB to 4 GB mid-run |

## The cross-project link that matters

**This project measures a classifier that is live in another of Bruno's products.** The
incumbent it benchmarks against is `classifyWireItem()` in the Sentinel backend, the iOS
news-intelligence product at `/Users/brunojaamaa/Desktop/AI REPORTING APP MVP`. This repo found
**six defects** in that function, each reproduced and pinned by a passing test, and measured it
at **0.337 macro-F1** with `consumer` at **0.000 F1**.

That finding belongs in Sentinel's own notes as well as here. It is actionable product work, not
just a benchmark row, and it includes a concrete recommendation: **the taxonomy is missing a
ninth class**, `politics`.

## Logging back to the hub

```bash
node "/Users/brunojaamaa/Desktop/Main Vault/Main/Shards/tools/obsidianlog.mjs" \
  --actor "claude:<who>" --op <op> --target "<what>" --result "<outcome>" \
  --trigger "<why>" --project "/Users/brunojaamaa/Desktop/distillation"
```

Ops used by this vault: `vault-init` · `audit` · `note-create` · `sync` · `verify`.
The project log is `/Users/brunojaamaa/Desktop/distillation/OBSIDIANLOG.md`.

## Back

[[(Map) Master Map]] · [[(System) Flint Init]] · [[(Report) Project Summary]]
