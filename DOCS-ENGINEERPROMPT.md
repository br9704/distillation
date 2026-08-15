# ENGINEERPROMPT — Documentation Pass
# Paste this into every project folder. It makes the repo read well on GitHub.

> **This is the same prompt for every project.** It reads the repo, the masterplan, and the CLAUDE.md, then rewrites the README and produces a machine-readable `PROJECT.json` that the portfolio consumes. Run it in a project **after** that project's engineering is done, and **before** the portfolio prompt (`~/bruno-portfolio/PORTFOLIO-RELAUNCH-ENGINEERPROMPT.md`), which reads what this produces.

---

## What you are doing, in one sentence

Make this repo the kind of thing an engineer stars, a recruiter screenshots, and the portfolio can render from — without inventing a single number.

## Ground rules

Everything in `CLAUDE.md` still binds: aethereum sync, masterplan discipline, honesty rules. Two additions for this pass specifically:

1. **Every number in the README maps to a committed artifact.** A test count links to the CI run or test file. A benchmark result links to `results/`. A latency figure links to the script that measured it. If the artifact doesn't exist, the number doesn't go in.
2. **The masterplan is your primary source, not the code.** Every masterplan in this set carries As-shipped deltas, verification records, and decisions with their reasons. That is the story of how this was built. Read it fully first — the README should reflect what actually happened, including what was found broken and repaired, because that is more interesting and more credible than a clean feature list.

---

## Phase 1 — Read (do not skip)

In this order:
1. `CLAUDE.md` — rules and the current-state line
2. `masterplan.md` / `MASTERPLAN.md` — **all of it**, especially: verified facts, locked decisions, As-shipped deltas, `[⏭]` deferrals with reasons, and the owner-gate block. Note every number that appears with a source.
3. `RESEARCH-CONTEXT.md` if present — the measured audit that started this
4. `MOTION.md` if present
5. The current README, to see what claims are already live and which the masterplan now contradicts
6. The code — enough to draw the architecture honestly and to verify any number you plan to cite

Then run the project. `npm test`, `npm run build`, whatever the masterplan's acceptance gates say. **Capture real output.** You will use it.

## Phase 2 — Ask (AskUserQuestion, all at once)

Only what you cannot decide from the repo:
- Which of the owner-gated items are now done? (published to npm, deployed, live URL, HF weights up, disclosure sent). The README changes shape depending on the answers — a published package leads with `npx`; an unpublished one leads with the demo.
- Any number Bruno wants held back or softened?
- For projects with a case-study on the portfolio: is the case study public, or still password-locked?

## Phase 3 — Plan mode

Draft the README outline and the `PROJECT.json` values, present both, get approval. Then add a "Sprint D — Documentation" section to the masterplan in its conventions and work it with status marks like any other sprint.

## Phase 4 — Build

### 4.1 The README

Structure — this order, these sections, nothing before the hook:

**Hook (above the fold, no heading).** One line: what it does and why it exists. Then **one visual** — a recorded terminal demo, a screenshot of the real product, or the headline chart. Then the one-line run command if there is one (`npx …`, live URL, `pip install`). Then a **results table or headline number** for anything with measurements. A reader who never scrolls should still know what this is, see it, and know the number.

**Badges row** — only ones that resolve: CI status, npm version + provenance, license, tests. No badge that 404s or reads "unknown". If the package isn't published, no npm badge until it is.

**What it does** — three to six short paragraphs of prose. Not a feature bullet list. What problem, what approach, what's distinctive. Write for a strong engineer who has never heard of it.

**Architecture** — a **Mermaid diagram** (GitHub renders these natively) showing the real components and data flow, plus a paragraph explaining the one or two design decisions that mattered. Pull those from the masterplan's `record_decision` entries and locked-decisions block. Draw what exists, not what was planned.

**How it was built** — this is the section most READMEs don't have and it's the one that makes yours different. Two or three paragraphs, from the masterplan: what the audit found when work started (if there was one — the RESEARCH-CONTEXT and the As-shipped deltas will tell you), what broke and was repaired, what was measured and what the measurement changed. Honest and specific. Include a link to the masterplan itself: `[masterplan.md](./masterplan.md)` — it's the receipts.

**Results / Evidence** — for benchmarks, models, tools with measurements: the full table, the chart, the methodology link, the limitations. Lead with what didn't work if there is such a thing. For projects without measurements, this section is "Verification" — what's tested, how, and the CI link.

**Usage** — real, copy-pasteable commands with real output shown. Flags table if a CLI.

**Limitations** — a real section. Every project has them; the masterplan's `[⏭]` deferrals and non-goals are the source. This is a credibility section, not a weakness section.

**Status** — one paragraph: what's shipped, what's owner-gated, what's next. Link to the masterplan's owner-gate block.

**License · Author** — footer. Author line links to brunojaamaa.dev and GitHub.

Rules for the prose:
- Outcomes, not process. "45× cheaper, measured with the real tokeniser" not "extensive cost analysis was performed". "Zero detectable effect at N=24" not "comprehensive benchmarking".
- No emoji in the README. GitHub's rendering of the terminal aesthetic is code blocks and tables — use them.
- No "blazing fast", "seamless", "powerful", "robust". Say the number or say nothing.
- Every claim a stranger could check, they should be able to: link the test, the run, the file.
- Screenshots and recordings go in `docs/media/` (or `assets/`), committed. Not external hosts. Recorded terminal demos: asciinema-to-SVG or a GIF under 3 MB.
- Section headings are sentence-case, plain.

### 4.2 `PROJECT.json` at repo root — the machine-readable card

The portfolio reads this. It is the single source of truth for what the portfolio may say about this project. Schema:

```json
{
  "schema": 1,
  "slug": "gitpulse",
  "name": "GITPULSE",
  "oneLiner": "≤ 90 chars, outcome-first, no adjectives",
  "status": "shipped | live | published | in-development | archived",
  "role": "SOLO BUILD",
  "year": "2026",
  "updated": "2026-08-15",
  "links": {
    "github": "https://github.com/br9704/…",
    "live": null,
    "npm": null,
    "huggingface": null,
    "appstore": null
  },
  "stack": ["typescript", "node", "…"],
  "metrics": [
    { "value": "45×", "label": "cheaper than the teacher", "source": "results/summary.json" },
    { "value": "0.00%", "label": "unparseable labels", "source": "results/labels/audit.json" }
  ],
  "headline": {
    "claim": "The single most interesting true sentence about this project.",
    "source": "README.md#results"
  },
  "honest": "One or two sentences on where it does not work / what is not proven. Required, never empty.",
  "media": {
    "hero": "docs/media/hero.png",
    "demo": "docs/media/demo.gif",
    "diagram": "docs/media/architecture.svg"
  },
  "built": {
    "audit": "What was found when work started, one sentence, or null.",
    "repaired": ["…", "…"],
    "measured": ["…"],
    "decisions": [{ "what": "Yjs over Redis", "why": "…" }]
  },
  "ownerGated": ["publish to npm", "…"],
  "masterplan": "masterplan.md"
}
```

Every `metrics[].source` and `headline.source` must point at a file that exists in the repo. `honest` is required — a project with an empty `honest` field is a project you haven't finished reading the masterplan for.

### 4.3 Repo hygiene

- `LICENSE` exists and matches `package.json`
- `package.json` has `repository`, `homepage`, `bugs`, `description`, `keywords`
- GitHub repo description + topics set (write them into `PROJECT.json` under `github.topics` and Bruno applies them; or use `gh repo edit` if authenticated)
- Delete process artifacts that aren't the masterplan: session logs, `TEST_REPORT_*.md`, agent handoff notes that duplicate the masterplan. Keep: README, CHANGELOG, masterplan, CLAUDE.md, MOTION.md, RESEARCH-CONTEXT.md, docs/.
- `.github/` has the CI workflow that produces the badge you're showing

## Phase 5 — Verify

- [ ] Render the README with GitHub's markdown (`gh markdown` or push to a branch and look). Mermaid diagram renders. Every image resolves. Every badge resolves.
- [ ] Every number in the README: grep it, find its source, confirm the source says the same thing
- [ ] `PROJECT.json` validates against the schema above; every `source` path exists
- [ ] Read the README aloud. Anywhere it sounds like marketing, rewrite it. Anywhere it sounds like a changelog, rewrite it.
- [ ] `record_verification` with the checklist as evidence; update the CLAUDE.md current-state line; close Sprint D in the masterplan.

## What "done" looks like

A stranger lands on the repo, sees a picture and a number in the first screen, understands the architecture from one diagram, learns something from "how it was built" that they wouldn't get from any other README, and can find the receipt for every claim. And `PROJECT.json` sits at the root ready for the portfolio to consume.
