---
id: ab45c61e-f9e7-4d50-b027-a6d85dcfde5e
title: "Environment Variables"
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

# Environment Variables

**This project needs no credential to do its job, and there is no `.env` file in the repo.**
Every arm ran locally against an open-weight model. That is a direct consequence of the
open-teacher decision: no key, no owner gate, no terms-of-service problem.

## What the pipeline reads instead of environment variables

Configuration lives in files, not the environment, and every value is copied into the run record
so a result can be traced:

| Source | What it carries |
|---|---|
| `configs/lora.yaml` | Base model, **pinned revision SHA**, every LoRA hyperparameter, the seed |
| `pyproject.toml` | The Python pin (`>=3.12,<3.13`) and the dependency set |
| `runs/*/hyperparams.json` | The resolved copy of all of the above, plus dataset SHA-256s, library versions, git commit and dirty flag |

`pyyaml` is a **declared** runtime dependency specifically so `src/record_run.py` and
`src/evaluate.py` can read the pinned revision out of `configs/lora.yaml` without depending on
mlx-lm continuing to pull it in transitively. The comment in `pyproject.toml` says why: **a
result's provenance must not depend on a transitive dependency staying put.**

## Local paths the code resolves

| Path | Used by |
|---|---|
| `~/.cache/huggingface/hub` | `src/merge_student.py`, to prefer the on-disk snapshot directory over the bare repo id. ⚠️ **This directory no longer exists.** See [[(Note) The Deleted Student Weights]] |
| The Ollama HTTP endpoint, local | `src/teacher.py` via `httpx` |

`merge_student.py` resolves the snapshot directory rather than reaching for the network, and the
docstring explains why: `mlx_lm fuse` goes through `snapshot_download(local_files_only=True)`,
which raises if any file recorded in the repo is absent from the cache, **including
`.gitattributes`, which carries no weights and which the original download skipped**. The
snapshot directory is named by the revision SHA, so pointing at it **keeps the pin rather than
weakening it**: the path itself is the provenance.

## CI

`.github/workflows/ci.yml` uses **no secrets at all**. It syncs, tests and greps.

## The credentials that are on disk and gitignored ⚠️

`.gitignore` covers `.env`, `.env.*` (with `!.env.example` un-ignored), `.mcp.json`,
`.cursor/mcp.json`, `.vscode/mcp.json`, `opencode.json` and `.ccline.json`.

Four of those hold an `Authorization` bearer header for the hosted Aethereum MCP server. **None
was opened by this audit.** Only `.codex/config.toml` uses env-var indirection, which is the
correct pattern.

**Nothing leaked to git**, and that was verified rather than assumed: the pre-publication scan
for the public-repo gate specifically checked history for `.env`, `.mcp.json` and credentials and
found none.

## Related

[[(Note) External Services]] · [[(Note) CI and Publication]] ·
[[(Note) The Deleted Student Weights]] · [[(Index) 70 Ops, Deploy & Env]]
