---
id: 1933f65b-486a-47e7-b992-16fe7dfb0575
title: "00 Overview"
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

# 00 Overview

**What was distilled from what, what it measured, and what state the repo is in.** Start here.

## Notes

| Note | What it answers |
|---|---|
| [[(Note) What Distillation Is]] | The task, the three arms, and why the incumbent is one of them |
| [[(Note) Honest State]] | 🟡 What is finished, what is missing from disk, what is unbacked up |
| [[(Note) Git History]] | **19 commits** over **two days**. One sprint per commit |

## Also read immediately

⚠️ [[(Note) The Deleted Student Weights]] before running anything that loads a model.

## The thirty-second version

A live iOS news product sorts every headline into one of eight topics using a **keyword regex**.
This repo rebuilt that classifier's corpus from the same **63 public RSS feeds**, labelled
**3,706** headlines with a **35B open-weight teacher** running locally, LoRA fine-tuned a **4B**
open model on those labels, and measured all three arms on the same **500** headlines held out
before a single label existed.

The student reaches **0.840 macro-F1** against the incumbent's **0.337**, at **41.3x** lower
list cost and **2.4x** lower latency than the teacher.

## Key numbers, all verified 2026-08-17

| | |
|---|---|
| Commits | **19**, 2026-08-14 to 2026-08-15 · **0** tags |
| Tracked files | **85** · **124** on disk outside exclusions |
| Repo on disk | **484 MB** (`.venv` **380 MB**, `runs/` **49 MB**, `.git` **4.3 MB**) |
| Was on disk before 2026-08-16 | **8.3 GB** |
| Source | **4,363** lines across **25** modules |
| Tests | **90** functions in **9** files, **139** after parametrisation |
| Corpus | **3,706** labelled headlines · **54** outlets · **63** feeds plus **83** section feeds |
| Split | **3,206** train pool · **500** held out, frozen on first run |
| Student | macro-F1 **0.8400** · accuracy **0.8540** · p50 **322 ms** · **0** unparseable |
| Incumbent regex | macro-F1 **0.3372** · accuracy **0.3420** · `consumer` F1 **0.000** |
| Teacher | p50 **782 ms** · quality **n/a by construction** · hand-audit ceiling **84%** |
| Working tree | clean · **0** unpushed |

## Up

[[(Map) Master Map]] · [[(System) Flint Init]] · [[(Report) Project Summary]]
