"""The run recorder parses the only surviving evidence of a training run, so it is tested
against real mlx-lm output rather than against a shape invented here.

The fixture below is copied verbatim from `runs/current/train.log` — tqdm carriage-return
noise included, because that noise is exactly what broke the naive `^Iter` anchor.
"""

from __future__ import annotations

from src.record_run import parse_log

# Verbatim mlx-lm 0.31.3 output. The `Calculating loss...` bar shares a physical line with the
# val report, which is why the parser must not anchor to the start of a line.
REAL_LOG = (
    "Loading configuration file configs/lora.yaml\n"
    "Loading pretrained model\n"
    "Trainable parameters: 0.022% (0.918M/4205.750M)\n"
    "Starting training..., iters: 1200\n"
    "Calculating loss...:  50%|#####     | 10/20 [00:07<00:06,  1.46it/s]"
    "Calculating loss...: 100%|##########| 20/20 [00:14<00:00,  1.39it/s]"
    "Iter 1: Val loss 5.604, Val took 14.384s\n"
    "Iter 1: Train loss 5.334, Learning Rate 1.000e-05, It/sec 0.035, Tokens/sec 1.859, "
    "Trained Tokens 53, Peak mem 31.753 GB\n"
    "Iter 2: Train loss 5.623, Learning Rate 1.000e-05, It/sec 0.202, Tokens/sec 10.314, "
    "Trained Tokens 104, Peak mem 31.753 GB\n"
    "Iter 100: Train loss nan, Learning Rate 1.000e-05, It/sec 0.062, Tokens/sec 2.216, "
    "Trained Tokens 5143, Peak mem 43.907 GB\n"
    "Iter 100: Val loss 0.095, Val took 13.776s\n"
    "Iter 101: Train loss 0.090, Learning Rate 1.000e-05, It/sec 0.303, Tokens/sec 15.152, "
    "Trained Tokens 5193, Peak mem 43.907 GB\n"
)


def test_parses_reports_that_share_a_line_with_a_progress_bar() -> None:
    records, _ = parse_log(REAL_LOG)
    val = [r for r in records if r["split"] == "valid"]
    assert [r["iter"] for r in val] == [1, 100]
    assert val[0]["loss"] == 5.604


def test_nan_is_preserved_as_an_explicit_gap_not_dropped() -> None:
    """A silently discarded nan window is the difference between a loss curve and a lie."""
    records, facts = parse_log(REAL_LOG)
    nan_records = [r for r in records if r["split"] == "train" and r["loss"] is None]
    assert len(nan_records) == 1
    assert nan_records[0]["iter"] == 100
    assert facts["nan_report_windows"] == 1
    assert facts["nan_at_iters"] == [100]
    # The row still exists — the step is not missing from the series, only its value.
    assert nan_records[0]["trained_tokens"] == 5143


def test_extracts_the_full_metric_row() -> None:
    records, _ = parse_log(REAL_LOG)
    first = next(r for r in records if r["split"] == "train" and r["iter"] == 1)
    assert first["loss"] == 5.334
    assert first["learning_rate"] == 1e-05
    assert first["it_per_sec"] == 0.035
    assert first["tokens_per_sec"] == 1.859
    assert first["trained_tokens"] == 53
    assert first["peak_mem_gb"] == 31.753


def test_run_facts_summarise_the_run() -> None:
    _, facts = parse_log(REAL_LOG)
    assert facts["reported_steps"] == 4
    assert facts["val_evaluations"] == 2
    assert facts["last_iter"] == 101
    assert facts["trainable_parameters"] == {
        "percent": 0.022,
        "trainable_millions": 0.918,
        "total_millions": 4205.750,
    }
    assert facts["peak_mem_gb"] == 43.907
    assert facts["first_train_loss"] == 5.334
    assert facts["final_train_loss"] == 0.090
    assert facts["loss_decreased"] is True


def test_an_unfinished_run_is_reported_as_unfinished() -> None:
    """The panic-killed run had no 'Saved final weights' line. That must be visible in the
    artifact, not inferred from the absence of something."""
    _, facts = parse_log(REAL_LOG)
    assert facts["completed"] is False
    assert facts["final_weights"] is None

    _, done = parse_log(REAL_LOG + "Saved final weights to runs/current/adapters/adapters.safetensors\n")
    assert done["completed"] is True
    assert done["final_weights"].endswith("adapters.safetensors")


def test_empty_log_yields_nothing_rather_than_a_fake_zero() -> None:
    records, facts = parse_log("Loading pretrained model\nno reports here\n")
    assert records == []
    assert facts["reported_steps"] == 0
    assert facts["last_iter"] == 0
