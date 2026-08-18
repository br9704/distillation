---
id: b5c2d3b1-83a4-45d7-a044-af3b2eb40041
title: "Roadmap and Owner Gates"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/masterplan.md"
---

# Roadmap and Owner Gates

**The engineering is finished. What remains is two unanswered questions for Bruno and one
recommendation the repo makes about itself.**

The plan's design goal was that **S0 to S8 complete without a single owner gate interrupting
them**, and it held: everything requiring money, publication or an irreversible external action
was batched into S9 at the tail.

## The sprints

| Sprint | What it delivered | State |
|---|---|---|
| **S0** | Foundation: constitution, masterplan, toolchain | ✅ |
| **S1** | **Contracts and scoring, frozen before a single label exists** | ✅ |
| **S2** | Corpus rebuilt from public RSS, 3,706 headlines, zero credentials | ✅ |
| **S3** | Teacher live, prompt frozen at v1, pilot clean | ✅ |
| **S4** | **3,706 labels at 0.00% unparseable**, hand-audit ceiling measured, **21 GB reclaimed** | ✅ |
| **S5** | Base-model architecture probe. **A real gate, not a formality**, and it caught the `enable_thinking` silent failure | ✅ |
| **S6** | Train, select the checkpoint, merge | ✅ |
| **S7** | Evaluate all three arms | ✅ |
| **S8** | `METHODOLOGY.md` and the write-up | ✅ |
| **S9** | **All owner gates** | 🟡 **2 of 4 answered** |
| **Sprint D** | Documentation pass. Found the live defect in the cost model | ✅ |

## S9, the four gates

| Gate | Answer |
|---|---|
| **Make the GitHub repo public** | ✅ **Approved and executed, 2026-08-15.** `github.com/br9704/distillation`, CI green on `macos-14`. Two fixes were required first: `LICENSE` had third-party notices appended to the MIT text, so GitHub classified the repo as "Other" until they were split into `NOTICE.md`; and the README still said `METHODOLOGY.md` did not exist while it sat committed beside it. The pre-publication scan found no `.env`, no `.mcp.json`, no credentials in history, and the Aethereum join code correctly absent |
| **Push weights to Hugging Face** | ⏭ **Deferred by Bruno, 2026-08-15.** "We defer it", not declined, so it stays available. The masterplan **recommends against publishing the merged weights regardless**, calling 7.9 GB "a maintenance liability, not a contribution" when the alternative is one `mlx_lm fuse` command. It recommends **an adapter repo of a few MB** with `base_model:` metadata instead. ⚠️ That recommendation reads differently now: the adapter is the only irreplaceable artefact and it has no backup |
| **Publish the labelled dataset, or keep it local** | ❓ **Still open.** Explicitly **not** to be inferred from the Hugging Face deferral. Recommendation on file: keep it local, because `data/` being gitignored keeps the repo reviewable and the labels are "regenerable". ⚠️ **That last premise is false**, see [[(Note) The Corpus and Splits]] |
| **Optional paid ablation on a larger hosted teacher** | ❓ **Still open.** Would produce a **teacher-strength curve** for roughly $5 to $15 on a hosted `Qwen3.5-122B-A10B` or `397B-A17B`. Requires an account and API key the agent does not hold, so it cannot proceed by inference |

**Acceptance for S9 is that every gate is explicitly answered, approved or declined, and the
answer recorded. A declined gate is a completed task, not a failure.** Two remain genuinely
unanswered and are **not** being closed by assumption.

## What the repo itself recommends next

> A second training seed is the better spend of the same effort. It costs nothing but local GPU
> time and closes the single-sample limitation, which is the one gap a reviewer can legitimately
> attack.

That is the masterplan's own words, written against the paid-ablation gate. It is still the
right call, and it is now cheaper than it looks: `data/mlx/` is intact, so a second seed needs
the **~8.5 GB base re-download** and **~64 minutes**, and nothing else.

## Tasks

- [ ] Back up `runs/current/best/adapters.safetensors` (3.67 MB) and all of `data/` (5.1 MB). Neither is in git and neither can be regenerated #task [project:: Distillation] [priority:: high]
- [ ] Correct `CLAUDE.md` and the README's Status section, both of which still say nothing is published and no remote exists #task [project:: Distillation] [priority:: high]
- [ ] Answer the dataset-publication gate. It is a genuine choice: the corpus carries zero credentials and zero user data #task [project:: Distillation]
- [ ] Answer the paid-ablation gate, or decline it in favour of the second seed #task [project:: Distillation]
- [ ] Run the second training seed and publish the variance #task [project:: Distillation]
- [ ] Fix the `.gitignore` comment claiming `data/` is regenerable. The repo's own measurements say it is not #task [project:: Distillation]
- [ ] Take the six regex defects and the missing `politics` class back to Sentinel as product work. **The taxonomy is missing a ninth class**, and that is a real, actionable finding rather than a benchmark artefact #task [project:: Distillation] [priority:: high]
- [ ] Verify the case-study page at `brunojaamaa.dev/projects/distillation`, which this audit did not fetch #task [project:: Distillation]

## Backlog, explicitly out of scope for this project

Article bodies. Non-English. Parity tuning. A production deployment. Those were fixed as
non-goals before any number existed and are not roadmap items.

## Related

[[(Note) Honest State]] · [[(Note) The Deleted Student Weights]] ·
[[(Note) Locked Decisions and Amendments]] · [[(Report) Gaps & Questions]] ·
[[(Index) 60 Roadmap, Tasks & Ideas]]
