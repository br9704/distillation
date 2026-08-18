---
id: db70fd44-699b-41b7-b6ba-499a6d5e56bc
title: "codebase-map-refresh"
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

# codebase-map-refresh

**Re-derive [[(Note) Source Tree]], [[(Report) Folder Audit]] and
[[(Index) Complete File Inventory]] from the repo as it is today.** **REPO WINS OVER NOTE.**

## Hard rules for this repo

Read-only outside the vault. **Never run training, never download weights, never `uv sync`,
never `pip install`.** Never open `.env*`, `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`
or `opencode.json`.

## Steps

1. **Check for dataless iCloud files first.** A read on one hangs indefinitely and macOS here has
   no `timeout`.

   ```bash
   find /Users/brunojaamaa/Desktop/distillation -type f -flags +dataless 2>/dev/null | head -20
   ```

   Measured **0** on 2026-08-17.

2. **Recount, excluding `.venv` and `__pycache__`.**

   ```bash
   cd /Users/brunojaamaa/Desktop/distillation
   git ls-files | wc -l
   find . -type f -not -path "./.git/*" -not -path "./.venv/*" -not -name "*.pyc" | wc -l
   du -sh . .git .venv data results runs charts src tests
   git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn
   ```

3. ⚠️ **Check what is still untracked and irreplaceable.** This is the point of the shard.

   ```bash
   git status --ignored --short runs/ data/
   ls -la models/
   ls ~/.cache/huggingface/hub 2>&1
   du -sh ~/.ollama 2>/dev/null
   ```

   Baseline on 2026-08-17: `models/` **empty**, HF cache **absent**, `~/.ollama` **12 KB**, and
   `runs/*/adapters/`, `runs/current/best/adapters.safetensors` and all of `data/` **ignored**.
   If any of that changes, [[(Note) The Deleted Student Weights]] needs updating.

4. **Re-list `src/` with sizes and line counts.**

   ```bash
   find src -type f -name "*.py" -exec stat -f '%z %N' {} \; | sort -k2
   wc -l src/*.py tests/*.py
   ```

5. **Re-grep for rot.** Baseline is **0** in `src/` and `tests/`.

   ```bash
   grep -rn "TODO\|FIXME\|HACK\|XXX" src tests
   ```

6. **Re-count tests statically.** Do not run the suite unless asked.

   ```bash
   grep -c "def test_" tests/*.py
   ```

   Baseline: **90** functions, **139** after parametrisation per `CLAUDE.md`.

7. **Update the notes, do not rewrite them.** Edit the fact, bump `updated:`.

8. **Log it** with `--op audit`, then `flint sync`.

## Related

[[changelog-from-git]] · [[vault-audit]] · [[onboarding-guide]] · [[(Map) Master Map]]
