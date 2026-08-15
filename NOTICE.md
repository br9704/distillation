# Third-party notices

This project is MIT licensed, see [`LICENSE`](./LICENSE). These notices were previously
appended to that file, which prevented GitHub from recognising it as MIT; they live here
instead so the licence text stays pristine and machine-detectable.

## Vendored assets

- **Geist** and **Geist Mono** (`assets/fonts/Geist-*.ttf`, `assets/fonts/GeistMono-*.ttf`),
  SIL Open Font License 1.1. Full text in [`assets/fonts/LICENSE.txt`](./assets/fonts/LICENSE.txt).
  Vendored so charts render identically without a system font install.

## Models

**No model weights are committed to this repository.** Models are referenced by repo id and
pinned revision, and are distributed under their own licences:

| model | role | licence |
|---|---|---|
| `Qwen/Qwen3.5-35B-A3B` (via `unsloth/Qwen3.5-35B-A3B-GGUF`, Q4_K_M) | teacher (produced every label) | Apache-2.0 |
| `Qwen/Qwen3.5-4B` (via `mlx-community/Qwen3.5-4B-bf16` @ `491fdc7c087ba7fb48adcb1253f8e76d011db783`) | student (base model) | Apache-2.0 |

An **open-weight teacher was a hard requirement, not a preference.** Training on a closed
model's output and then publishing the result would breach that provider's terms, and
publishable weights are the point of the exercise. Both licences permit it.

## Data

The corpus is rebuilt from **public RSS feeds**, with zero credentials and zero user data. The
production database was deliberately never read. Headlines remain the property of their
publishers and are used here for research and evaluation. The harvested corpus is not committed
(`data/` is gitignored); `src/harvest.py` regenerates it.

Individual headlines and outlet names do appear inside committed result artifacts
(`results/error_analysis.json`, `results/audit_50_sample.json`) as evidence for specific
classification claims, since a claim about a misclassified headline is unverifiable without the
headline.
