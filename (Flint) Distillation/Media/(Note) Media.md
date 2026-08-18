---
id: dbd3a1eb-e993-4740-8b9f-4ad965c30a9b
title: "Media"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/charts"
---

# Media

**This folder is empty, and should stay that way.** The project's five images live in the repo
where they are regenerable from committed artefacts. Copying them here would create a second copy
that drifts.

| Asset | Path | Bytes |
|---|---|---|
| The hero | `/Users/brunojaamaa/Desktop/distillation/charts/label_distribution.png` | 120,646 |
| Training curve | `.../charts/training_curve.png` | 112,937 |
| Class distribution | `.../charts/class_distribution.png` | 101,428 |
| Student confusion matrix | `.../charts/confusion_student.png` | 78,280 |
| Regex confusion matrix | `.../charts/confusion_regex.png` | 76,782 |

## Why the charts are unusual

All five are **generated from committed artefacts**, so they regenerate today **with no model on
disk**. The renderer is `src/charts.py`, which vendors Geist and Geist Mono from
`assets/fonts/` under SIL OFL-1.1.

The design system reserves **`#FF9500`** for collision alerts. `src/charts.py` names the token so
the constraint is documented, and two separate guards make sure naming it is all that ever
happens: **CI greps `src/`**, and `tests/test_charts_guard.py` reads the **committed PNGs pixel
by pixel**. That is why `pillow` is a declared dev dependency rather than an assumed one.

## If media is added later

Put screenshots and diagrams here, not in `Mesh/`. Never copy anything large; link by absolute
path in `source_path:` instead.

## Related

[[(Note) Charts and Artefacts]] · [[(Note) Exports]] · [[(Index) Sources]] · [[(Map) Master Map]]
