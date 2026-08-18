---
id: 1ea0f06d-679f-482c-ba0a-d44cea84994f
title: "Git History"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/.git"
---

# Git History

**19 commits over two days, one branch, zero tags.** One commit per sprint, in order, with no
reverts and no merges.

| | |
|---|---|
| Commits | **19** |
| First | **2026-08-14** · `1fabd33` · S0 foundation |
| Last | **2026-08-15** · `a8a52d1` · docs: link the case study on brunojaamaa.dev |
| Branches | `main` only, tracking `origin/main` |
| Remotes | **1** · `origin` → `https://github.com/br9704/distillation.git` |
| Tags | **0** |
| Working tree | ✅ clean |
| Unpushed | **0** |

## All 19 commits, newest first

| Commit | Subject |
|---|---|
| `a8a52d1` | docs: link the case study on brunojaamaa.dev |
| `18f6885` | README: lead with the plain-language explanation |
| `6043e31` | README: explain in plain language what this is and what I did; drop em dashes |
| `86b43ee` | **S9: public-repo gate approved and executed; Hugging Face deferred** |
| `de1fd47` | Split third-party notices out of LICENSE so GitHub detects MIT |
| `8e643a4` | docs: point the README at METHODOLOGY.md and correct the sprint state |
| `65c4637` | S8: METHODOLOGY.md, and the sprint closes, only owner gates remain |
| `0981a77` | **S6+S7: the student is trained, merged and measured on all three arms** |
| `39333c7` | S6 (wip): cost model on real published tiers, training-curve chart |
| `61af2e3` | S6 (wip): A3 reverses the S5 prompt decision; eval harness written |
| `b560ec9` | S5: Qwen3.5-4B confirmed trainable; probe caught a silent-failure bug |
| `5078744` | **S4: 3,706 labels at 0.00% unparseable, ceiling measured, 21 GB reclaimed** |
| `b4dfc5f` | S4 (wip): held-out labelled, hand audit, label-distribution chart |
| `1391d5d` | S3: teacher live, prompt frozen at v1, pilot clean |
| `7ebc49d` | S5 risk pre-verified during the S3 download wait: mlx-lm supports qwen3_5 |
| `61b00cb` | S3 (wip): teacher labelling client, prompt v1, parser guards |
| `4ad0823` | S2: corpus rebuilt from public RSS, 3,706 headlines, zero credentials |
| `6363455` | **S1: contracts and scoring, frozen before any label exists** |
| `1fabd33` | S0: foundation, constitution, masterplan, toolchain |

## What the log tells you

**`6363455` is the discipline commit.** The scoring function and the label schema were committed
in S1, before the teacher existed and before a single label had been produced. Everything the
project claims about not choosing a favourable metric rests on that commit's timestamp.

**`7ebc49d` is out of order on purpose.** An S5 risk was pre-verified during the S3 download
wait: rather than sit idle for a 22 GB pull, the session confirmed that `mlx-lm` registers
`qwen3_5` and handles the multimodal `text_config` nesting. The commit is labelled with the
sprint it belongs to, not the position it sits in.

**`5078744` reclaimed 21 GB.** That is the S4 teacher deletion, planned from the start because of
the 34 GB disk budget. It is a **different event** from the 2026-08-16 storage migration that
removed the merged student weights. See [[(Note) The Deleted Student Weights]].

**`86b43ee` is the only irreversible owner gate that was executed.** Two fixes were required
first: `LICENSE` had third-party notices appended to the MIT text, so GitHub classified the repo
as "Other" until they were split into `NOTICE.md`; and the README still said `METHODOLOGY.md`
did not exist while it sat committed beside it. The pre-publication scan found no `.env`, no
`.mcp.json`, no credentials in history, and the Aethereum join code correctly absent.

⚠️ **Note that `CLAUDE.md` and the README both still say no remote exists.** The commit history
disproves it. See [[(Report) Gaps & Questions]].

**Zero tags.** There is no release artefact to tag: nothing is published to a registry and the
Hugging Face push is deferred.

**`runs/current/hyperparams.json` records the training commit as `39333c7` with
`"dirty": true`**, so the trained adapter came from a working tree that was ahead of any commit.
That is recorded rather than hidden, which is the right call, but it means the exact training
tree cannot be recovered from git alone.

## Related

[[(Note) Honest State]] · [[(Note) Locked Decisions and Amendments]] ·
[[(Note) Roadmap and Owner Gates]] · [[(Index) 00 Overview]]
