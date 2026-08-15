# Error analysis — held-out 500

Gold is the teacher's label, so every disagreement counted here is a disagreement with the teacher, not a proven mistake. The S4 hand audit put the teacher's own agreement with a human at 84% (results/audit_50.md), which is the ceiling on every number in this file.

## student

- 500 scored · 73 disagreements · agreement 85.4%

**Top confused pairs**

| gold | predicted | n |
|---|---|---|
| `general` | `science` | 7 |
| `consumer` | `tech` | 7 |
| `general` | `geopolitics` | 7 |
| `general` | `entertainment` | 5 |
| `consumer` | `general` | 4 |

**Errors by cause**

- **disagreement involving the `general` catch-all** — 39 (53.4% of this arm's errors)
  - "NHS must plan for heatwaves like it does for winter, health secretary says" · bbc.com · gold `science`, said `general`
  - "Hundreds attend teenager's eclipse party" · bbc.com · gold `general`, said `science`
- **cross-domain confusion: consumer vs tech** — 7 (9.6% of this arm's errors)
  - "Apple official refurb store: Save hundreds on our top picks of the week" · 9to5mac.com · gold `consumer`, said `tech`
  - "Ford on track to complete $2B factory overhaul for Fathom EV truck" · techcrunch.com · gold `consumer`, said `tech`
- **cross-domain confusion: finance vs tech** — 3 (4.1% of this arm's errors)
  - "Fox News AI Newsletter: One year until AI market busts, investor says" · foxnews.com · gold `finance`, said `tech`
  - "Chinese EVs pull into the lead" · cbsnews.com · gold `finance`, said `tech`
- **cross-domain confusion: entertainment vs science** — 2 (2.7% of this arm's errors)
  - "Einstein the musician, AI prophets and more: Books in brief" · nature.com · gold `entertainment`, said `science`
  - "EJ Swift wins the 2026 Arthur C Clarke award for science fiction" · theguardian.com · gold `entertainment`, said `science`
- **cross-domain confusion: finance vs geopolitics** — 2 (2.7% of this arm's errors)
  - "White House revives unprecedented effort to remove Fed governor Lisa Cook" · axios.com · gold `finance`, said `geopolitics`
  - "Transit giant CRRC sets down marker in Hong Kong as sales pitch to overseas cities" · scmp.com · gold `finance`, said `geopolitics`
- **cross-domain confusion: tech vs finance** — 2 (2.7% of this arm's errors)
  - "Anthropic’s $2 trillion problem: Its underlying business is nowhere near the IPO valuation it wants" · fortune.com · gold `tech`, said `finance`
  - "AI ecosystem's 'circular' investment: risk or advantage?" · dw.com · gold `tech`, said `finance`
- **cross-domain confusion: consumer vs finance** — 2 (2.7% of this arm's errors)
  - "'Funflation' hits home: Why staying in isn't the cost-saver it used to be" · cnbc.com · gold `consumer`, said `finance`
  - "Finding an apartment in Manhattan is getting even harder, as listings plummet and rents reach $5,000" · businessinsider.com · gold `consumer`, said `finance`
- **cross-domain confusion: entertainment vs geopolitics** — 2 (2.7% of this arm's errors)
  - "What Nolan’s Odysseus tells us about Western elite’s existential angst" · scmp.com · gold `entertainment`, said `geopolitics`
  - "Cover Story newsletter: The Mythos moment" · economist.com · gold `entertainment`, said `geopolitics`
- **cross-domain confusion: tech vs science** — 1 (1.4% of this arm's errors)
  - "Artificial Intelligence used to design brand new viruses" · bbc.com · gold `tech`, said `science`
- **cross-domain confusion: sports vs tech** — 1 (1.4% of this arm's errors)
  - "Apple in talks to acquire streaming rights for golf’s Open Championship: report" · 9to5mac.com · gold `sports`, said `tech`
- **cross-domain confusion: science vs tech** — 1 (1.4% of this arm's errors)
  - "US boosts drone surveillance as flesh-eating screwworms spread in Texas" · arstechnica.com · gold `science`, said `tech`
- **cross-domain confusion: science vs entertainment** — 1 (1.4% of this arm's errors)
  - "Where Wild Things Go" · newyorker.com · gold `science`, said `entertainment`
- **cross-domain confusion: tech vs geopolitics** — 1 (1.4% of this arm's errors)
  - "Truth Social’s sale of fast access to Trump posts draws legal concerns" · washingtonpost.com · gold `tech`, said `geopolitics`
- **cross-domain confusion: consumer vs entertainment** — 1 (1.4% of this arm's errors)
  - "Bakery buys comedian's former sites after closure" · bbc.com · gold `consumer`, said `entertainment`
- **cross-domain confusion: geopolitics vs finance** — 1 (1.4% of this arm's errors)
  - "Trade court upholds Trump's closure of 'de minimis' loophole" · cnbc.com · gold `geopolitics`, said `finance`
- **cross-domain confusion: consumer vs science** — 1 (1.4% of this arm's errors)
  - "‘It’s been a revelation’: how heat pumps can cool your home in a heatwave" · theguardian.com · gold `consumer`, said `science`
- **cross-domain confusion: science vs geopolitics** — 1 (1.4% of this arm's errors)
  - "The EU climate policy the world copied is under fire — what's at stake?" · dw.com · gold `science`, said `geopolitics`
- **cross-domain confusion: geopolitics vs tech** — 1 (1.4% of this arm's errors)
  - "Humanoid robots: Trump's latest China trade battle?" · dw.com · gold `geopolitics`, said `tech`
- **cross-domain confusion: geopolitics vs entertainment** — 1 (1.4% of this arm's errors)
  - "Stockard Channing: ‘I cried at the election of Joe Biden, thinking we were out of the woods. Wrong!’" · theguardian.com · gold `geopolitics`, said `entertainment`
- **cross-domain confusion: entertainment vs consumer** — 1 (1.4% of this arm's errors)
  - "Meet David Advance Plus+, genius of toothpaste marketing: the Stephen Collins cartoon" · theguardian.com · gold `entertainment`, said `consumer`
- **cross-domain confusion: sports vs geopolitics** — 1 (1.4% of this arm's errors)
  - "Trump lingers awkwardly long after presenting World Cup trophy to Spain. It could have been worse" · latimes.com · gold `sports`, said `geopolitics`
- **cross-domain confusion: consumer vs sports** — 1 (1.4% of this arm's errors)
  - "‘Community spaces are being taken away’: campaigners rail at rise of pay-to-play padel courts" · theguardian.com · gold `consumer`, said `sports`

**By headline length**

| band | n | agreement |
|---|---|---|
| long (70-89) | 141 | 78.7% |
| medium (40-69) | 245 | 88.2% |
| short (<40 ch) | 33 | 78.8% |
| very long (90+) | 81 | 91.4% |

**By outlet volume band**

_No tier taxonomy exists in this repo — Feed is (outlet, url, section) and heldout.jsonl has no tier field. Volume bands are a stated proxy for prominence, not an editorial ranking._

| band | n | agreement |
|---|---|---|
| high volume (20+ held-out headlines) | 238 | 85.7% |
| low volume (<8) | 114 | 87.7% |
| medium volume (8-19) | 148 | 83.1% |

**Weakest outlets** (8+ held-out headlines)

| outlet | n | agreement |
|---|---|---|
| washingtonpost.com | 11 | 54.5% |
| scmp.com | 8 | 62.5% |
| economist.com | 8 | 75.0% |
| 9to5mac.com | 17 | 76.5% |
| cbsnews.com | 22 | 77.3% |

## regex

- 500 scored · 329 disagreements · agreement 34.2%

**Top confused pairs**

| gold | predicted | n |
|---|---|---|
| `geopolitics` | `general` | 78 |
| `science` | `general` | 59 |
| `entertainment` | `general` | 50 |
| `sports` | `general` | 39 |
| `finance` | `general` | 31 |

**Errors by cause**

- **regex catch-all: no keyword matched, fell through to `general`** — 310 (94.2% of this arm's errors)
  - "Initiatives aim to help breastfeeding difficulties" · bbc.com · gold `science`, said `general`
  - "Two deadly flowers could inspire powerful new medicines" · sciencedaily.com · gold `science`, said `general`
- **regex first-match-wins: an earlier branch claimed the headline** — 18 (5.5% of this arm's errors)
  - "Space news: The Perseid meteor shower, the Sun's surface, and a SpaceX moon crash" · npr.org · gold `science`, said `tech`
  - "Einstein the musician, AI prophets and more: Books in brief" · nature.com · gold `entertainment`, said `tech`
- **regex matched a keyword the story is not about** — 1 (0.3% of this arm's errors)
  - "Video shows moment man throws yogurt on two women in Iran" · cnn.com · gold `general`, said `geopolitics`

**By headline length**

| band | n | agreement |
|---|---|---|
| long (70-89) | 141 | 41.1% |
| medium (40-69) | 245 | 32.2% |
| short (<40 ch) | 33 | 6.1% |
| very long (90+) | 81 | 39.5% |

**By outlet volume band**

_No tier taxonomy exists in this repo — Feed is (outlet, url, section) and heldout.jsonl has no tier field. Volume bands are a stated proxy for prominence, not an editorial ranking._

| band | n | agreement |
|---|---|---|
| high volume (20+ held-out headlines) | 238 | 28.6% |
| low volume (<8) | 114 | 41.2% |
| medium volume (8-19) | 148 | 37.8% |

**Weakest outlets** (8+ held-out headlines)

| outlet | n | agreement |
|---|---|---|
| espn.com | 13 | 7.7% |
| thehill.com | 12 | 8.3% |
| bbc.com | 47 | 17.0% |
| cnn.com | 23 | 17.4% |
| sciencedaily.com | 23 | 26.1% |

## Student versus the incumbent

- Student right where the regex is wrong: **285**
- Regex right where the student is wrong: **29**

Student wins, verbatim:

- "Initiatives aim to help breastfeeding difficulties" — gold `science`, regex said `general`
- "Two deadly flowers could inspire powerful new medicines" — gold `science`, regex said `general`
- "Stress can scramble your brain’s internal GPS, MRI study finds" — gold `science`, regex said `general`
- "DNA reveals a society organised around women in pre-Roman Britain" — gold `science`, regex said `general`
- "1 in 5 people may carry this hidden genetic heart risk" — gold `science`, regex said `general`
- "Sun-like star caught after eating one of its own planets" — gold `science`, regex said `general`

Regex wins, verbatim — these lead the README if any class regresses:

- "Hundreds attend teenager's eclipse party" — gold `general`, student said `science`
- "Capybaras Were the Newest Lobbyists in This Brazilian Legislature" — gold `general`, student said `science`
- "Apple in talks to acquire streaming rights for golf’s Open Championship: report" — gold `sports`, student said `tech`
- "Fox News AI Newsletter: One year until AI market busts, investor says" — gold `finance`, student said `tech`
- "Burnham tells cabinet to tackle living costs at first meeting" — gold `general`, student said `geopolitics`
- "Graham Platner to speak at Maine rally in return to public eye" — gold `general`, student said `geopolitics`

## Per class, student versus regex

| class | n | student recall | regex recall | Δ recall | student F1 | regex F1 | Δ F1 |
|---|---|---|---|---|---|---|---|
| `geopolitics` | 97 | 92.8% | 19.6% | +73.2% | 0.895 | 0.317 | +0.579 |
| `finance` | 51 | 86.3% | 33.3% | +52.9% | 0.871 | 0.486 | +0.386 |
| `tech` | 60 | 93.3% | 53.3% | +40.0% | 0.868 | 0.627 | +0.241 |
| `sports` | 52 | 94.2% | 25.0% | +69.2% | 0.952 | 0.394 | +0.558 |
| `entertainment` | 62 | 85.5% | 12.9% | +72.6% | 0.862 | 0.229 | +0.633 |
| `science` | 78 | 92.3% | 21.8% | +70.5% | 0.894 | 0.350 | +0.544 |
| `consumer` | 34 | 52.9% | 0.0% | +52.9% | 0.679 | 0.000 | +0.679 |
| `general` | 66 | 68.2% | 98.5% | -30.3% ⚠︎ | 0.698 | 0.295 | +0.403 |

**The student loses to the regex on recall for: `general`.** Per CLAUDE.md this leads rather than being buried.

- `general`: student recall 68.2% vs regex 98.5%. But the regex reaches that recall at **17.3% precision**, against the student's 71.4% — it wins the class by predicting it indiscriminately. On F1 the ordering reverses: 0.698 vs 0.295.

**On F1 the student does not lose to the regex on any class.**

