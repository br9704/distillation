---
id: a07c00a9-5c9f-47ef-a7d3-ab0ee302d086
title: "Gaps & Questions"
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
source_path: "/Users/brunojaamaa/Desktop/distillation"
---

# Gaps & Questions

**Everything this vault could not establish, plus every contradiction found between the repo's
own documents.** Nothing here is invented. Where a fact is unknown, the row says where it was
looked for.

## Contradictions inside the repo

| # | Finding | Evidence | Severity |
|---|---|---|---|
| 1 | ⚠️ **`CLAUDE.md` says "nothing is published, no remote exists"**, and the README's Status section says "Nothing here is published". Both are **false**. Commit `86b43ee` records the public-repo gate as approved and executed on 2026-08-15, `origin` is `https://github.com/br9704/distillation.git`, and the tree is clean with **0** unpushed | `git log`, `git remote -v`, `git status` against `CLAUDE.md` and `README.md` | ⚠️ **misleading to any agent reading either file as current state**, and it is exactly what the repo's own rule about updating the current-state line at every sprint close exists to prevent |
| 2 | ⚠️ **`.gitignore` calls `data/` "regenerable from `src/harvest.py` + `src/gdelt.py`".** The repo's own measurements say it is not: a second RSS pass yields **7** rows, GDELT returns **429** on everything after the first request, and the README calls the corpus "a snapshot of August 2026 rather than a stable benchmark" | `.gitignore` against `README.md`, `masterplan.md` amendment A1, and `results/corpus_stats.json` | ⚠️ **this comment is the reason nobody has backed the corpus up** |
| 3 | **`masterplan.md` still says `EXPANSION_FEEDS` is 84.** `CLAUDE.md` records the corrected count as **83**, and separately corrects the feed catalog from 61 to **63** | `CLAUDE.md` current-state block versus `masterplan.md` | ⚫ cosmetic, and already flagged inside the repo |
| 4 | **`results/sanity_20.json` records what the merged model said**, and the merged model no longer exists on disk. The artefact is still valid evidence of what happened; it just can no longer be re-derived without the ~8.5 GB download | `results/sanity_20.json` versus an empty `models/` | ⚫ documented in [[(Note) The Deleted Student Weights]] |
| 5 | **`AGENTS.md` and `GEMINI.md` are byte-identical**, 3,829 bytes each. Deliberate, one per agent harness, but it means an edit to one silently diverges them | `stat` and `diff` | ⚫ |
| 6 | **`PROJECT.json` names the project `DISTILLATION`**, `pyproject.toml` names it `distillation`, and this Flint is registered as `Distillation` | three files | ⚫ trivial |

## Storage and backup ⚠️

| # | Finding | Evidence | Severity |
|---|---|---|---|
| 7 | ⚠️ **The shipped LoRA adapter has exactly one copy, and git does not have it.** `runs/current/best/adapters.safetensors`, **3.67 MB**, matched by the `*.safetensors` rule in `.gitignore`. Confirmed with `git status --ignored` | `.gitignore`, `git ls-files runs/`, `git status --ignored` | ⚠️ **losing it costs an ~8.5 GB download plus a 64-minute training run, and the retrained result would not reproduce 0.840 exactly** |
| 8 | ⚠️ **The corpus has exactly one copy, and git does not have it.** All of `data/`, **5.1 MB**. And per row 2, it cannot be re-harvested | same | ⚠️ **this one is genuinely irreplaceable** |
| 9 | **`models/student-merged/`, 7.9 GB, was deleted on 2026-08-16** with Bruno's authorisation, along with the base HuggingFace weights. `~/.cache/huggingface/hub` does not exist | empty `models/`, absent cache directory | 🟡 **recoverable**, see [[(Note) The Deleted Student Weights]] |
| 10 | **`runs/current/hyperparams.json` records the training commit as `39333c7` with `"dirty": true`.** The exact tree the adapter was trained from **cannot be recovered from git alone**. This is recorded rather than hidden, which is the right call, but it is a real limit on reproducibility | `runs/current/hyperparams.json` | 🟡 |

## Not verified, and why

| # | Question | Where it was looked for | Why unresolved |
|---|---|---|---|
| 11 | Is `brunojaamaa.dev/projects/distillation` live? | `PROJECT.json` `links.caseStudy`, commit `a8a52d1` | > [!todo] Missing - not found in the repo. **No network call was made by this audit.** Commit `a8a52d1` says the case study was linked, but the sibling `mcpaudit` repo records the equivalent portfolio promotion as **deliberately not executed** because the portfolio tree was dirty, so the same may apply here |
| 12 | Is the GitHub repo actually public right now, with the 10 topics and green CI? | `masterplan.md` S9, `PROJECT.json` `github` block | > [!todo] Missing - the repo asserts it as of 2026-08-15. **GitHub was not queried** |
| 13 | Does `uv run pytest -q` pass today? | `.github/workflows/ci.yml`, `CLAUDE.md` | > [!todo] Missing - **the test suite was not run.** This audit read the repo and did not execute it. `CLAUDE.md` records **139 tests green** as of 2026-08-15. **90 test functions** were counted statically |
| 14 | What is the student's run-to-run variance? | `results/`, `masterplan.md` | **Unknown, and the repo says so.** One run, one seed, one machine, one 500-example draw. A second seed is the repo's own recommended next step |
| 15 | Are the two open owner gates still open? | `masterplan.md` S9 | > [!todo] Missing - the last written word is 2026-08-15, and both were open. Only Bruno can close them |
| 16 | Does the surviving adapter still load and score 0.840? | `results/summary.json` provenance | > [!todo] Missing - **cannot be checked without the base weights**, and downloading them was out of bounds for this audit. The adapter's SHA-256 in `results/summary.json` can at least prove it is the same file |

## Coverage gaps the project states about itself

Listed so a reader does not have to reconstruct them from the README.

| # | Gap |
|---|---|
| 17 | **Gold is the teacher**, so the student's 85.4% is agreement, not correctness. The teacher's own ceiling is **84%** |
| 18 | **The taxonomy has no `politics` class**, an irreducible noise floor for every arm, and a real product finding |
| 19 | **`consumer` recall is 0.529**, the tail-class cost amendment A1 predicted when the corpus target dropped |
| 20 | **Headline-only, English-only**, despite a corpus including DW, France24, NHK and SCMP |
| 21 | **Cost is list-price arithmetic**, not measured spend. 41.3x optimistic, 8.3x pessimistic, both published |
| 22 | **Teacher tokens were counted with the student's tokeniser**, because the teacher's weights were deleted in S4. Same Qwen family, not the same file |

## Questions for Bruno

1. **Can `runs/current/best/adapters.safetensors` and `data/` be backed up today?** Together they
   are **9 MB**, they are the only irreplaceable things in the project, and neither is in git.
2. Do you want the deferred Hugging Face gate reopened **for the adapter only**? It would solve
   question 1 and give the lineage third-party corroboration, and the masterplan already
   recommends the adapter repo over the merged one.
3. Should the six regex defects and the missing `politics` class be raised as **Sentinel product
   work**? They are actionable findings about a live classifier, not just benchmark rows.
4. Is a second training seed worth an hour of GPU time to close the variance gap? The repo
   recommends it over the paid ablation.

## Related

[[(Note) The Deleted Student Weights]] · [[(Note) Honest State]] · [[(Report) Folder Audit]] ·
[[(Note) Roadmap and Owner Gates]] · [[(Report) Project Summary]] · [[(Report) Build Log]]
