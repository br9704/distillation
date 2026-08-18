# CLAUDE.md — Agent Bootstrap

**You are working inside the `(Flint) Distillation` vault — the knowledge vault for
`distillation`.**

This vault is not the codebase. The codebase is the tree one level up, at
`/Users/brunojaamaa/Desktop/distillation`. Resolve it properly rather than hardcoding the path:

```bash
flint resolve codebase "Distillation"
```

## What this project is, in one line

A **4B LoRA student** distilled from a **35B open-weight teacher**, benchmarked against the
**keyword regex running in production** in the Sentinel iOS product, on 500 headlines held out
before a single label existed. Student **0.840 macro-F1** against the incumbent's **0.337**, at
**41.3x** lower list cost and **2.4x** lower latency than the teacher.

## ⚠️ Read this before you run anything

**`models/student-merged/` (7.9 GB) and the base HuggingFace weights were deleted on
2026-08-16**, with Bruno's authorisation, during a storage migration.

- The **trained LoRA adapter survived** at `runs/current/best/adapters.safetensors`, **3.67 MB**.
- **Every published result survived**; all 11 files under `results/` are committed.
- Restoring the merged model needs an **~8.5 GB download and minutes of compute**, not a training
  run. A training run is only needed if the adapter is lost, and it takes **~64 minutes**.
- ⚠️ **The adapter and all of `data/` are gitignored.** Local disk is their only copy, and the
  corpus **cannot be re-harvested** because the RSS window has moved.

Read `Mesh/40 Data & Integrations/(Note) The Deleted Student Weights.md` in full before touching
anything heavy.

## Read this first

**`Mesh/(System) Flint Init.md`** — the workspace contract. Read it before you write anything.

## Then

1. `Mesh/(Report) Project Summary.md` — one page, the whole project.
2. `Mesh/(Map) Master Map.md` — the graph and the "start here if you want to…" list.
3. The numbered section index you need: `00 Overview`, `10 Architecture`, `20 Codebase Map`,
   `30 Setup & Run`, `40 Data & Integrations`, `50 Decisions & ADRs`,
   `60 Roadmap, Tasks & Ideas`, `70 Ops, Deploy & Env`, `80 Testing & Quality`, `90 Reference`.

## Order of trust

`masterplan.md` then `SYNC.md` then `CLAUDE.md` in the repo, then this vault. Above all of them,
the committed artefacts under `results/`.

⚠️ The repo's `CLAUDE.md` and README both say **"nothing is published"** and **"no remote
exists"**. Both are **false**: the repo is public at `github.com/br9704/distillation`. See
`Mesh/(Report) Gaps & Questions.md`.

## Hard rules

- **Read-only outside this vault.** Never `git commit`, `git push`, `git checkout`, `git reset`,
  `git clean` or `git rebase` in the repo.
- **Never run training. Never download model weights. Never `uv sync`. Never `pip install`.**
- **Never delete or move anything under `runs/`, `data/` or `models/`.** Two of those hold the
  project's only copies of irreplaceable artefacts.
- **Never open** `.env*`, `*.pem`, `*.key`, `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`
  or `opencode.json`. Record variable names only.
- **REPO WINS OVER NOTE.** Edit the fact, do not rewrite the note.
- **Tag list items must be quoted** in frontmatter: `- "#note"`. An unquoted `#` starts a YAML
  comment and silently empties the tag list.
- **Every new note gets a fresh lowercase UUID**: `uuidgen | tr 'A-Z' 'a-z'`.
- **Log material actions** with
  `node "/Users/brunojaamaa/Desktop/Main Vault/Main/Shards/tools/obsidianlog.mjs"`.
- Run `flint sync` after adding notes.

## Repeatable jobs

`Shards/project/` holds four: `codebase-map-refresh`, `changelog-from-git`, `onboarding-guide`,
`vault-audit`.

Up: `Mesh/(Guide) BRUNO HQ.md` → the hub at `/Users/brunojaamaa/Desktop/Main Vault/Main`.
