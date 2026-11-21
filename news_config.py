"""Settings for the Daily News engine. Edit this file to change what you see.

Rules of the engine (see news_engine.py):
  * Only feeds listed in SOURCES are read. A story is accepted only if its link
    points to that source's own domain(s) (no redirects or aggregator junk).
  * Headlines are shown exactly as published, with the outlet's own summary.
    No AI rewriting, so nothing can be "invented" by the engine.
  * A story must be reported by at least MIN_PUBLISHERS different outlets,
    unless it comes from an official source or its category is relaxed below.
"""

# tier: "official" = government / international body (primary source)
#       "major"    = large established newsroom
#       "regional" = established local outlet
# NOTE: feed URLs are public RSS endpoints that outlets can change at any time.
# The app's Sources panel shows which feeds worked on the last run.
SOURCES = [
    # ---- World
    {"name": "BBC News", "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
     "domains": ("bbc.co.uk", "bbc.com"), "category": "World", "tier": "major"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss",
     "domains": ("theguardian.com",), "category": "World", "tier": "major"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml",
     "domains": ("aljazeera.com",), "category": "World", "tier": "major"},
    {"name": "Deutsche Welle", "url": "https://rss.dw.com/rdf/rss-en-all",
     "domains": ("dw.com",), "category": "World", "tier": "major"},
    {"name": "NPR", "url": "https://feeds.npr.org/1004/rss.xml",
     "domains": ("npr.org",), "category": "World", "tier": "major"},

    # ---- India
    {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss",
     "domains": ("thehindu.com",), "category": "India", "tier": "major"},
    {"name": "Indian Express", "url": "https://indianexpress.com/section/india/feed/",
     "domains": ("indianexpress.com",), "category": "India", "tier": "major"},
    {"name": "Hindustan Times", "url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
     "domains": ("hindustantimes.com",), "category": "India", "tier": "major"},
    {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
     "domains": ("timesofindia.indiatimes.com", "indiatimes.com"), "category": "India", "tier": "major"},
    {"name": "PIB (Govt of India)", "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
     "domains": ("pib.gov.in",), "category": "India", "tier": "official"},

    # ---- Bahrain & Gulf (verify these feeds in the Sources panel; local outlets change URLs often)
    {"name": "Al Jazeera (Gulf)", "url": "https://www.aljazeera.com/xml/rss/all.xml",
     "domains": ("aljazeera.com",), "category": "Bahrain & Gulf", "tier": "major",
     "keywords": ("bahrain", "manama", "gulf", "gcc", "saudi", "uae", "emirates", "qatar", "kuwait", "oman")},
    {"name": "Gulf Daily News", "url": "https://www.gdnonline.com/rss.aspx",
     "domains": ("gdnonline.com",), "category": "Bahrain & Gulf", "tier": "regional"},
    {"name": "Bahrain News Agency", "url": "https://www.bna.bh/en/rss.aspx",
     "domains": ("bna.bh",), "category": "Bahrain & Gulf", "tier": "official"},
    {"name": "BBC Middle East", "url": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
     "domains": ("bbc.co.uk", "bbc.com"), "category": "Bahrain & Gulf", "tier": "major",
     "keywords": ("bahrain", "manama", "gulf", "gcc", "saudi", "uae", "emirates", "qatar", "kuwait", "oman")},

    # ---- Economy & everyday money (prices, jobs, inflation, fuel; not stock tips)
    {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
     "domains": ("bbc.co.uk", "bbc.com"), "category": "Economy", "tier": "major"},
    {"name": "The Guardian Business", "url": "https://www.theguardian.com/business/rss",
     "domains": ("theguardian.com",), "category": "Economy", "tier": "major"},
    {"name": "The Hindu Business", "url": "https://www.thehindu.com/business/feeder/default.rss",
     "domains": ("thehindu.com",), "category": "Economy", "tier": "major"},
    {"name": "Reserve Bank of India", "url": "https://rbi.org.in/pressreleases_rss.xml",
     "domains": ("rbi.org.in",), "category": "Economy", "tier": "official"},

    # ---- Health
    {"name": "WHO", "url": "https://www.who.int/rss-feeds/news-english.xml",
     "domains": ("who.int",), "category": "Health", "tier": "official"},
    {"name": "BBC Health", "url": "https://feeds.bbci.co.uk/news/health/rss.xml",
     "domains": ("bbc.co.uk", "bbc.com"), "category": "Health", "tier": "major"},

    # ---- Science & Technology
    {"name": "BBC Technology", "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
     "domains": ("bbc.co.uk", "bbc.com"), "category": "Technology", "tier": "major"},
    {"name": "The Guardian Technology", "url": "https://www.theguardian.com/technology/rss",
     "domains": ("theguardian.com",), "category": "Technology", "tier": "major"},
    {"name": "BBC Science", "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
     "domains": ("bbc.co.uk", "bbc.com"), "category": "Science", "tier": "major"},
    {"name": "NASA", "url": "https://www.nasa.gov/feed/",
     "domains": ("nasa.gov",), "category": "Science", "tier": "official"},

    # ---- Explained: background articles that explain *why*, not just *what happened*
    {"name": "Indian Express Explained", "url": "https://indianexpress.com/section/explained/feed/",
     "domains": ("indianexpress.com",), "category": "Explained", "tier": "major"},
    {"name": "The Conversation", "url": "https://theconversation.com/global/articles.atom",
     "domains": ("theconversation.com",), "category": "Explained", "tier": "major"},
    {"name": "The Guardian Long Read", "url": "https://www.theguardian.com/news/series/the-long-read/rss",
     "domains": ("theguardian.com",), "category": "Explained", "tier": "major"},

    # ---- Sports (results and major events only; remove this block if you do not want sports)
    {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml",
     "domains": ("bbc.co.uk", "bbc.com"), "category": "Sports", "tier": "major"},
    {"name": "The Hindu Sport", "url": "https://www.thehindu.com/sport/feeder/default.rss",
     "domains": ("thehindu.com",), "category": "Sports", "tier": "major"},
]

# Order shown to the reader, and how many stories to show per category.
CATEGORY_ORDER = ["India", "Bahrain & Gulf", "World", "Explained", "Economy", "Health", "Technology", "Science", "Sports"]
PER_CATEGORY = {"India": 6, "Bahrain & Gulf": 5, "World": 6, "Economy": 4,
                "Explained": 4, "Health": 3, "Technology": 3, "Science": 3, "Sports": 3}

# Categories you do not want at all (e.g. {"Sports"}).
MUTED_CATEGORIES = set()

# How many different outlets must report a story before it is shown.
MIN_PUBLISHERS = 2
# Categories where one reputable outlet is enough (shown with a "1 source" label).
SINGLE_SOURCE_OK = {"Explained", "Bahrain & Gulf", "Health", "Technology", "Science", "Sports"}

# Only stories from the last N hours.
MAX_AGE_HOURS = 30
# Explainers stay useful longer than breaking news.
MAX_AGE_BY_CATEGORY = {"Explained": 96}
# Categories made of background articles, not events: shown as "Explainer", not as confirmed reports.
EXPLAINER_CATEGORIES = {"Explained"}

# ---- "Unwanted news" filter -------------------------------------------------
# Any headline/summary matching one of these (case-insensitive) is dropped.
BLOCK_WORDS = [
    "horoscope", "zodiac", "astrology", "celebrity", "celeb ", "gossip", "bollywood",
    "box office", "red carpet", "net worth", "dating", "girlfriend", "boyfriend",
    "wedding", "viral", "trolled", "reels", "influencer", "outfit", "fashion week",
    "you won't believe", "shocking", "jaw-dropping", "heartbreaking", "this is why",
    "quiz", "puzzle", "crossword", "recipe", "gift guide", "deals", "discount code",
    "sponsored", "advertorial", "web series", "ott release", "trailer", "teaser",
    "tv show", "reality show", "bigg boss", "k-pop",
]
# Links containing these path pieces are opinion/video/gallery pages, not news reports.
BLOCK_URL_PARTS = [
    "/opinion", "/comment", "/editorial", "/lifestyle", "/entertainment", "/video",
    "/videos", "/gallery", "/photos", "/podcast", "/sponsored", "/brandstudio",
    "/horoscope", "/astrology", "/cartoon", "/crossword", "/puzzle", "/quiz",
]
# Market-trading chatter you said you don't want in the daily news. (Economy news about
# prices, jobs, inflation or fuel stays; stock tips and trading calls go.)
BLOCK_TRADING = [
    "stocks to buy", "stock picks", "buy or sell", "target price", "price target",
    "technical analysis", "intraday", "top gainers", "top losers", "sensex today",
    "nifty today", "share price", "multibagger",
]

# ---- "Must know" section: the last 7 days, only what every citizen should know -------------
# Categories that can appear in it (sports, technology, science and explainers stay in Today only).
MUST_KNOW_CATEGORIES = {"India", "Bahrain & Gulf", "World", "Economy", "Health"}
# A story qualifies if an official source reported it, OR 3+ outlets reported it, OR it stayed in the news 2+ days.
MUST_KNOW_MIN_OUTLETS = 3
MUST_KNOW_MIN_DAYS = 2
MUST_KNOW_LIMIT = 10          # total stories shown
MUST_KNOW_PER_CATEGORY = 4    # so one topic cannot fill the whole list
