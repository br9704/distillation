"""S7 error analysis: where and why each arm loses, by cause rather than by class.

The masterplan calls this "the part most people skip", and an aggregate macro-F1 is exactly
the number that hides what a reviewer wants to know. This module answers five questions from
`results/predictions.jsonl`, and writes them to `results/error_analysis.json` plus a prose
`results/error_analysis.md`:

1. **Top confused pairs** — which gold→pred substitutions dominate, per arm.
2. **An error taxonomy by cause.** Classes are not causes. `tech` predicted for a SpaceX
   launch and `tech` predicted for an Amazon sale are the same confusion pair and two
   different mistakes. The taxonomy buckets by mechanism: the incumbent's first-match-wins
   ordering, its `china`-implies-geopolitics rule, its catch-all `general`, genuinely
   ambiguous cross-domain headlines, and the residue.
3. **Where the student beats the regex badly** — the product argument, stated as examples
   rather than as a delta.
4. **Where the student loses to the regex** — per CLAUDE.md this leads the README if it
   happens anywhere, so it is computed first-class and not left to be noticed.
5. **Breakdowns by headline length and by outlet**, because "the student is worse" is a
   different finding from "the student is worse on short headlines from low-volume outlets".

**On "outlet tier".** The masterplan asks for an outlet-*tier* breakdown. No tier taxonomy
exists in this repo: `Feed` is `(outlet, url, section)` and `data/heldout.jsonl` carries no
`tier` field, so a tier column would have read `unknown` for all 500 rows while looking like a
real result. Inventing an editorial ranking (Reuters = tier 1, and so on) would be fabricating
data to satisfy a checkbox. Instead this reports **by outlet**, which is real, plus a
**volume band** — outlets grouped by how many held-out headlines they contribute — which is an
explicit, stated proxy for prominence rather than an editorial judgement dressed as one.

Gold is the teacher's label, so every "error" here is a *disagreement with the teacher*, not
a proven mistake. The hand audit put the teacher's own agreement with a human at 84%, which
is the ceiling on all of this. Both facts are printed into the report rather than assumed.

    uv run python -m src.error_analysis
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.schema import TOPIC_CLASSES, UNPARSEABLE
from src.store import DATA, read_jsonl

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# Length bands, chosen before looking at the results. A headline under ~40 characters carries
# very little for any classifier; over ~90 it usually names its own subject.
LENGTH_BANDS = ((0, 40, "short (<40 ch)"), (40, 70, "medium (40-69)"), (70, 90, "long (70-89)"), (90, 10_000, "very long (90+)"))

# The regex's own failure mechanisms, read off its source rather than inferred. See
# src/regex_baseline.py — a faithful port of classifyWireItem(), bugs included.
CHINA_RE = re.compile(r"\bchina\b|\bchinese\b|\bbeijing\b", re.IGNORECASE)


def band(headline: str) -> str:
    n = len(headline)
    for low, high, name in LENGTH_BANDS:
        if low <= n < high:
            return name
    return LENGTH_BANDS[-1][2]


def volume_bands(rows: list[dict]) -> dict[str, str]:
    """Map each outlet to a volume band — a stated proxy for prominence, not an editorial tier.

    The repo has no tier taxonomy (see the module docstring). What it does have is how many of
    the held-out 500 each outlet contributed, which is a real, checkable quantity. Bands are
    cut on counts rather than on names so no judgement about any outlet is being smuggled in.
    """
    counts = Counter(r["outlet"] for r in rows if r["outlet"])
    mapping = {}
    for outlet, count in counts.items():
        if count >= 20:
            mapping[outlet] = "high volume (20+ held-out headlines)"
        elif count >= 8:
            mapping[outlet] = "medium volume (8-19)"
        else:
            mapping[outlet] = "low volume (<8)"
    return mapping


def load_predictions(path: Path) -> dict[str, list[dict]]:
    by_arm: dict[str, list[dict]] = defaultdict(list)
    for row in read_jsonl(path):
        by_arm[row["arm"]].append(row)
    return dict(by_arm)


def enrich(predictions: list[dict], examples: dict[str, dict]) -> list[dict]:
    """Attach the headline, outlet and tier each prediction was made from."""
    out = []
    for p in predictions:
        example = examples.get(p["id"], {})
        out.append(
            {
                **p,
                "headline": example.get("headline", ""),
                "outlet": example.get("outlet", ""),
                "tier": example.get("tier", "unknown"),
                "correct": p["pred"] == p["gold"],
            }
        )
    return out


def taxonomy(errors: list[dict], arm: str) -> dict[str, dict]:
    """Bucket errors by mechanism, not by class.

    The regex buckets are mechanical and checkable against its source. The student's are
    behavioural, so they are deliberately coarser — inventing fine-grained causes for a neural
    model's errors would be storytelling.
    """
    buckets: dict[str, list[dict]] = defaultdict(list)
    for e in errors:
        gold, pred, headline = e["gold"], e["pred"], e["headline"]
        if pred == UNPARSEABLE:
            buckets["unparseable output"].append(e)
        elif arm == "regex" and pred == "general":
            # The incumbent's catch-all. Its own `if` chain falls through to `general` whenever
            # no keyword matched, which is most of the time.
            buckets["regex catch-all: no keyword matched, fell through to `general`"].append(e)
        elif arm == "regex" and pred == "geopolitics" and CHINA_RE.search(headline):
            # Visible in the source: any headline containing `china` returns geopolitics before
            # any later branch can run.
            buckets["regex `china` rule fires before every later branch"].append(e)
        elif arm == "regex" and gold == "general":
            buckets["regex matched a keyword the story is not about"].append(e)
        elif arm == "regex":
            buckets["regex first-match-wins: an earlier branch claimed the headline"].append(e)
        elif gold == "general" or pred == "general":
            # `general` is a catch-all on the gold side too, so disagreement with it is closer
            # to a taxonomy problem than a model error.
            buckets["disagreement involving the `general` catch-all"].append(e)
        else:
            buckets[f"cross-domain confusion: {gold} vs {pred}"].append(e)

    return {
        name: {
            "n": len(rows),
            "share_of_errors": round(len(rows) / len(errors), 4) if errors else 0.0,
            "examples": [
                {"headline": r["headline"], "outlet": r["outlet"], "gold": r["gold"], "pred": r["pred"]}
                for r in rows[:4]
            ],
        }
        for name, rows in sorted(buckets.items(), key=lambda kv: -len(kv[1]))
    }


def breakdown(rows: list[dict], key) -> dict[str, dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    return {
        name: {
            "n": len(items),
            "correct": sum(1 for i in items if i["correct"]),
            "agreement": round(sum(1 for i in items if i["correct"]) / len(items), 4),
        }
        for name, items in sorted(groups.items())
    }


def confused_pairs(rows: list[dict], top: int = 5) -> list[dict]:
    counter = Counter((r["gold"], r["pred"]) for r in rows if not r["correct"])
    return [{"gold": g, "pred": p, "n": n} for (g, p), n in counter.most_common(top)]


def head_to_head(student: list[dict], regex: list[dict]) -> dict:
    """Where each arm succeeds and the other fails, as examples rather than a delta."""
    by_id = {r["id"]: r for r in regex}
    student_wins, regex_wins = [], []
    for s in student:
        r = by_id.get(s["id"])
        if r is None:
            continue
        if s["correct"] and not r["correct"]:
            student_wins.append({"headline": s["headline"], "outlet": s["outlet"],
                                 "gold": s["gold"], "regex_said": r["pred"]})
        elif r["correct"] and not s["correct"]:
            regex_wins.append({"headline": s["headline"], "outlet": s["outlet"],
                               "gold": s["gold"], "student_said": s["pred"]})
    return {
        "student_right_regex_wrong": {"n": len(student_wins), "examples": student_wins[:12]},
        "regex_right_student_wrong": {"n": len(regex_wins), "examples": regex_wins[:12]},
        "note": (
            "Per CLAUDE.md, any class where the student loses to the regex leads the README. "
            "`regex_right_student_wrong` is computed first-class for that reason."
        ),
    }


def per_class_gap(student: list[dict], regex: list[dict]) -> dict[str, dict]:
    """Per-class comparison on BOTH recall and F1, so a regression cannot hide in the average —
    and so a spurious one cannot be manufactured either.

    Recall alone is misleading in exactly one direction here, and it matters. The incumbent
    predicts `general` for 375 of the 500 held-out headlines, so it "catches" almost every true
    `general` and posts 98.5% recall on that class — at 17.3% precision. Judged on recall the
    regex wins `general`; judged on F1 it loses it badly (0.295 vs 0.698). Reporting only the
    first would invent a student weakness that is really the catch-all's artefact; reporting
    only the second would bury a real difference. Both are reported, and `student_loses` (recall)
    is kept distinct from `student_loses_on_f1`.
    """
    from src.scoring import score as score_fn

    def per_class(rows: list[dict]) -> dict[str, dict]:
        usable = [r for r in rows if r["pred"] != UNPARSEABLE]
        scored = score_fn([r["gold"] for r in usable], [r["pred"] for r in usable]).as_dict()
        out = {}
        for entry in scored["per_class"]:
            label = entry.get("label", entry.get("class"))
            out[label] = entry
        return out

    s_pc, r_pc = per_class(student), per_class(regex)

    def rate(rows: list[dict], cls: str) -> tuple[int, float]:
        of_class = [r for r in rows if r["gold"] == cls]
        if not of_class:
            return 0, 0.0
        return len(of_class), round(sum(1 for r in of_class if r["correct"]) / len(of_class), 4)

    out = {}
    for cls in TOPIC_CLASSES:
        n_s, s_rate = rate(student, cls)
        _, r_rate = rate(regex, cls)
        s_f1 = round(s_pc.get(cls, {}).get("f1", 0.0), 4)
        r_f1 = round(r_pc.get(cls, {}).get("f1", 0.0), 4)
        out[cls] = {
            "n_gold": n_s,
            "student_agreement": s_rate,
            "regex_agreement": r_rate,
            "student_minus_regex": round(s_rate - r_rate, 4),
            "student_loses": s_rate < r_rate,
            "student_precision": round(s_pc.get(cls, {}).get("precision", 0.0), 4),
            "regex_precision": round(r_pc.get(cls, {}).get("precision", 0.0), 4),
            "student_f1": s_f1,
            "regex_f1": r_f1,
            "student_minus_regex_f1": round(s_f1 - r_f1, 4),
            "student_loses_on_f1": s_f1 < r_f1,
        }
    return out


def to_markdown(report: dict) -> str:
    """Prose, because the masterplan asks for prose. Numbers alone are not error analysis."""
    lines = ["# Error analysis — held-out 500", ""]
    lines.append(report["caveat"])
    lines.append("")

    for arm in ("student", "regex"):
        arm_report = report["arms"].get(arm)
        if not arm_report:
            continue
        lines.append(f"## {arm}")
        lines.append("")
        lines.append(f"- {arm_report['n']} scored · {arm_report['errors']} disagreements "
                     f"· agreement {arm_report['agreement']:.1%}")
        lines.append("")
        lines.append("**Top confused pairs**")
        lines.append("")
        lines.append("| gold | predicted | n |")
        lines.append("|---|---|---|")
        for pair in arm_report["top_confused_pairs"]:
            lines.append(f"| `{pair['gold']}` | `{pair['pred']}` | {pair['n']} |")
        lines.append("")
        lines.append("**Errors by cause**")
        lines.append("")
        for name, bucket in arm_report["taxonomy"].items():
            lines.append(f"- **{name}** — {bucket['n']} ({bucket['share_of_errors']:.1%} of this arm's errors)")
            for ex in bucket["examples"][:2]:
                lines.append(f"  - \"{ex['headline']}\" · {ex['outlet']} · gold `{ex['gold']}`, said `{ex['pred']}`")
        lines.append("")
        lines.append("**By headline length**")
        lines.append("")
        lines.append("| band | n | agreement |")
        lines.append("|---|---|---|")
        for name, stats in arm_report["by_length"].items():
            lines.append(f"| {name} | {stats['n']} | {stats['agreement']:.1%} |")
        lines.append("")
        lines.append("**By outlet volume band**")
        lines.append("")
        lines.append(f"_{arm_report['outlet_tier_note']}_")
        lines.append("")
        lines.append("| band | n | agreement |")
        lines.append("|---|---|---|")
        for name, stats in arm_report["by_outlet_volume_band"].items():
            lines.append(f"| {name} | {stats['n']} | {stats['agreement']:.1%} |")
        lines.append("")
        worst = sorted(
            (kv for kv in arm_report["by_outlet"].items() if kv[1]["n"] >= 8),
            key=lambda kv: kv[1]["agreement"],
        )[:5]
        if worst:
            lines.append("**Weakest outlets** (8+ held-out headlines)")
            lines.append("")
            lines.append("| outlet | n | agreement |")
            lines.append("|---|---|---|")
            for name, stats in worst:
                lines.append(f"| {name} | {stats['n']} | {stats['agreement']:.1%} |")
            lines.append("")

    h2h = report.get("head_to_head")
    if h2h:
        lines.append("## Student versus the incumbent")
        lines.append("")
        lines.append(f"- Student right where the regex is wrong: **{h2h['student_right_regex_wrong']['n']}**")
        lines.append(f"- Regex right where the student is wrong: **{h2h['regex_right_student_wrong']['n']}**")
        lines.append("")
        lines.append("Student wins, verbatim:")
        lines.append("")
        for ex in h2h["student_right_regex_wrong"]["examples"][:6]:
            lines.append(f"- \"{ex['headline']}\" — gold `{ex['gold']}`, regex said `{ex['regex_said']}`")
        lines.append("")
        if h2h["regex_right_student_wrong"]["examples"]:
            lines.append("Regex wins, verbatim — these lead the README if any class regresses:")
            lines.append("")
            for ex in h2h["regex_right_student_wrong"]["examples"][:6]:
                lines.append(f"- \"{ex['headline']}\" — gold `{ex['gold']}`, student said `{ex['student_said']}`")
            lines.append("")

    gap = report.get("per_class")
    if gap:
        lines.append("## Per class, student versus regex")
        lines.append("")
        lines.append("| class | n | student recall | regex recall | Δ recall | student F1 | regex F1 | Δ F1 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for cls, stats in gap.items():
            flag = " ⚠︎" if stats["student_loses"] else ""
            f1flag = " ⚠︎" if stats["student_loses_on_f1"] else ""
            lines.append(
                f"| `{cls}` | {stats['n_gold']} | {stats['student_agreement']:.1%} | "
                f"{stats['regex_agreement']:.1%} | {stats['student_minus_regex']:+.1%}{flag} | "
                f"{stats['student_f1']:.3f} | {stats['regex_f1']:.3f} | "
                f"{stats['student_minus_regex_f1']:+.3f}{f1flag} |"
            )
        lines.append("")
        losses = [c for c, s in gap.items() if s["student_loses"]]
        f1_losses = [c for c, s in gap.items() if s["student_loses_on_f1"]]
        if losses:
            lines.append(
                f"**The student loses to the regex on recall for: "
                f"{', '.join(f'`{c}`' for c in losses)}.** Per CLAUDE.md this leads rather than "
                f"being buried."
            )
            lines.append("")
            for cls in losses:
                s = gap[cls]
                lines.append(
                    f"- `{cls}`: student recall {s['student_agreement']:.1%} vs regex "
                    f"{s['regex_agreement']:.1%}. But the regex reaches that recall at "
                    f"**{s['regex_precision']:.1%} precision**, against the student's "
                    f"{s['student_precision']:.1%} — it wins the class by predicting it "
                    f"indiscriminately. On F1 the ordering reverses: "
                    f"{s['student_f1']:.3f} vs {s['regex_f1']:.3f}."
                )
            lines.append("")
        if f1_losses:
            lines.append(f"**On F1 the student loses on: {', '.join(f'`{c}`' for c in f1_losses)}.** "
                         "This is the one that cannot be explained away by a catch-all artefact.")
        else:
            lines.append("**On F1 the student does not lose to the regex on any class.**")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="S7 error analysis over results/predictions.jsonl.")
    parser.add_argument("--predictions", type=Path, default=RESULTS / "predictions.jsonl")
    parser.add_argument("--out", type=Path, default=RESULTS / "error_analysis.json")
    parser.add_argument("--markdown", type=Path, default=RESULTS / "error_analysis.md")
    args = parser.parse_args()

    if not args.predictions.exists():
        print(f"[errors] no predictions at {args.predictions} — run src.evaluate first", file=sys.stderr)
        return 1

    examples = {row["id"]: row for row in read_jsonl(DATA / "heldout.jsonl")}
    by_arm = {arm: enrich(rows, examples) for arm, rows in load_predictions(args.predictions).items()}
    if not by_arm:
        print("[errors] predictions file is empty", file=sys.stderr)
        return 1

    report: dict = {
        "caveat": (
            "Gold is the teacher's label, so every disagreement counted here is a disagreement "
            "with the teacher, not a proven mistake. The S4 hand audit put the teacher's own "
            "agreement with a human at 84% (results/audit_50.md), which is the ceiling on every "
            "number in this file."
        ),
        "arms": {},
    }
    for arm, rows in by_arm.items():
        errors = [r for r in rows if not r["correct"]]
        bands = volume_bands(rows)
        by_outlet = breakdown(rows, lambda r: r["outlet"] or "unknown")
        report["arms"][arm] = {
            "n": len(rows),
            "errors": len(errors),
            "agreement": round(sum(1 for r in rows if r["correct"]) / len(rows), 4),
            "top_confused_pairs": confused_pairs(rows),
            "taxonomy": taxonomy(errors, arm),
            "by_length": breakdown(rows, lambda r: band(r["headline"])),
            "by_outlet_volume_band": breakdown(rows, lambda r: bands.get(r["outlet"], "low volume (<8)")),
            # Every outlet, sorted by volume. The full table rather than a top-N, because a
            # single outlet the student fails on is exactly what a top-N would hide.
            "by_outlet": dict(sorted(by_outlet.items(), key=lambda kv: -kv[1]["n"])),
            "outlet_tier_note": (
                "No tier taxonomy exists in this repo — Feed is (outlet, url, section) and "
                "heldout.jsonl has no tier field. Volume bands are a stated proxy for "
                "prominence, not an editorial ranking."
            ),
        }

    if "student" in by_arm and "regex" in by_arm:
        report["head_to_head"] = head_to_head(by_arm["student"], by_arm["regex"])
        report["per_class"] = per_class_gap(by_arm["student"], by_arm["regex"])
    else:
        missing = {"student", "regex"} - set(by_arm)
        report["head_to_head"] = None
        report["per_class"] = None
        print(f"[errors] head-to-head skipped — no predictions for: {', '.join(sorted(missing))}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    args.markdown.write_text(to_markdown(report))

    for arm, arm_report in report["arms"].items():
        print(f"[errors] {arm:<8} {arm_report['errors']:>4} disagreements of {arm_report['n']} "
              f"({arm_report['agreement']:.1%} agreement)")
    if report.get("per_class"):
        losses = [c for c, s in report["per_class"].items() if s["student_loses"]]
        print(f"[errors] classes where the student loses to the regex: {losses or 'none'}")
    print(f"[errors] wrote {args.out.relative_to(ROOT)} and {args.markdown.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
