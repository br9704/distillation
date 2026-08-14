"""The wire-feed catalog, transcribed from Sentinel's production backend:
  ~/Desktop/AI REPORTING APP MVP/supabase/functions/_shared/wire.ts:34-115

63 feeds across 9 editorial sections. Transcribed rather than fetched so this repo has no
runtime dependency on the product repo.

**The sections are the reason the corpus works.** The plan expected to stratify on the
regex's own labels, which would have been circular and would have left the tail classes
thin — `sports`, `science` and `entertainment` are rare in hard-news feeds, and the regex
only finds them when its keyword list happens to fire. But the catalog already carries
dedicated sports, science, entertainment, tech and markets sections. Sampling across
sections gives genuine tail-class coverage from a source independent of the thing being
measured.

`section` is **not** a label. It is a sampling stratum and a weak prior — Variety publishes
business stories, ESPN publishes legal ones. The teacher assigns labels; this only decides
what gets shown to the teacher.
"""

from __future__ import annotations

from typing import NamedTuple


class Feed(NamedTuple):
    outlet: str  # lowercase hostname without www., matching extractOutlet() in wire.ts
    url: str
    section: str  # sampling stratum, NOT a label


FEEDS: tuple[Feed, ...] = (
    # ── Wire services + general news ──────────────────────────────────────────────
    Feed("apnews.com", "https://feedx.net/rss/ap.xml", "general"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/rss.xml", "general"),
    Feed("cnn.com", "http://rss.cnn.com/rss/edition.rss", "general"),
    Feed("foxnews.com", "https://moxie.foxnews.com/google-publisher/latest.xml", "general"),
    Feed("nbcnews.com", "https://feeds.nbcnews.com/nbcnews/public/news", "general"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "general"),
    Feed("washingtonpost.com", "http://feeds.washingtonpost.com/rss/national", "general"),
    Feed("wsj.com", "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "general"),
    Feed("theguardian.com", "https://www.theguardian.com/world/rss", "general"),
    Feed("economist.com", "https://www.economist.com/the-world-this-week/rss.xml", "general"),
    Feed("abcnews.go.com", "https://abcnews.go.com/abcnews/topstories", "general"),
    Feed("cbsnews.com", "https://www.cbsnews.com/latest/rss/main", "general"),
    Feed("usatoday.com", "https://rssfeeds.usatoday.com/usatoday-NewsTopStories", "general"),
    Feed("latimes.com", "https://www.latimes.com/world-nation/rss2.0.xml", "general"),
    Feed("newsweek.com", "https://www.newsweek.com/rss", "general"),
    Feed("huffpost.com", "https://chaski.huffpost.com/us/auto/vertical/front-page", "general"),
    # ── International / regional ──────────────────────────────────────────────────
    Feed("aljazeera.com", "https://www.aljazeera.com/xml/rss/all.xml", "international"),
    Feed("dw.com", "https://rss.dw.com/rdf/rss-en-all", "international"),
    Feed("france24.com", "https://www.france24.com/en/rss", "international"),
    Feed("nhk.or.jp", "https://www3.nhk.or.jp/rj/podcast/rss/english.xml", "international"),
    Feed("scmp.com", "https://www.scmp.com/rss/91/feed", "international"),
    Feed(
        "channelnewsasia.com",
        "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6511",
        "international",
    ),
    Feed("rferl.org", "https://www.rferl.org/api/zrqiteuuipt", "international"),
    Feed("haaretz.com", "https://www.haaretz.com/cmlink/1.628752", "international"),
    Feed("smh.com.au", "https://www.smh.com.au/rss/feed.xml", "international"),
    Feed(
        "ctvnews.ca",
        "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009",
        "international",
    ),
    # ── Markets / business ────────────────────────────────────────────────────────
    Feed("cnbc.com", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "markets"),
    Feed("marketwatch.com", "https://feeds.content.dowjones.io/public/rss/mw_topstories", "markets"),
    Feed("businessinsider.com", "https://www.businessinsider.com/rss", "markets"),
    Feed("fortune.com", "https://fortune.com/feed", "markets"),
    Feed("forbes.com", "https://www.forbes.com/business/feed/", "markets"),
    Feed("yahoo.com", "https://www.yahoo.com/news/rss", "markets"),
    Feed("fool.com", "https://www.fool.com/feeds/index.aspx", "markets"),
    Feed("investing.com", "https://www.investing.com/rss/news.rss", "markets"),
    Feed("barrons.com", "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain", "markets"),
    # ── Politics / opinion ────────────────────────────────────────────────────────
    Feed("axios.com", "https://api.axios.com/feed/", "politics"),
    Feed("thehill.com", "https://thehill.com/feed/", "politics"),
    Feed("vox.com", "https://www.vox.com/rss/index.xml", "politics"),
    Feed("slate.com", "https://slate.com/feeds/all.rss", "politics"),
    Feed("theatlantic.com", "https://www.theatlantic.com/feed/all/", "politics"),
    Feed("newyorker.com", "https://www.newyorker.com/feed/everything", "politics"),
    # ── Public radio / nonprofit ──────────────────────────────────────────────────
    Feed("npr.org", "https://feeds.npr.org/1001/rss.xml", "public"),
    Feed("propublica.org", "https://www.propublica.org/feeds/propublica/main", "public"),
    # ── Tech ──────────────────────────────────────────────────────────────────────
    Feed("techcrunch.com", "https://techcrunch.com/feed/", "tech"),
    Feed("theverge.com", "https://www.theverge.com/rss/index.xml", "tech"),
    Feed("wired.com", "https://www.wired.com/feed/rss", "tech"),
    Feed("arstechnica.com", "https://feeds.arstechnica.com/arstechnica/index", "tech"),
    Feed("engadget.com", "https://www.engadget.com/rss.xml", "tech"),
    Feed("9to5mac.com", "https://9to5mac.com/feed/", "tech"),
    Feed("macrumors.com", "https://feeds.macrumors.com/MacRumors-All", "tech"),
    Feed("venturebeat.com", "https://venturebeat.com/feed/", "tech"),
    Feed("zdnet.com", "https://www.zdnet.com/news/rss.xml", "tech"),
    # ── Sports ────────────────────────────────────────────────────────────────────
    Feed("espn.com", "https://www.espn.com/espn/rss/news", "sports"),
    Feed("bleacherreport.com", "https://bleacherreport.com/articles/feed", "sports"),
    Feed("cbssports.com", "https://www.cbssports.com/rss/headlines/", "sports"),
    # ── Science ───────────────────────────────────────────────────────────────────
    Feed("scientificamerican.com", "https://www.scientificamerican.com/feed/", "science"),
    Feed("newscientist.com", "https://www.newscientist.com/feed/home/", "science"),
    Feed("sciencedaily.com", "https://www.sciencedaily.com/rss/all.xml", "science"),
    Feed("nature.com", "https://www.nature.com/nature.rss", "science"),
    # ── Entertainment ─────────────────────────────────────────────────────────────
    Feed("variety.com", "https://variety.com/feed/", "entertainment"),
    Feed("hollywoodreporter.com", "https://www.hollywoodreporter.com/feed/", "entertainment"),
    Feed("deadline.com", "https://deadline.com/feed/", "entertainment"),
    Feed("pitchfork.com", "https://pitchfork.com/feed/feed-news/rss", "entertainment"),
)

# ── Same-outlet section expansion ─────────────────────────────────────────────────────
#
# One pass over the 63 production feeds yields ~1,800 unique headlines, and repeat passes
# yield sharply less as the feeds only cycle so fast. Reaching 5,500 needed more volume
# from somewhere, and there were three options:
#
#   1. GDELT backfill — tested, and it throttles far harder than its documented
#      1-req/5s: a single request succeeds and the next two 429 even at 20s spacing.
#      It returned 52 articles for techcrunch/7d against a requested 250. Kept as a
#      supplementary trickle in src/gdelt.py, but it cannot carry the corpus.
#   2. Many more repeat passes over hours — free and reliable, but slow.
#   3. **Section feeds from the outlets already in the catalog** — chosen.
#
# Option 3 preserves what actually defines the distribution: the outlets. BBC's technology
# feed is the same newsroom as BBC's front page. Every URL below belongs to an outlet
# already present in FEEDS above — nothing new was introduced, and one candidate
# (skysports.com) was dropped for exactly that reason despite working.
#
# It also fixes the tail-class problem at the source. The production catalog has 3 sports
# feeds and 4 science feeds against 16 general ones; the expansion adds 11 sports and 17
# science. Probed live: 84 of 86 candidates returned items.
EXPANSION_FEEDS: tuple[Feed, ...] = (
    # bbc
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/world/rss.xml", "general"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/business/rss.xml", "markets"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/technology/rss.xml", "tech"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "science"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "entertainment"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/sport/rss.xml", "sports"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/politics/rss.xml", "politics"),
    Feed("bbc.com", "https://feeds.bbci.co.uk/news/health/rss.xml", "science"),
    # guardian
    Feed("theguardian.com", "https://www.theguardian.com/uk/technology/rss", "tech"),
    Feed("theguardian.com", "https://www.theguardian.com/uk/business/rss", "markets"),
    Feed("theguardian.com", "https://www.theguardian.com/uk/sport/rss", "sports"),
    Feed("theguardian.com", "https://www.theguardian.com/uk/culture/rss", "entertainment"),
    Feed("theguardian.com", "https://www.theguardian.com/science/rss", "science"),
    Feed("theguardian.com", "https://www.theguardian.com/environment/rss", "science"),
    Feed("theguardian.com", "https://www.theguardian.com/us-news/rss", "general"),
    Feed("theguardian.com", "https://www.theguardian.com/politics/rss", "politics"),
    Feed("theguardian.com", "https://www.theguardian.com/film/rss", "entertainment"),
    Feed("theguardian.com", "https://www.theguardian.com/music/rss", "entertainment"),
    Feed("theguardian.com", "https://www.theguardian.com/money/rss", "markets"),
    Feed("theguardian.com", "https://www.theguardian.com/lifeandstyle/rss", "general"),
    # nytimes
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "tech"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "markets"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml", "science"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml", "sports"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Arts.xml", "entertainment"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "international"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml", "science"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Movies.xml", "entertainment"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Music.xml", "entertainment"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml", "markets"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml", "tech"),
    Feed("nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml", "politics"),
    # cnn
    Feed("cnn.com", "http://rss.cnn.com/rss/edition_world.rss", "international"),
    Feed("cnn.com", "http://rss.cnn.com/rss/edition_technology.rss", "tech"),
    Feed("cnn.com", "http://rss.cnn.com/rss/money_news_international.rss", "markets"),
    Feed("cnn.com", "http://rss.cnn.com/rss/edition_sport.rss", "sports"),
    Feed("cnn.com", "http://rss.cnn.com/rss/edition_entertainment.rss", "entertainment"),
    Feed("cnn.com", "http://rss.cnn.com/rss/edition_space.rss", "science"),
    # npr
    Feed("npr.org", "https://feeds.npr.org/1004/rss.xml", "international"),
    Feed("npr.org", "https://feeds.npr.org/1019/rss.xml", "tech"),
    Feed("npr.org", "https://feeds.npr.org/1007/rss.xml", "science"),
    Feed("npr.org", "https://feeds.npr.org/1008/rss.xml", "entertainment"),
    Feed("npr.org", "https://feeds.npr.org/1006/rss.xml", "markets"),
    Feed("npr.org", "https://feeds.npr.org/1014/rss.xml", "politics"),
    Feed("npr.org", "https://feeds.npr.org/1039/rss.xml", "entertainment"),
    Feed("npr.org", "https://feeds.npr.org/1128/rss.xml", "science"),
    # washington post
    Feed("washingtonpost.com", "https://feeds.washingtonpost.com/rss/world", "international"),
    Feed("washingtonpost.com", "https://feeds.washingtonpost.com/rss/business", "markets"),
    Feed("washingtonpost.com", "https://feeds.washingtonpost.com/rss/politics", "politics"),
    Feed("washingtonpost.com", "https://feeds.washingtonpost.com/rss/sports", "sports"),
    Feed("washingtonpost.com", "https://feeds.washingtonpost.com/rss/lifestyle", "general"),
    # cnbc
    Feed("cnbc.com", "https://www.cnbc.com/id/19854910/device/rss/rss.html", "tech"),
    Feed("cnbc.com", "https://www.cnbc.com/id/10001147/device/rss/rss.html", "markets"),
    Feed("cnbc.com", "https://www.cnbc.com/id/20910258/device/rss/rss.html", "markets"),
    Feed("cnbc.com", "https://www.cnbc.com/id/10000664/device/rss/rss.html", "markets"),
    # espn
    Feed("espn.com", "https://www.espn.com/espn/rss/nfl/news", "sports"),
    Feed("espn.com", "https://www.espn.com/espn/rss/nba/news", "sports"),
    Feed("espn.com", "https://www.espn.com/espn/rss/mlb/news", "sports"),
    Feed("espn.com", "https://www.espn.com/espn/rss/nhl/news", "sports"),
    Feed("espn.com", "https://www.espn.com/espn/rss/soccer/news", "sports"),
    # sciencedaily
    Feed("sciencedaily.com", "https://www.sciencedaily.com/rss/top/science.xml", "science"),
    Feed("sciencedaily.com", "https://www.sciencedaily.com/rss/top/health.xml", "science"),
    Feed("sciencedaily.com", "https://www.sciencedaily.com/rss/top/technology.xml", "tech"),
    Feed("sciencedaily.com", "https://www.sciencedaily.com/rss/space_time.xml", "science"),
    # fox news
    Feed("foxnews.com", "https://moxie.foxnews.com/google-publisher/world.xml", "international"),
    Feed("foxnews.com", "https://moxie.foxnews.com/google-publisher/politics.xml", "politics"),
    Feed("foxnews.com", "https://moxie.foxnews.com/google-publisher/science.xml", "science"),
    Feed("foxnews.com", "https://moxie.foxnews.com/google-publisher/tech.xml", "tech"),
    Feed("foxnews.com", "https://moxie.foxnews.com/google-publisher/sports.xml", "sports"),
    Feed("foxnews.com", "https://moxie.foxnews.com/google-publisher/entertainment.xml", "entertainment"),
    # cbs news
    Feed("cbsnews.com", "https://www.cbsnews.com/latest/rss/world", "international"),
    Feed("cbsnews.com", "https://www.cbsnews.com/latest/rss/technology", "tech"),
    Feed("cbsnews.com", "https://www.cbsnews.com/latest/rss/entertainment", "entertainment"),
    Feed("cbsnews.com", "https://www.cbsnews.com/latest/rss/science", "science"),
    Feed("cbsnews.com", "https://www.cbsnews.com/latest/rss/moneywatch", "markets"),
    # nbc news
    Feed("nbcnews.com", "https://feeds.nbcnews.com/nbcnews/public/world", "international"),
    Feed("nbcnews.com", "https://feeds.nbcnews.com/nbcnews/public/science", "science"),
    Feed("nbcnews.com", "https://feeds.nbcnews.com/nbcnews/public/politics", "politics"),
    # variety
    Feed("variety.com", "https://variety.com/v/film/feed/", "entertainment"),
    Feed("variety.com", "https://variety.com/v/music/feed/", "entertainment"),
    Feed("variety.com", "https://variety.com/v/tv/feed/", "entertainment"),
    # marketwatch
    Feed("marketwatch.com", "https://feeds.content.dowjones.io/public/rss/mw_marketpulse", "markets"),
    # the verge
    Feed("theverge.com", "https://www.theverge.com/tech/rss/index.xml", "tech"),
)

# What harvest.py actually fetches.
ALL_FEEDS: tuple[Feed, ...] = FEEDS + EXPANSION_FEEDS

SECTIONS: tuple[str, ...] = (
    "general",
    "international",
    "markets",
    "politics",
    "public",
    "tech",
    "sports",
    "science",
    "entertainment",
)

# Production settings, from wire.ts:117-118.
RSS_FETCH_TIMEOUT_MS = 5_000
RSS_MAX_ITEMS = 10

assert {f.section for f in ALL_FEEDS} <= set(SECTIONS), "a feed has an unknown section"
assert len({f.url for f in ALL_FEEDS}) == len(ALL_FEEDS), "duplicate feed URL"
# Outlet fidelity: the expansion must never introduce an outlet the product does not read.
assert {f.outlet for f in EXPANSION_FEEDS} <= {f.outlet for f in FEEDS}, (
    "expansion introduced an outlet absent from the production catalog"
)
