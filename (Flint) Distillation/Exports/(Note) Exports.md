---
id: de49316f-9af1-4c53-b813-601371546ec4
title: "Exports"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/(Flint) Distillation/Exports"
---

# Exports

**Empty, on purpose.** `Exports/` is for anything generated out of this vault for an audience
outside it.

## What would belong here

| Candidate | Why |
|---|---|
| A **Sentinel defect report** | The six regex defects and the missing `politics` class are actionable product findings about a live classifier. They belong in Sentinel's own record, not only in a benchmark repo. See [[(Guide) BRUNO HQ]] |
| A **Hugging Face model card draft** | If the deferred adapter gate is ever reopened, the required YAML is already specified in `masterplan.md` S9: `license`, `base_model`, `pipeline_tag`, `tags`, `datasets`, `library_name`, plus an explicit disclosure of the labelling source, teacher model, revision and prompt version |
| A **digest for the hub** | The hub has **no** project note for distillation. [[(Report) Project Summary]] is the source for it |
| A **case-study draft** | `PROJECT.json` already carries the metrics, the honest block and the decisions. It is close to a case study already |

## What does not belong here

Anything already in the repo. `results/`, `charts/` and `runs/current/` are the evidence layer
and would drift the moment they were copied.

**And do not export the corpus or the adapter as an "export".** They need a **backup**, which is a
different thing: an export is a derived artefact, a backup is a second copy of an original. See
[[(Note) The Deleted Student Weights]].

## How to export

```bash
flint export --help
```

Then log it with `--op export`. See [[(Guide) BRUNO HQ]].

## Related

[[(Note) Media]] · [[(Index) Sources]] · [[(Guide) BRUNO HQ]] · [[(Map) Master Map]]
