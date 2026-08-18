---
id: 4ea76858-a21e-48ab-ac23-dca082d26a41
title: "Flint Init"
type: "system"
project: "Distillation"
tags:
  - "#system"
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

# Flint Init

**This is the knowledge vault for `distillation`, not the codebase.** The codebase is the tree
one level up at `/Users/brunojaamaa/Desktop/distillation`, and this vault sits inside it as
`(Flint) Distillation/`.

Resolve the code properly rather than hardcoding a path:

```bash
flint resolve codebase "Distillation"
```

## The contract

| | |
|---|---|
| Registered Flint name | `Distillation` |
| Vault path | `/Users/brunojaamaa/Desktop/distillation/(Flint) Distillation` |
| Codebase | `/Users/brunojaamaa/Desktop/distillation` |
| Codebase reference | fulfilled, `flint reference list` shows a green tick |
| Hub | `BRUNO` at `/Users/brunojaamaa/Desktop/Main Vault/Main` |
| Project log | `/Users/brunojaamaa/Desktop/distillation/OBSIDIANLOG.md` |

## ⚠️ Read this before touching anything heavy

**`models/student-merged/` was deleted on 2026-08-16 and the base HuggingFace weights went with
it.** The trained LoRA adapter survives, the results are all committed, and most of the repo
still runs. Read [[(Note) The Deleted Student Weights]] **before** running anything that loads a
model, and never start a download or a training run to "fix" it without asking.

**Never run training. Never download model weights. Never `uv sync`. Never `pip install`.**

## Where things go

| Folder | What lives there |
|---|---|
| `Mesh/` | Every note. The only place you write prose. |
| `Mesh/00` to `Mesh/90` | The ten numbered sections, each with its own `(Index)`. |
| `Sources/` | Read-only imports. Indexed by [[(Index) Sources]]. |
| `Media/` | Images. See [[(Note) Media]]. The five committed charts stay in the repo. |
| `Exports/` | Generated for an outside audience. See [[(Note) Exports]]. |
| `Shards/project/` | The four repeatable jobs written for this repo. |
| `Workspace/` | Scratch. Nothing durable. |

## Naming, without exceptions

Every file is `(Type) Name.md`. Types: `(System)`, `(Dashboard)`, `(Plan)`, `(Notepad)`,
`(Note)`, `(Report)`, `(Task)`, `(Index)`, `(Map)`, `(Guide)`. No new types.

Fresh lowercase UUID on every note:

```bash
uuidgen | tr 'A-Z' 'a-z'
```

Required frontmatter: `id`, `title`, `type`, `project`, `tags`, `status`, `created`, `updated`,
plus `source_path` where the note describes something on disk.

**Tag list items are quoted.** `- "#note"`, never `- #note`. An unquoted hash starts a YAML
comment and silently empties the whole tag list.

Wikilinks carry the full `(Type) Name`, never aliased. Link lists join with a middle dot.

## Safety rules

1. **Read-only outside this vault.** Never `git commit`, `git push`, `git checkout`,
   `git reset`, `git clean` or `git rebase` in the repo.
2. **Never run a training run, never download weights, never `uv sync` or `pip install`.**
   The repo's own disk budget is the reason half its sprint boundaries exist.
3. **Never open** `.env*`, `*.pem`, `*.key`, `.mcp.json`, `.cursor/mcp.json`,
   `.vscode/mcp.json` or `opencode.json`. Record variable names only.
4. **Do not touch `runs/`, `data/` or `models/`.** ⚠️ `runs/*/adapters/`, `runs/current/best/*.safetensors`
   and all of `data/` are **gitignored**, so local disk is their only copy. Deleting any of it
   destroys work that cannot be re-derived from the remote.
5. **REPO WINS OVER NOTE.** The code and the committed artefacts are right; the note gets fixed.
6. Log material actions. See [[(Guide) BRUNO HQ]]. Run `flint sync` after adding notes.

## Order of trust

`masterplan.md` then `SYNC.md` then `CLAUDE.md` then this vault. Above all of them, the
committed artefacts under `results/`, which every published number cites.

## Start

[[(Map) Master Map]] · [[(Report) Project Summary]] · [[(Note) The Deleted Student Weights]] ·
[[(Guide) BRUNO HQ]]
