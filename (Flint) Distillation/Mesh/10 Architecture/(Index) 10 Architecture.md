---
id: 39aa81c7-e4b7-46f5-86ab-ca2073bb912a
title: "10 Architecture"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/src"
---

# 10 Architecture

**The architecture is the pipeline: one module per stage, feeds to corpus to split to labels to
training to evaluation.** There is no service, no server and no database.

## Notes

| Note | What it answers |
|---|---|
| [[(Note) System Architecture]] | The whole pipeline, with the diagram, and the two decisions that do most of the work |
| [[(Note) The Training Pipeline]] | The LoRA run: config, what it cost, and why iteration 800 shipped instead of 1200 |
| [[(Note) Evaluation and Scoring]] | One harness, three arms, and why macro-F1 is computed the hard way |

## Up

[[(Map) Master Map]] · [[(Report) Project Summary]]
