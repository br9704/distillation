---
id: 0ef7db7d-1954-4084-a612-d52743e9b708
title: "Build Log"
type: "report"
project: "Distillation"
tags:
  - "#report"
  - "#project"
  - "#ld/living"
  - "#stack/python"
  - "#status/shipped"
  - "#cluster/personal"
status: shipped
created: "2026-08-17"
updated: "2026-08-17"
source_path: "/Users/brunojaamaa/Desktop/distillation/(Flint) Distillation"
---

# Build Log

**How this vault was built, on 2026-08-17, and what the verification found.** Written last, so it
describes the finished state.

## What was done

| Step | Command or action | Result |
|---|---|---|
| Hazard check | `find /Users/brunojaamaa/Desktop/distillation -type f -flags +dataless` | **0** dataless iCloud files. No read could hang |
| Log | `obsidianlog.mjs --op vault-init` | Appended to the project log and rolled up to the hub |
| Create | `flint init "Distillation" --path /Users/brunojaamaa/Desktop/distillation --no-open` | Vault at `<parent>/(Flint) Distillation/`, auto-registered |
| Sync | `flint sync` | `.obsidian/` cloned, **2** shards applied |
| Reference | `flint reference codebase "Distillation" /Users/brunojaamaa/Desktop/distillation` | Added |
| Fulfil | `flint fulfill codebase "Distillation" /Users/brunojaamaa/Desktop/distillation` | Fulfilled |
| Resolve | `flint resolve codebase "Distillation"` | Returns the repo path, one worktree on `main` |
| Audit | read-only pass over the repo | Logged with `--op audit` |
| Build | **46** files written | See the tree below |
| Verify | a Node script over the vault | See below |

⚠️ **`flint sync`, `flint reference` and `flint fulfill` must be run from inside the vault.** Run
from the repo root they fail with "Not inside a Flint workspace", because the repo root is the
vault's **parent**. The `--path` flag on `flint init` is the parent directory, confirmed.

## Verification results

Run over `Mesh/`, `Sources/`, `Media/`, `Exports/` and `Shards/project/`. Flint's own plumbing
(`.obsidian/`, `.flint/`, `Shards/Flint/`, `Shards/Orbh/`, `Mesh/Main/`, `Mesh/Metadata/`) is
excluded, because this build did not author it.

| Gate | Result |
|---|---|
| Notes checked | **45** |
| Unique `id` values | **45**, no duplicates |
| Broken wikilinks | **0** |
| Orphan notes | **0**, every note has at least one inbound link |
| Frontmatter parses | **45 of 45** |
| Required keys present | `id`, `title`, `type`, `project`, `tags`, `status`, `created`, `updated` on **all 45** |
| Unquoted tag list items | **0**. Every tag is quoted, so no tag list is silently empty |
| Repo folders documented or excluded | **all**, see [[(Report) Folder Audit]] |

**One allowlisted cross-vault target:** `(Map) BRUNO HQ` lives in the hub vault at
`/Users/brunojaamaa/Desktop/Main Vault/Main/Mesh/(Map) BRUNO HQ.md`. It is linked from
[[(Map) Master Map]], [[(Guide) BRUNO HQ]] and [[(Report) Project Summary]] on purpose and
resolves only when both vaults are open. It is the **only** link in this vault that does not
resolve locally, and it is intentional rather than a defect.

**One verification bug worth recording.** The first run flagged two "broken links" inside the
Mermaid diagram in [[(Note) System Architecture]]: Mermaid's subroutine node shape uses double
square brackets, which a naive wikilink regex reads as a link. The nodes were changed to the
parallelogram shape. **A diagramming syntax that collides with a linking syntax is a real trap**,
and any future verifier should either skip fenced code blocks or expect it.

## Tree

```
(Flint) Distillation/
├── CLAUDE.md
├── Mesh/
│   ├── (System) Flint Init.md
│   ├── (Map) Master Map.md
│   ├── (Report) Project Summary.md
│   ├── (Report) Folder Audit.md
│   ├── (Index) Complete File Inventory.md
│   ├── (Report) Gaps & Questions.md
│   ├── (Report) Build Log.md
│   ├── (Guide) BRUNO HQ.md
│   ├── 00 Overview/            (Index) + What Distillation Is · Honest State · Git History
│   ├── 10 Architecture/        (Index) + System Architecture · The Training Pipeline · Evaluation and Scoring
│   ├── 20 Codebase Map/        (Index) + Source Tree · Charts and Artefacts
│   ├── 30 Setup & Run/         (Index) + Install and Run · Command Surface
│   ├── 40 Data & Integrations/ (Index) + The Deleted Student Weights ⚠️ · The Corpus and Splits · External Services
│   ├── 50 Decisions & ADRs/    (Index) + Locked Decisions and Amendments
│   ├── 60 Roadmap, Tasks & Ideas/ (Index) + Roadmap and Owner Gates
│   ├── 70 Ops, Deploy & Env/   (Index) + CI and Publication · Environment Variables
│   ├── 80 Testing & Quality/   (Index) + Test Suite
│   └── 90 Reference/           (Index) + Results Reference · Teacher and Student Models
├── Sources/(Index) Sources.md
├── Media/(Note) Media.md
├── Exports/(Note) Exports.md
└── Shards/project/             codebase-map-refresh · changelog-from-git · onboarding-guide · vault-audit
```

**46 files authored**: 45 notes plus the vault-root `CLAUDE.md`, which carries no frontmatter by
convention and is therefore excluded from the note count.

## Sections kept and dropped

All **ten** numbered sections carry real content, so none was dropped. `Z0 Archive` was not
created, because a two-day-old repo has nothing archived and an empty folder would be padding.

## What was deliberately not done

- **No training run, no weight download, no `uv sync`, no `pip install`.** These were hard
  constraints on the audit, and they are also the right default for this repo permanently.
- **The test suite was not executed.** Test counts here are static: **90** functions counted by
  grep, which the repo's own `CLAUDE.md` reports as **139** after parametrisation.
- **No network calls.** GitHub, HuggingFace and `brunojaamaa.dev` were never queried, so every
  claim about them comes from the repo's own documents and is dated. The open questions are rows
  in [[(Report) Gaps & Questions]].
- **No file in the repo was modified**, except `OBSIDIANLOG.md`, which the shared logger appends
  to. Nothing under `runs/`, `data/` or `models/` was touched, moved or read into the vault.
- **Four config files were never opened**: `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`,
  `opencode.json`. Grepped for key names only.
- **No git operation beyond read.**

## The finding this build exists to record

⚠️ **`models/student-merged/` (7.9 GB) and the base HuggingFace weights were deleted on
2026-08-16.** The trained adapter survived, every published result survived, and most of the repo
still runs. **Restoring the merged model needs an ~8.5 GB download and minutes of compute, not a
training run**, because the adapter is still on disk. Full detail in
[[(Note) The Deleted Student Weights]].

The larger risk this audit surfaced, which was not in the brief: **the surviving adapter and the
entire corpus are gitignored and have no backup**, and the corpus cannot be re-harvested because
the RSS window has moved. That is **9 MB** of irreplaceable material with one copy, on one
laptop.

## One warning, recorded rather than hidden

`flint sync` reports `Shards/project` as an **orphan shard**, because the folder is not declared
in `flint.toml` under `[shards]`. Nothing was deleted and all four files are intact. The four job
notes are plain markdown rather than a packaged shard, which is the same shape the hub uses for
`Shards/hq/`.

## Notes for the next run

The vault is a **living document**. When the repo changes, edit the fact and bump `updated:` in
frontmatter. Do not create a second note for the same thing. The four shards in
`Shards/project/` exist so this does not have to be re-derived by hand, and `vault-audit` carries
a fifth gate specific to this repo: **check that the adapter and `data/` are still there.**

## Related

[[(Report) Folder Audit]] · [[(Report) Gaps & Questions]] ·
[[(Note) The Deleted Student Weights]] · [[vault-audit]] · [[(System) Flint Init]] ·
[[(Map) Master Map]] · [[(Report) Project Summary]]
