---
id: 0eb2fbed-dd43-41e4-a62a-0368ddd36296
title: "CI and Publication"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/.github/workflows/ci.yml"
---

# CI and Publication

**One workflow, and it runs on `macos-14` on purpose.** MLX is a Metal library with no Linux
wheel, so an Ubuntu runner cannot even resolve this project's dependency set. The comment in the
file says it plainly: running CI on the architecture the project targets is **the honest
configuration, not a convenience**.

## `ci.yml`

Triggers: push to `main`, every pull request, and manual dispatch.

| Step | What it proves |
|---|---|
| `astral-sh/setup-uv@v5` with caching | |
| `uv sync --all-extras --dev` | The pinned Python 3.12 environment resolves. **Not 3.14**, because the ML wheels do not exist for it |
| `uv run pytest -q` | **139 tests** green |
| **Assert the reserved amber never reaches a chart** | Greps `src/` for `#FF9500` and fails unless every occurrence is inside a named constant. The design system reserves that colour for collision alerts, and `src/charts.py` names it so the constraint is documented. This step makes sure naming it is the only thing that ever happens to it |

`tests/test_charts_guard.py` goes further than the grep and reads the **committed PNGs pixel by
pixel** to prove the amber never appears in a rendered chart. `pillow` is a declared dev
dependency for exactly that reason: undeclared, the guard silently skips, which is the same as
not having it.

## What "publication" means here

There is no package, no registry and no deployed service. Publication is:

| Target | State |
|---|---|
| **GitHub repo public** | ✅ **Done, 2026-08-15.** `github.com/br9704/distillation`, MIT, **10** topics: distillation, lora, fine-tuning, mlx, apple-silicon, qwen, text-classification, open-weights, reproducible-research, python |
| **Hugging Face adapter** | ⏭ Deferred owner gate. `git-lfs` and `huggingface-cli` are **deliberately uninstalled**, because installing them would be preparing for a gate that may be declined |
| **Hugging Face merged weights** | ⏭ Deferred, and **recommended against regardless**: 7.9 GB to save a reader one `mlx_lm fuse` command is a maintenance liability, not a contribution |
| **The labelled dataset** | ❓ Still open |
| **brunojaamaa.dev case study** | ❓ Not verified. `PROJECT.json` points at `/projects/distillation` and commit `a8a52d1` links it, but **no network call was made by this audit** |

## The two fixes the public-repo gate required

1. **`LICENSE` had third-party notices appended to the MIT text**, so GitHub's licence detector
   classified the repo as "Other". Splitting them into `NOTICE.md` fixed it, in commit `de1fd47`.
2. **The README claimed `METHODOLOGY.md` did not exist** while the file sat committed beside it.

The pre-publication scan found **no `.env`, no `.mcp.json`, no credentials in history, and the
Aethereum join code correctly absent**. That last point is worth noting because the sibling
`mcpaudit` repo does **not** pass the same check: its `CLAUDE.md` commits a join code to a public
repo. Same author, same week, opposite outcome, and the difference is that this project ran an
explicit scan before flipping the switch.

## ⚠️ Two documents that contradict the git log

`CLAUDE.md` and the README's Status section both say **"nothing is published"** and **"no remote
exists"**. Commit `86b43ee` says otherwise, `git remote -v` says otherwise, and the working tree
is clean with 0 unpushed. Both were written before the gate and were never updated after it. See
[[(Report) Gaps & Questions]].

## Nothing is versioned

**Zero git tags.** There is no release artefact, so there is nothing to tag. If the adapter is
ever pushed to Hugging Face, that would be the first thing worth a version.

## Related

[[(Note) Environment Variables]] · [[(Note) Roadmap and Owner Gates]] ·
[[(Note) Test Suite]] · [[(Note) Git History]] · [[(Index) 70 Ops, Deploy & Env]]
