---
id: cf13be14-3c34-4215-9327-4d0ccdbcd0a5
title: "External Services"
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
source_path: "/Users/brunojaamaa/Desktop/distillation"
---

# External Services

**Nothing in this project calls a paid API, and nothing needs a credential.** Every arm ran
locally at **$0**. That was a decision, not a coincidence: an open-weight teacher run locally
needs no owner gate, no key, and no terms-of-service problem when the resulting weights are
published.

## Runtime

| Service | Role | State |
|---|---|---|
| **Ollama**, local | Serves the teacher, `hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M`, **22 GB**. Reached over HTTP by `src/teacher.py` with `httpx`, JSON-schema-constrained decoding, temperature 0, `num_ctx` pinned to 2048 | ⚫ **weights deleted.** `~/.ollama` is now **12 KB** |
| **MLX**, local | Trains and serves the student on Apple silicon Metal | 🟢 installed in `.venv` |
| **63 public RSS feeds** plus **83 section feeds** | The corpus source. Zero credentials | 🟢 reachable, but the window has moved |
| **GDELT** | The planned corpus backfill | ⚫ **unusable.** One request succeeds, then HTTP **429** on everything after, verified at 20 s and 65 s spacing, **0 rows in 20 minutes** |

## Model distribution

| Service | Role | State |
|---|---|---|
| **HuggingFace Hub** | Source of `mlx-community/Qwen3.5-4B-bf16` at revision `491fdc7c...`, and of the teacher GGUF via Ollama | ⚫ **local cache deleted.** `~/.cache/huggingface/hub` does not exist |
| **HuggingFace, as a publish target** | Would host the adapter and the lineage widget | ⏭ **deferred** owner gate. `git-lfs` and `huggingface-cli` are **deliberately uninstalled** |

## Publication

| Service | Role | State |
|---|---|---|
| **GitHub** | `br9704/distillation`, public, MIT, **10** topics | 🟢 approved and executed 2026-08-15 |
| **GitHub Actions** | `ci.yml` on **`macos-14`** | 🟢 green |
| **brunojaamaa.dev** | Case study at `/projects/distillation`, consuming `PROJECT.json` | ❓ **not verified.** No network call was made by this audit |

## Cost model, and what it is not

The cost figures come from **published serverless list prices**, retrieved 2026-08-15, applied
to **measured** token counts:

| Tier | Rate |
|---|---|
| Under 4B parameters | **$0.10 / 1M tokens** |
| MoE up to 56B | **$0.50 / 1M tokens** |

Both are flat across input and output, which is the rare case where a price applies to a specific
open model without guessing.

```
regex     $0.0000 / 1k requests
teacher   $0.1547 / 1k requests   (302.98 in + 6.51 out) x 1000 = 309,490 tokens x $0.50/1M
student   $0.0037 / 1k requests   ( 35.98 in + 1.51 out) x 1000 =  37,490 tokens x $0.10/1M
```

**41.3x = 5.0x price tier multiplied by 8.26x fewer tokens.** Neither factor alone produces it.

Both sensitivities are published beside the headline: billed **one tier up**, because Qwen3.5-4B
is 4.21B parameters and just over the sub-4B boundary, it is **8.3x**. Had the student kept the
teacher's full prompt it would have been **5.1x**, and that gap is what amendment A3 bought.

## Developer-side integrations, not part of the project

| Service | Where | Note |
|---|---|---|
| **Aethereum MCP server** | `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`, `opencode.json`, `.codex/config.toml` | The agent coordination room, described in `AGENTS.md` and the byte-identical `GEMINI.md`. ⚠️ Four of those files hold a plaintext bearer token; all are gitignored and **none was opened by this audit**. The pre-publication scan for the public-repo gate specifically confirmed the Aethereum join code was **absent** from the repo, unlike the `mcpaudit` repo where it is committed |

## Related

[[(Note) Teacher and Student Models]] · [[(Note) Environment Variables]] ·
[[(Note) CI and Publication]] · [[(Note) The Corpus and Splits]] ·
[[(Index) 40 Data & Integrations]]
