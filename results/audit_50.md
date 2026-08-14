# Teacher label audit — 50 held-out examples, adjudicated by hand

Stratified sample (seed 4242): up to 7 per teacher-assigned class, so every class is actually
audited rather than only the large ones. Adjudicated by the engineer against
`CLASS_DEFINITIONS` in `src/schema.py` — the same definitions the teacher was given.

**This number is the ceiling.** The student is trained on these labels and scored against
them, so it cannot be meaningfully more right than they are. Reported before any student
result exists, so it cannot be tuned to flatter one.

Verdicts:
- **AGREE** — I would have assigned the same label.
- **DISAGREE** — I would have assigned a different one, and I think the teacher is wrong.
- **AMBIGUOUS** — the headline honestly supports two classes, or is unknowable from the
  headline alone. Counted separately rather than folded into either side, because calling
  these "errors" would overstate teacher noise and calling them "agreements" would understate
  the task's difficulty.

## Result

| | count | rate |
|---|---|---|
| AGREE | 42 | **84%** |
| DISAGREE | 3 | 6% |
| AMBIGUOUS | 5 | 10% |

**Strict agreement: 84%.** Excluding the genuinely ambiguous: **42/45 = 93%.**

Both numbers get reported. The strict one is the conservative ceiling; the second is the
fairer read of how often the teacher is actually wrong.

## The systematic finding: the taxonomy has no `politics` class

The three disagreements are individually minor. The **inconsistency** underneath them is not.

The teacher routes US domestic politics to `general` sometimes and `geopolitics` other times:

| # | headline | teacher |
|---|---|---|
| 22 | Mamdani's luxury-home tax gets new life as appeals court lifts roadblock | `general` |
| 25 | Trump's New Plan to Get His Name Back on the Kennedy Center | `general` |
| 28 | Graham Platner to speak at Maine rally in return to public eye | `general` |
| 29 | Concerned about Trump's ballroom project, Senate Democrats seek audit | `geopolitics` |
| 30 | O'Reilly: 'I don't believe the American public are going to buy the socialist communist…' | `geopolitics` |
| 33 | Barabak: Democrats are at each other's throats — this time over the 2028 calendar | `geopolitics` |
| 35 | Warren presses RFK Jr. on Trump ties to lettuce distributor | `geopolitics` |

This is not the teacher being sloppy. **The eight-class taxonomy — inherited verbatim from
the product — has no home for domestic politics.** `geopolitics` is defined as relations
*between states* (and, per its keyword list, war and diplomacy); `general` is the catch-all.
A story about a Senate audit or a state-level tax fits neither, so the boundary is genuinely
undecidable and any labeller will wobble across it.

Consequences, all of which belong in S8's limitations:
1. It is an irreducible noise floor on this class pair, for **every** arm.
2. The student will inherit the wobble and be scored against it, so some of its `general` ↔
   `geopolitics` confusion in S7 will be the taxonomy's fault rather than the model's. The
   error analysis must separate the two rather than charging it all to the student.
3. It is a real, actionable finding for Sentinel: the product's own category set is missing a
   `politics` class, and a ninth class would likely improve the incumbent regex too.

## Adjudications

| # | teacher | verdict | note |
|---|---|---|---|
| 1 | consumer | AGREE | retail / main-street trends |
| 2 | consumer | AGREE | promo codes, unambiguous |
| 3 | consumer | AGREE | product review; `tech` arguable for EVs |
| 4 | consumer | AGREE | consumer-protection policy |
| 5 | consumer | AGREE | pricing/deals beats the Apple→tech pull |
| 6 | consumer | AGREE | product roundup |
| 7 | consumer | **DISAGREE** | "Flying a sports car with wings" — I read this as `tech` |
| 8 | entertainment | AGREE | celebrity |
| 9 | entertainment | AGREE | music/culture; `general` arguable |
| 10 | entertainment | AGREE | TV development |
| 11 | entertainment | AGREE | celebrity |
| 12 | entertainment | AGREE | Apple exec, but the story is Ted Lasso |
| 13 | entertainment | AGREE | celebrity |
| 14 | entertainment | AGREE | TV |
| 15 | finance | AGREE | CPI |
| 16 | finance | AGREE | executive compensation |
| 17 | finance | AGREE | crypto |
| 18 | finance | AGREE | corporate/business |
| 19 | finance | AGREE | equities |
| 20 | finance | AGREE | asset management |
| 21 | finance | **DISAGREE** | "AI market busts" from an AI newsletter — I read this as `tech` |
| 22 | general | AGREE | weak; see taxonomy note |
| 23 | general | AGREE | FOIA/administrative |
| 24 | general | AGREE | crime |
| 25 | general | AGREE | weak; Kennedy Center makes `entertainment` arguable too |
| 26 | general | AGREE | weak; `finance` arguable |
| 27 | general | AGREE | crime |
| 28 | general | **DISAGREE** | a campaign rally is an election story; `CLASS_DEFINITIONS` puts elections in `geopolitics` |
| 29 | geopolitics | AMBIGUOUS | domestic oversight — see taxonomy note |
| 30 | geopolitics | AMBIGUOUS | domestic political commentary |
| 31 | geopolitics | AMBIGUOUS | headline alone does not identify the subject |
| 32 | geopolitics | AGREE | naval deployment |
| 33 | geopolitics | AGREE | elections, per the definition given |
| 34 | geopolitics | AGREE | war |
| 35 | geopolitics | AMBIGUOUS | oversight vs food safety (`consumer`) |
| 36 | science | AGREE | planetary science |
| 37 | science | AGREE | health |
| 38 | science | AGREE | health |
| 39 | science | AGREE | space |
| 40 | science | AGREE | health |
| 41 | science | AGREE | research methods (Nature) |
| 42 | science | AGREE | health/astronomy |
| 43 | sports | AGREE | football |
| 44 | sports | AGREE | cricket |
| 45 | sports | AGREE | baseball |
| 46 | sports | AGREE | memorabilia; `consumer` arguable |
| 47 | sports | AMBIGUOUS | "HQ PM Newsletter 8/13/2026" — unknowable from the headline; the teacher used the outlet signal, which is legitimate but unverifiable |
| 48 | sports | AGREE | football |
| 49 | sports | AGREE | football transfer |
| 50 | tech | AGREE | security breach |

## A second, smaller note

Two of the five AMBIGUOUS cases (#31, #47) are **uninformative headlines** — newsletter
titles that carry no topical content at all. The teacher can only fall back on the outlet.
That is a reasonable strategy and the student will learn it too, but it means a slice of both
arms' apparent accuracy is outlet-prior rather than headline understanding. Worth a sentence
in METHODOLOGY.
