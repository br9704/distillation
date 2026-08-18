---
id: 6bb7d3dc-b5d6-47c8-89ba-16048c60a73a
title: "Sources"
type: "index"
project: "Distillation"
tags:
  - "#index"
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

# Sources

**`Sources/` is read-only and currently empty.** Nothing has been imported, deliberately:
everything this vault describes lives in the repo one level up, and copying it in would create a
second copy that drifts. Sources are linked by absolute path in each note's `source_path:`.

## Where the primary sources actually are

| Source | Absolute path | Bytes |
|---|---|---|
| The sprint log | `/Users/brunojaamaa/Desktop/distillation/masterplan.md` | 77,662 |
| The decision ledger | `/Users/brunojaamaa/Desktop/distillation/SYNC.md` | 51,122 |
| The public write-up | `/Users/brunojaamaa/Desktop/distillation/README.md` | 39,820 |
| The method | `/Users/brunojaamaa/Desktop/distillation/METHODOLOGY.md` | 21,673 |
| The agent contract | `/Users/brunojaamaa/Desktop/distillation/CLAUDE.md` | 15,997 |
| The portfolio record | `/Users/brunojaamaa/Desktop/distillation/PROJECT.json` | 12,876 |
| The original brief | `/Users/brunojaamaa/Desktop/distillation/ENGINEERPROMPT.md` | 11,661 |
| Third-party attributions | `/Users/brunojaamaa/Desktop/distillation/NOTICE.md` | 1,898 |
| **The evidence** | `/Users/brunojaamaa/Desktop/distillation/results/` | 344 KB, 11 files |
| **The charts** | `/Users/brunojaamaa/Desktop/distillation/charts/` | 488 KB, 5 files |
| **The run record** | `/Users/brunojaamaa/Desktop/distillation/runs/current/` | 49 MB |
| ⚠️ **The corpus** | `/Users/brunojaamaa/Desktop/distillation/data/` | 5.1 MB, **gitignored, no backup** |

**Order of trust:** `masterplan.md` then `SYNC.md` then `CLAUDE.md` then this vault. Above all of
them, the committed artefacts under `results/`, which every published number cites. See
[[(System) Flint Init]].

## Never opened

`.mcp.json` · `.cursor/mcp.json` · `.vscode/mcp.json` · `opencode.json`. All four hold a live
bearer token and all four are gitignored. Grepped for key names only.

## Never run

No training, no weight download, no `uv sync`, no `pip install`, and the test suite was not
executed.

## Related

[[(System) Flint Init]] · [[(Report) Folder Audit]] · [[(Note) Charts and Artefacts]] ·
[[(Map) Master Map]]
