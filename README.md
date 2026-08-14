# distillation

**Can a 4B open model replace a keyword regex — and get close to a 35B teacher — on a
classification task running in production today?**

Sentinel, a live iOS news-intelligence product, sorts every ingested headline into one of
eight topic classes. In production that classifier is a keyword regex. This repo rebuilds
its corpus from the same 61 public RSS feeds, labels ~5,000 headlines with a large
open-weight teacher, LoRA fine-tunes a ~4B open model on those labels, and reports quality,
cost and latency for all three arms on 500 headlines held out before a single label existed.

## Results

> **Pending — S0 of 9 complete.** No numbers are published until they are regenerable from
> committed artifacts. See `masterplan.md` for the current sprint.

| Arm | Macro-F1 | Accuracy | p50 | p95 | Cost / 1k |
|---|---|---|---|---|---|
| regex (incumbent) | — | — | — | — | — |
| teacher · Qwen3.5-35B-A3B | — | — | — | — | — |
| student · ~4B LoRA | — | — | — | — | — |

## Run it

```bash
uv sync                      # Python 3.12 + MLX
uv run python -m src.harvest # rebuild the corpus from public RSS
```

## Design notes

- **Open-weight teacher throughout.** Training on a closed frontier model's output and then
  publishing the weights would breach its terms; an open teacher makes the deliverable clean
  and costs nothing in the cost story.
- **Three arms, not two.** The regex is the real incumbent. Comparing only against the
  teacher would be choosing the flattering baseline.
- **Zero credentials, zero user data.** The corpus comes from public feeds, not from the
  product's database.

Full rules in `CLAUDE.md`; sequencing and acceptance gates in `masterplan.md`.

## Limitations

Written up honestly and in full at S8, alongside the results. The known ones already:
teacher-label noise sets the ceiling, this is one narrow task, the held-out set is 500
examples, classification is headline-only and English-only, and the cost figures are
list-price arithmetic rather than measured spend.
