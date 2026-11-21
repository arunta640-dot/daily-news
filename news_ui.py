"""Look and feel for the Daily News page. Pure HTML/CSS strings, so it is easy to test and restyle."""
import datetime as dt
import html

import news_config as cfg

# One colour per category (like metro lines). Light and dark variants live in the CSS below.
CAT_CLASS = {"India": "c-india", "Bahrain & Gulf": "c-gulf", "World": "c-world", "Explained": "c-explain", "Economy": "c-econ",
             "Health": "c-health", "Technology": "c-tech", "Science": "c-sci", "Sports": "c-sport"}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;700;800&display=swap');
:root{--bg:#f4f6f9;--surface:#ffffff;--ink:#17212b;--muted:#586577;--line:#dfe4ea;--ok:#0f7a55;--warn:#9a6a00;--official:#1d5fd0;
--c-india:#d96b00;--c-gulf:#c8102e;--c-world:#1d5fd0;--c-econ:#0f8a5f;--c-health:#b02a80;--c-explain:#8a5a2b;--c-tech:#6444d0;--c-sci:#0a7f98;--c-sport:#9a7410}
@media (prefers-color-scheme: dark){:root{--bg:#0f141a;--surface:#18202a;--ink:#eef2f6;--muted:#9aa8b8;--line:#2b3644;--ok:#4cc79b;--warn:#e5b34a;--official:#6fa3ff;
--c-india:#ff9a3d;--c-gulf:#ff5a73;--c-world:#6fa3ff;--c-econ:#45c796;--c-health:#ee6fbf;--c-explain:#d9a566;--c-tech:#a08cff;--c-sci:#4cc4dd;--c-sport:#e0b54a}}
.stApp{background:var(--bg)}
header[data-testid="stHeader"],footer,#MainMenu{display:none!important}
.block-container{max-width:720px!important;padding:.9rem 16px 4rem!important}
div[data-baseweb="tab-list"]{gap:1.4rem}
div[data-baseweb="tab-list"] button p{font-family:'Schibsted Grotesk',system-ui,sans-serif;font-size:1.02rem;font-weight:500;color:var(--muted)}
div[data-baseweb="tab-list"] button[aria-selected="true"] p{color:var(--ink);font-weight:700}
div[data-baseweb="tab-highlight"]{background-color:var(--ink)!important;height:3px!important}
div[data-baseweb="tab-border"]{background-color:var(--line)!important}
.dn,.dn *{font-family:'Schibsted Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif;box-sizing:border-box}
.dn{color:var(--ink);line-height:1.5}
.dn a{color:inherit;text-decoration:none}
.dn a:hover .hl,.dn a:focus-visible .hl{text-decoration:underline;text-underline-offset:3px}
.dn a:focus-visible{outline:3px solid var(--official);outline-offset:3px;border-radius:4px}
.c-india{--c:var(--c-india)}.c-gulf{--c:var(--c-gulf)}.c-world{--c:var(--c-world)}.c-econ{--c:var(--c-econ)}
.c-explain{--c:var(--c-explain)}.c-health{--c:var(--c-health)}.c-tech{--c:var(--c-tech)}.c-sci{--c:var(--c-sci)}.c-sport{--c:var(--c-sport)}

.mast{padding:.8rem 0 1rem}
.dn .mast h1{font-size:clamp(2.3rem,9vw,3.4rem);font-weight:800;letter-spacing:-.035em;line-height:1;margin:0!important;padding:0!important}
.mast .date{font-size:1.05rem;font-weight:500;margin-top:.55rem}
.mast .state{font-size:.9rem;color:var(--muted);margin-top:.15rem}

.jump{display:flex;gap:.45rem;overflow-x:auto;padding:.2rem 0 1rem;margin:0 -16px;padding-left:16px;padding-right:16px;scrollbar-width:none}
.jump::-webkit-scrollbar{display:none}
.jump a{flex:none;display:flex;align-items:center;gap:.45rem;padding:.5rem .85rem;border-radius:999px;background:var(--surface);border:1px solid var(--line);font-size:.92rem;font-weight:500;min-height:40px}
.jump a:before{content:"";width:.6rem;height:.6rem;border-radius:50%;background:var(--c)}

.lead{display:block;background:var(--surface);border-radius:18px;padding:1.45rem 1.2rem 1.1rem;box-shadow:inset 0 6px 0 var(--c);margin:.2rem 0 2rem}
.lead .cat{font-weight:700;color:var(--c);font-size:.95rem}
.lead .hl{font-size:clamp(1.5rem,5.6vw,2rem);font-weight:800;line-height:1.15;letter-spacing:-.02em;margin:.35rem 0 .55rem}
.lead .sum{color:var(--muted);font-size:1.02rem;margin:0 0 .8rem}

.sec{margin:2rem 0 0;scroll-margin-top:1rem}
.dn .sec h2{padding:0!important;display:flex;align-items:center;gap:.6rem;font-size:1.35rem;font-weight:800;letter-spacing:-.015em;margin:0 0 .3rem}
.sec h2:before{content:"";width:6px;height:1.4rem;border-radius:3px;background:var(--c)}
.story{display:block;padding:.95rem 0 1rem}
.story+.story{border-top:1px solid var(--line)}
.story.mk .cat{display:flex;align-items:center;gap:.45rem;font-weight:700;font-size:.9rem;color:var(--c);margin-bottom:.2rem}
.story.mk .cat:before{content:"";width:.6rem;height:.6rem;border-radius:50%;background:var(--c)}
.story .hl{font-size:1.14rem;font-weight:700;line-height:1.3;letter-spacing:-.01em}
.story .sum{color:var(--muted);font-size:.98rem;margin:.3rem 0 0;max-width:62ch}
.sum{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}

.meta{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem 1rem;margin-top:.6rem;font-size:.86rem;color:var(--muted)}
.dots{display:inline-flex;align-items:center;gap:.28rem;font-weight:500}
.dots i{width:.55rem;height:.55rem;border-radius:50%;background:var(--ok)}
.dots.one i{background:var(--warn)}
.dots.exp i{background:var(--c,var(--muted))}
.dots.off{color:var(--official)}
.dots.off i{background:var(--official)}
.dots b{font-weight:600;margin-left:.15rem}
.src{overflow-wrap:anywhere}

.empty{background:var(--surface);border-radius:14px;padding:1.2rem;margin:1rem 0}
.empty strong{display:block;font-size:1.1rem;margin-bottom:.25rem}
.foot{color:var(--muted);font-size:.88rem;margin-top:2.4rem}
@media (prefers-reduced-motion:no-preference){.lead{animation:rise .5s ease-out both}}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
"""


def _e(text):
    return html.escape(text or "", quote=True)


def ago(iso, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    mins = max(0, int((now - dt.datetime.fromisoformat(iso)).total_seconds() // 60))
    if mins < 60:
        return f"{max(mins, 1)} min ago"
    hours = mins // 60
    return f"{hours} h ago" if hours < 24 else f"{hours // 24} d ago"


def _confirmation(story):
    n = story["n_sources"]
    if story.get("confirmation") == "Explainer":
        return '<span class="dots exp"><i></i><b>Explainer</b></span>'
    if story["official"] and n == 1:
        return '<span class="dots off"><i></i><b>Official source</b></span>'
    cls = "dots" if n > 1 else "dots one"
    dots = "<i></i>" * min(n, 5)
    label = f"{n} outlets" if n > 1 else "1 outlet"
    return f'<span class="{cls}">{dots}<b>{label}</b></span>'


def _meta(story, now):
    names = _e(", ".join(s["name"] for s in story["sources"]))
    return (f'<div class="meta">{_confirmation(story)}<span>{_e(ago(story["published"], now))}</span>'
            f'<span class="src">{names}</span></div>')


def _slug(cat):
    return "sec-" + "".join(ch if ch.isalnum() else "-" for ch in cat.lower())


def lead_html(story, now):
    cls = CAT_CLASS.get(story["category"], "c-world")
    summary = f'<p class="sum">{_e(story["summary"])}</p>' if story["summary"] else ""
    return (f'<a class="lead {cls}" href="{_e(story["url"])}" target="_blank" rel="noopener">'
            f'<div class="cat">{_e(story["category"])}</div><div class="hl">{_e(story["title"])}</div>'
            f'{summary}{_meta(story, now)}</a>')


def story_html(story, now):
    summary = f'<p class="sum">{_e(story["summary"])}</p>' if story["summary"] else ""
    return (f'<a class="story" href="{_e(story["url"])}" target="_blank" rel="noopener">'
            f'<div class="hl">{_e(story["title"])}</div>{summary}{_meta(story, now)}</a>')


def _must_know_story_html(story):
    cls = CAT_CLASS.get(story["category"], "c-world")
    summary = f'<p class="sum">{_e(story["summary"])}</p>' if story["summary"] else ""
    why = f'In the news for {story["days_seen"]} days' if story["days_seen"] > 1 else ""
    names = _e(", ".join(s["name"] for s in story["sources"]))
    return (f'<a class="story mk {cls}" href="{_e(story["url"])}" target="_blank" rel="noopener">'
            f'<div class="cat">{_e(story["category"])}</div><div class="hl">{_e(story["title"])}</div>{summary}'
            f'<div class="meta">{_confirmation(story)}{f"<span><b>{_e(why)}</b></span>" if why else ""}'
            f'<span class="src">{names}</span></div></a>')


def must_know_html(result):
    parts = ['<div class="dn"><div class="mast"><h1>Must know</h1>']
    if result["stories"]:
        parts.append(f'<div class="date">Last {result["days_covered"]} day{"s" if result["days_covered"] != 1 else ""} of news</div>'
                     '<div class="state">The most important stories first. Missed a few days? Start here.</div></div>')
        parts.append("".join(_must_know_story_html(s) for s in result["stories"]))
    else:
        parts.append('</div><div class="empty"><strong>Nothing qualifies yet</strong>'
                     'Stories appear here when an official source or several outlets report them, or when they stay in the news for days.</div>')
    parts.append('<p class="foot">Only India, Bahrain &amp; Gulf, World, Economy and Health stories are considered. '
                 'Sports, technology and science stay in Today.</p></div>')
    return "".join(parts)


def pick_lead(stories):
    """The big top card: official or widely reported news first; explainers and local incidents avoided."""
    news = [s for s in stories if s.get("confirmation") != "Explainer"]
    if not news:
        return None

    def rank(s):
        text = s["title"].lower()
        strong = s["official"] or s["n_sources"] >= cfg.LEAD_MIN_OUTLETS
        demoted = any(w in text for w in cfg.LEAD_DEMOTE_WORDS)
        return (strong and not demoted, not demoted, s["score"])
    return max(news, key=rank)


def page_html(digest, now=None, local_offset_hours=3):
    now = now or dt.datetime.now(dt.timezone.utc)
    local = now + dt.timedelta(hours=local_offset_hours)
    parts = ['<div class="dn">',
             f'<div class="mast"><h1>Daily News</h1><div class="date">{local:%A, %d %B %Y}</div>'
             f'<div class="state">Updated {local:%H:%M}, {digest["feeds_ok"]} of {digest["feeds_total"]} sources reachable</div></div>']
    sections = digest["sections"]
    if not sections:
        parts.append('<div class="empty"><strong>No confirmed stories right now</strong>'
                     'The news sources may be unreachable. Press Refresh in a minute, or open the source report below.</div>')
    else:
        parts.append('<nav class="jump" aria-label="Categories">' + "".join(
            f'<a class="{CAT_CLASS.get(c, "c-world")}" href="#{_slug(c)}">{_e(c)}</a>' for c in sections) + "</nav>")
        top = pick_lead([s for stories in sections.values() for s in stories])
        if top:
            parts.append(lead_html(top, now))
        for cat, stories in sections.items():
            rest = [s for s in stories if s is not top]
            if not rest:
                continue
            parts.append(f'<section class="sec {CAT_CLASS.get(cat, "c-world")}" id="{_slug(cat)}"><h2>{_e(cat)}</h2>'
                         + "".join(story_html(s, now) for s in rest) + "</section>")
    parts.append(f'<p class="foot">{digest["total_stories"]} stories. {digest["unconfirmed_dropped"]} stories were left out '
                 f'because too few outlets reported them. Dots show how many outlets reported each story.</p></div>')
    return "".join(parts)
