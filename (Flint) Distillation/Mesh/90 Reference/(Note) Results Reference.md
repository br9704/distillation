---
id: 7276bb96-4c17-4c78-a69c-1c6d7ed89bf1
title: "Results Reference"
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
source_path: "/Users/brunojaamaa/Desktop/distillation/results/summary.json"
---

# Results Reference

**Every number below comes from `results/summary.json`, evaluated 2026-08-15T11:18:27Z on 500
held-out headlines.** ⚠️ **This is a map, not the source.** The file carries a provenance block
with the adapter SHA-256 and the held-out file hashes; read it before acting on a figure.

## Headline

| Arm | macro-F1 | accuracy | p50 ms | p95 ms | invalid | cost / 1k req |
|---|---|---|---|---|---|---|
| regex | **0.3372** | 0.3420 | 0.0 | 0.0 | 0 | **$0.0000** |
| **student** | **0.8400** | **0.8540** | **322.1** | 403.0 | **0** | **$0.0037** |
| teacher | **n/a by construction** | n/a | 781.8 | 867.7 | 0 | **$0.1547** |

The student is **41.3x cheaper** and **2.4x faster** than the teacher, and reproduces its
judgement on **85.4%** of held-out headlines.

## Per class, the incumbent regex

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| geopolitics | 0.826 | 0.196 | 0.317 | 97 |
| finance | 0.895 | 0.333 | 0.486 | 51 |
| tech | 0.762 | 0.533 | 0.628 | 60 |
| sports | 0.929 | 0.250 | 0.394 | 52 |
| entertainment | **1.000** | 0.129 | 0.229 | 62 |
| science | 0.895 | 0.218 | 0.351 | 78 |
| **consumer** | **0.000** | **0.000** | **0.000** | 34 |
| general | **0.173** | **0.985** | 0.295 | 66 |

**The shape is the finding.** Precision is high wherever the regex fires, recall is terrible
everywhere, `consumer` never fires at all because `amazon` is caught by the `tech` branch above
it, and `general` gets 0.985 recall only because the regex answers `general` three times in four
at **0.173 precision**.

## Where the student wins and where it loses

| | |
|---|---|
| Classes won on F1 | **8 of 8** |
| Classes lost on recall | **1**: `general`, 0.682 against 0.985 |
| Student right where the regex is wrong | **285** |
| Regex right where the student is wrong | **29** |
| Regex-`general` held-out rows the teacher reassigns | **310 of 375**, **82.7%** |
| Student errors involving `general` | **53.4%** of 73 |
| Student's worst class | **`consumer`**, recall **0.529** |
| Student's second worst | **`general`**, F1 0.698 |

**Per the repo's own rule, the one loss leads the write-up rather than getting buried.**

## The checkpoint comparison, both published

| Checkpoint | macro-F1 | Where |
|---|---|---|
| **iteration 800**, shipped | **0.8400** | `results/summary.json` |
| iteration 1200, mlx-lm's default | **0.7599** | `results/summary_final_checkpoint.json` |

**+8.0 macro-F1 points** for choosing the best-validation checkpoint over the final weights,
chosen on the 160-example validation split alone.

## Cost arithmetic

```
regex     $0.0000 / 1k requests   a pure function, no model, no tokens, no request
teacher   $0.1547 / 1k requests   (302.98 in +  6.51 out) x 1000 = 309,490 tokens x $0.50/1M
student   $0.0037 / 1k requests   ( 35.98 in +  1.51 out) x 1000 =  37,490 tokens x $0.10/1M

41.3x = 5.0x price tier x 8.26x fewer tokens
```

| Sensitivity | Result |
|---|---|
| Student billed one parameter tier up (it is 4.21B, just over the sub-4B boundary) | **8.3x**, the pessimistic read |
| Had the student kept the teacher's full prompt | **5.1x**, which is what amendment A3 bought |

⚠️ **List-price arithmetic, not measured spend.** Every arm ran locally at **$0**. Rates are
published serverless tiers retrieved 2026-08-15. Latency, by contrast, **is** measured.

## Corpus receipts

| | |
|---|---|
| Harvested / labelled | 3,812 / **3,706** |
| Outlets | **54** |
| Unparseable rate | **0.00%** |
| Regex sends to `general` | **74.18%** of the labelled corpus |
| Teacher hand-audit ceiling | **84%** strict, **93%** excluding ambiguous |
| Teacher self-agreement at temperature 0 | **100 of 100** |
| Across the `num_ctx` change | **60 of 60** identical |
| Independent re-prediction of the held-out set | **500 of 500** |

## The caveats that travel with every number

1. **Gold is the teacher.** The student's 85.4% is **agreement, not correctness**. The teacher's
   own ceiling is 84%. The two numbers must never be read as the student beating the teacher.
2. **One run, one seed, one machine, one 500-example draw.** No variance estimate. **Treat the
   third decimal as noise.**
3. **The teacher's tokens were counted with the student's tokeniser**, because the teacher's
   22 GB of weights were deleted in S4 to reclaim disk. Same Qwen family, not the same file.
   Recorded in `results/token_counts.json` rather than left implicit.
4. **`consumer` has 34 held-out examples.** That is thin, and it is the class both the student
   and the regex struggle with most.
5. **Headline-only, English-only, August 2026.**

## Related

[[(Note) Evaluation and Scoring]] · [[(Note) Charts and Artefacts]] ·
[[(Note) Teacher and Student Models]] · [[(Note) Honest State]] · [[(Index) 90 Reference]]
