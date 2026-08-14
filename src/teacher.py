"""Arm 2: the teacher. Labels headlines with a large open-weight model, running locally.

`Qwen/Qwen3.5-35B-A3B` at Q4_K_M via Ollama — Apache-2.0, so nothing here constrains what
can be published later. It is a mixture-of-experts with roughly 3B active parameters, which
is why a 35B-class teacher is practical on an M4 Pro at all.

Three decisions worth knowing about before reading the code:

**Constrained decoding.** The request carries a JSON schema whose `topic` field is an enum
over the eight classes, so the sampler cannot emit anything else. The alternative — asking
for one word and parsing — spends label quality on a problem that is avoidable. `UNPARSEABLE`
still exists and is still reported, because a request can fail for reasons other than the
sampler (timeouts, a truncated response, a malformed envelope), and those must surface
rather than quietly become `general`.

**Never coerce to `general`.** A failed label is `UNPARSEABLE` and gets filtered downstream.
Coercing it would bias the teacher toward the majority class — and the majority class is
already 74% of what the incumbent produces, so this is exactly the direction the data would
be poisoned in.

**Resumable.** Labels are appended per batch and keyed by id, so a crash costs one batch
rather than the run. Re-running skips what is already labelled.

    uv run python -m src.teacher --input data/heldout.jsonl --output data/heldout_labels.jsonl
    uv run python -m src.teacher --input data/train_pool.jsonl --output data/train_labels.jsonl
    uv run python -m src.teacher --latency --input data/heldout.jsonl   # sequential timing run
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

from src.schema import CLASS_DEFINITIONS, TOPIC_CLASSES, UNPARSEABLE
from src.store import DATA, append_jsonl, read_jsonl

OLLAMA = "http://127.0.0.1:11434"
TEACHER_MODEL = "hf.co/unsloth/Qwen3.5-35B-A3B-GGUF:Q4_K_M"
TEACHER_REVISION = "Q4_K_M"  # the quant IS the revision for a GGUF pull

# Bump this string on ANY change to the prompt below. It is written into every Label row,
# so a mixed-prompt dataset is detectable after the fact instead of silently averaged.
PROMPT_VERSION = "v1"

CHECKPOINT_EVERY = 50

_CLASS_LINES = "\n".join(f"- {name}: {desc}" for name, desc in CLASS_DEFINITIONS.items())

SYSTEM_PROMPT = f"""You are a news desk editor routing incoming wire headlines into exactly one topic channel.

The channels:
{_CLASS_LINES}

Rules:
- Choose the channel matching what the story is ABOUT, not merely words it contains. A story about a shopping festival in China is consumer, not geopolitics. A story about an athlete's contract is sports, not finance.
- If a story genuinely spans two channels, choose the one a reader would most expect to find it under.
- Use `general` only when no other channel fits — not as a default.

Answer with the channel name only."""

# The retry prompt is deliberately blunter. It is used only when the first attempt fails,
# which under constrained decoding means the transport or the envelope broke rather than
# the sampler wandering off.
RETRY_SUFFIX = "\n\nRespond with exactly one of: " + ", ".join(TOPIC_CLASSES)

TOPIC_SCHEMA = {
    "type": "object",
    "properties": {"topic": {"type": "string", "enum": list(TOPIC_CLASSES)}},
    "required": ["topic"],
}


def build_user_prompt(headline: str, outlet: str) -> str:
    return f"Outlet: {outlet}\nHeadline: {headline}"


def _parse(content: str) -> str | None:
    """Pull a valid class out of the response, or None. Never guesses."""
    content = content.strip()
    # Reasoning models may wrap output; take the last JSON object if there is one.
    if "{" in content:
        candidate = content[content.rfind("{") : content.rfind("}") + 1]
        try:
            topic = json.loads(candidate).get("topic", "")
            if topic in TOPIC_CLASSES:
                return topic
        except (json.JSONDecodeError, AttributeError):
            pass
    bare = content.lower().strip().strip(".\"'` \n")
    return bare if bare in TOPIC_CLASSES else None


def label_one(client: httpx.Client, headline: str, outlet: str, model: str) -> tuple[str, float, str]:
    """Return (label, latency_ms, raw_output). Latency is wall-clock around the request."""
    raw = ""
    for attempt in (1, 2):
        system = SYSTEM_PROMPT if attempt == 1 else SYSTEM_PROMPT + RETRY_SUFFIX
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": build_user_prompt(headline, outlet)},
            ],
            "stream": False,
            "think": False,
            "format": TOPIC_SCHEMA,
            "options": {"temperature": 0, "num_predict": 24, "seed": 20260814},
        }
        started = time.perf_counter()
        try:
            response = client.post(f"{OLLAMA}/api/chat", json=payload, timeout=180.0)
            elapsed = (time.perf_counter() - started) * 1000
            response.raise_for_status()
            raw = response.json().get("message", {}).get("content", "")
        except Exception as exc:  # noqa: BLE001
            elapsed = (time.perf_counter() - started) * 1000
            raw = f"<error> {type(exc).__name__}: {exc}"
            continue
        parsed = _parse(raw)
        if parsed:
            return parsed, elapsed, raw
    return UNPARSEABLE, elapsed, raw


def run(input_path: Path, output_path: Path, model: str, limit: int = 0) -> int:
    rows = list(read_jsonl(input_path))
    done = {row["id"] for row in read_jsonl(output_path)}
    todo = [row for row in rows if row["id"] not in done]
    if limit:
        todo = todo[:limit]

    if not todo:
        print(f"[teacher] nothing to do — {len(done)} already labelled in {output_path.name}")
        return 0

    print(f"[teacher] {len(todo)} to label ({len(done)} already done) · model {model} · prompt {PROMPT_VERSION}")
    buffer: list[dict] = []
    counts: dict[str, int] = {}
    started = time.time()

    with httpx.Client() as client:
        for index, row in enumerate(todo, start=1):
            label, latency_ms, raw = label_one(client, row["headline"], row["outlet"], model)
            counts[label] = counts.get(label, 0) + 1
            buffer.append(
                {
                    "id": row["id"],
                    "label": label,
                    "teacher_model": model,
                    "teacher_revision": TEACHER_REVISION,
                    "prompt_version": PROMPT_VERSION,
                    "latency_ms": round(latency_ms, 2),
                    "raw_output": raw[:400],
                }
            )
            if len(buffer) >= CHECKPOINT_EVERY:
                append_jsonl(output_path, buffer)
                buffer.clear()
                rate = index / (time.time() - started)
                remaining = (len(todo) - index) / rate if rate else 0
                print(
                    f"[teacher] {index}/{len(todo)}  {rate:.2f}/s  eta {remaining / 60:.0f}m  "
                    + " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
                )

    if buffer:
        append_jsonl(output_path, buffer)

    total = time.time() - started
    bad = counts.get(UNPARSEABLE, 0)
    print(f"[teacher] done — {len(todo)} labelled in {total / 60:.1f}m")
    print(f"[teacher] unparseable: {bad} ({bad / len(todo):.2%})")
    print("[teacher] distribution: " + " · ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


def latency_run(input_path: Path, model: str, n: int, output_path: Path) -> int:
    """A dedicated sequential timing run — the honest measurement.

    One request at a time, no concurrency, no batching, timed around each call. This exists
    because batched labelling throughput is not latency and must never be reported as it.
    Run this BEFORE the teacher weights are deleted; they are 22 GB and the disk plan
    reclaims them in S4.
    """
    rows = list(read_jsonl(input_path))[:n]
    print(f"[latency] {len(rows)} sequential single requests against {model}")
    records = []
    with httpx.Client() as client:
        # Warm up first. Measured on this machine, a cold first call costs ~5,200ms against
        # ~500ms warm — pure weight-loading. Including that in p95 would report the cost of
        # starting a server, not the cost of serving a request, and both arms in this
        # comparison are served warm. The warm-up calls are discarded, and the fact that
        # they happened is stated in METHODOLOGY rather than buried here.
        print("[latency] warming up (3 discarded calls)")
        for warm in rows[:3]:
            label_one(client, warm["headline"], warm["outlet"], model)

        for index, row in enumerate(rows, start=1):
            label, latency_ms, _ = label_one(client, row["headline"], row["outlet"], model)
            records.append({"id": row["id"], "arm": "teacher", "pred": label, "latency_ms": round(latency_ms, 2)})
            if index % 50 == 0:
                print(f"[latency] {index}/{len(rows)}")

    from src.scoring import percentile

    values = [r["latency_ms"] for r in records]
    from src.store import write_jsonl

    write_jsonl(output_path, records)
    print(f"[latency] n={len(values)}  p50={percentile(values, 50):.0f}ms  p95={percentile(values, 95):.0f}ms")
    print(f"[latency] wrote {output_path}")
    return 0


def consistency_run(input_path: Path, model: str, n: int, samples: int) -> int:
    """How stable is the teacher with itself?

    This is a floor on the label noise the student inherits. If the teacher gives three
    different answers to the same headline, no amount of training makes the student right
    about it, and the ceiling reported in S7 has to say so.

    Two temperatures, because they measure different things:
      - temp 0 tests **determinism**. Anything below 100% means the labelling run is not
        reproducible, which would be a bug worth finding before 3,200 labels depend on it.
      - temp 0.7 tests **confidence**. Disagreement here marks headlines the model finds
        genuinely ambiguous, and those are the ones worth reading in the S4 hand audit.
    """
    rows = list(read_jsonl(input_path))[:n]
    print(f"[consistency] {len(rows)} headlines × {samples} samples at temp 0 and temp 0.7")
    results: dict[float, list[list[str]]] = {0.0: [], 0.7: []}

    with httpx.Client() as client:
        for temperature in (0.0, 0.7):
            for row in rows:
                answers = []
                for sample in range(samples):
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": build_user_prompt(row["headline"], row["outlet"])},
                        ],
                        "stream": False,
                        "think": False,
                        "format": TOPIC_SCHEMA,
                        # Seed varies per sample or temp>0 would still be deterministic.
                        "options": {"temperature": temperature, "num_predict": 24, "seed": 1000 + sample},
                    }
                    try:
                        response = client.post(f"{OLLAMA}/api/chat", json=payload, timeout=180.0)
                        answers.append(_parse(response.json().get("message", {}).get("content", "")) or UNPARSEABLE)
                    except Exception:  # noqa: BLE001
                        answers.append(UNPARSEABLE)
                results[temperature].append(answers)

    for temperature, all_answers in results.items():
        unanimous = sum(1 for answers in all_answers if len(set(answers)) == 1)
        print(f"[consistency] temp {temperature}: {unanimous}/{len(all_answers)} unanimous ({unanimous / len(all_answers):.1%})")
        disagreed = [(row, answers) for row, answers in zip(rows, all_answers, strict=True) if len(set(answers)) > 1]
        for row, answers in disagreed[:8]:
            print(f"    {'/'.join(sorted(set(answers))):<32} {row['headline'][:66]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Label headlines with the open-weight teacher.")
    parser.add_argument("--input", type=Path, default=DATA / "heldout.jsonl")
    parser.add_argument("--output", type=Path, default=DATA / "heldout_labels.jsonl")
    parser.add_argument("--model", default=TEACHER_MODEL)
    parser.add_argument("--limit", type=int, default=0, help="label at most this many (pilot runs)")
    parser.add_argument("--latency", action="store_true", help="sequential timing run instead of labelling")
    parser.add_argument("--consistency", action="store_true", help="self-agreement probe instead of labelling")
    parser.add_argument("--n", type=int, default=500, help="latency- or consistency-run sample size")
    parser.add_argument("--samples", type=int, default=3, help="samples per headline in the consistency run")
    args = parser.parse_args()

    if args.latency:
        return latency_run(args.input, args.model, args.n, DATA / "teacher_latency.jsonl")
    if args.consistency:
        return consistency_run(args.input, args.model, args.n, args.samples)
    return run(args.input, args.output, args.model, args.limit)


if __name__ == "__main__":
    sys.exit(main())
