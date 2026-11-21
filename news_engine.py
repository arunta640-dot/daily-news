"""Daily News engine: everyday news for a citizen, from a whitelist of genuine sources.

Pipeline:  fetch feeds -> keep only whitelisted domains and fresh items -> drop unwanted
topics -> group the same story across outlets -> require enough independent outlets ->
rank -> short digest per category.

No AI is used. Headlines and summaries are shown exactly as the outlet published them.
Standard library only (plus nothing else), so it runs anywhere, including GitHub Actions.
"""
import datetime as dt
import email.utils
import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import news_config as cfg

UA = "DailyNewsEngine/1.0 (personal RSS reader)"
_STOP = set("""a an the and or but of in on at to for from by with as is are was were be been it its this that
these those after before over under into than then up down out about new says say said will would could
may might has have had not no more most their his her they them he she we you i our your amid""".split())
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


# ----------------------------------------------------------------------------- fetching
def _http_get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _clean_text(value):
    return _WS.sub(" ", html.unescape(_TAG.sub(" ", value or ""))).strip()


def _parse_date(value):
    if not value:
        return None
    value = value.strip()
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        parsed = None
    if parsed is None:
        try:
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def parse_feed(raw, source):
    """Return raw entries (title, url, summary, published) from an RSS 2.0, RDF or Atom document."""
    root = ET.fromstring(raw)
    out = []
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        fields = {}
        for child in node:
            ctag = child.tag.split("}")[-1].lower()
            if ctag == "link" and not (child.text or "").strip():
                fields.setdefault("link", child.get("href", ""))
            elif ctag in ("title", "link", "description", "summary", "pubdate", "published", "updated", "date"):
                fields.setdefault(ctag, (child.text or "").strip())
        out.append({
            "title": _clean_text(fields.get("title")),
            "url": (fields.get("link") or "").strip(),
            "summary": _clean_text(fields.get("description") or fields.get("summary"))[:300],
            "published": _parse_date(fields.get("pubdate") or fields.get("published")
                                     or fields.get("updated") or fields.get("date")),
        })
    return out


# ----------------------------------------------------------------------------- filtering
def _host_allowed(url, domains):
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in domains)


def unwanted_reason(title, summary, url):
    """Return why an item is unwanted, or None if it is fine."""
    low_url = (url or "").lower()
    for part in cfg.BLOCK_URL_PARTS:
        if part in low_url:
            return f"link type {part}"
    text = f" {title} {summary} ".lower()
    for word in list(cfg.BLOCK_WORDS) + list(cfg.BLOCK_TRADING):
        if word in text:
            return f"blocked word '{word.strip()}'"
    return None


def _tokens(title):
    words = re.findall(r"[a-z0-9]+", title.lower())
    return {w for w in words if w not in _STOP and len(w) > 2}


def _same_story(a, b):
    if not a or not b:
        return False
    inter = len(a & b)
    return inter >= 3 and inter / len(a | b) >= 0.4


def _accept(entry, source, now, stats):
    if not entry["title"] or not entry["url"]:
        stats["invalid"] += 1
        return None
    if not _host_allowed(entry["url"], source["domains"]):
        stats["off_domain"] += 1
        return None
    published = entry["published"]
    max_age = cfg.MAX_AGE_BY_CATEGORY.get(source["category"], cfg.MAX_AGE_HOURS)
    if published is None or (now - published) > dt.timedelta(hours=max_age) \
            or published > now + dt.timedelta(hours=1):
        stats["stale_or_undated"] += 1
        return None
    keys = source.get("keywords")
    if keys and not any(k in f"{entry['title']} {entry['summary']}".lower() for k in keys):
        stats["off_topic"] += 1
        return None
    if unwanted_reason(entry["title"], entry["summary"], entry["url"]):
        stats["unwanted"] += 1
        return None
    return {**entry, "source": source["name"], "outlet": source["domains"][0], "tier": source["tier"],
            "category": source["category"], "tokens": _tokens(entry["title"])}


# ----------------------------------------------------------------------------- grouping & ranking
def group_stories(items):
    """Group items about the same event (within a category) across outlets."""
    groups = []
    for item in sorted(items, key=lambda x: x["published"], reverse=True):
        for g in groups:
            if g["category"] == item["category"] and _same_story(g["tokens"], item["tokens"]):
                g["items"].append(item)
                g["tokens"] |= item["tokens"]
                break
        else:
            groups.append({"category": item["category"], "tokens": set(item["tokens"]), "items": [item]})
    return groups


_TIER_RANK = {"official": 0, "major": 1, "regional": 2}


def _publishers(group):
    seen = {}
    for it in group["items"]:
        seen.setdefault(it["outlet"], it)  # two feeds of one outlet count once
    return seen


def _story(group, now):
    pubs = _publishers(group)
    lead = min(pubs.values(), key=lambda i: (_TIER_RANK[i["tier"]], -i["published"].timestamp()))
    newest = max(i["published"] for i in group["items"])
    hours_old = (now - newest).total_seconds() / 3600
    official = any(i["tier"] == "official" for i in pubs.values())
    score = 10 * len(pubs) + (8 if official else 0) - 0.2 * hours_old
    return {
        "category": group["category"],
        "title": lead["title"],
        "summary": lead["summary"],
        "url": lead["url"],
        "lead_source": lead["source"],
        "sources": [{"name": i["source"], "url": i["url"]} for i in pubs.values()],
        "n_sources": len(pubs),
        "official": official,
        "published": newest.isoformat(),
        "score": round(score, 2),
        "confirmation": ("Explainer" if group["category"] in cfg.EXPLAINER_CATEGORIES
                         else "Official source" if official and len(pubs) == 1
                         else f"Reported by {len(pubs)} outlets" if len(pubs) > 1
                         else "Single source"),
    }


def _enough_support(group):
    pubs = _publishers(group)
    if any(i["tier"] == "official" for i in pubs.values()):
        return True
    need = 1 if group["category"] in cfg.SINGLE_SOURCE_OK else cfg.MIN_PUBLISHERS
    return len(pubs) >= need


# ----------------------------------------------------------------------------- main entry
def build_digest(now=None, fetch=_http_get, sources=None):
    """Fetch every feed and return the digest. `fetch(url)` can be replaced for testing."""
    now = now or dt.datetime.now(dt.timezone.utc)
    sources = [s for s in (sources or cfg.SOURCES) if s["category"] not in cfg.MUTED_CATEGORIES]
    stats_by_source, accepted = {}, []

    def work(src):
        stats = dict(fetched=0, kept=0, invalid=0, off_domain=0, stale_or_undated=0,
                     off_topic=0, unwanted=0, error=None)
        kept = []
        try:
            entries = parse_feed(fetch(src["url"]), src)
            stats["fetched"] = len(entries)
            for e in entries:
                item = _accept(e, src, now, stats)
                if item:
                    kept.append(item)
            stats["kept"] = len(kept)
        except Exception as exc:  # one broken feed must never stop the digest
            stats["error"] = f"{type(exc).__name__}: {exc}"[:160]
        return src, stats, kept

    with ThreadPoolExecutor(max_workers=6) as pool:
        for src, stats, kept in pool.map(work, sources):
            key = f"{src['name']} [{src['category']}]"
            stats_by_source[key] = stats
            accepted.extend(kept)

    groups = group_stories(accepted)
    dropped_weak = sum(1 for g in groups if not _enough_support(g))
    stories = [_story(g, now) for g in groups if _enough_support(g)]

    sections = {}
    for cat in cfg.CATEGORY_ORDER:
        if cat in cfg.MUTED_CATEGORIES:
            continue
        ranked = sorted((s for s in stories if s["category"] == cat), key=lambda s: -s["score"])
        if ranked:
            sections[cat] = ranked[: cfg.PER_CATEGORY.get(cat, 4)]

    ok = [k for k, v in stats_by_source.items() if not v["error"]]
    return {
        "generated_at": now.isoformat(),
        "sections": sections,
        "total_stories": sum(len(v) for v in sections.values()),
        "feeds_ok": len(ok),
        "feeds_total": len(stats_by_source),
        "unconfirmed_dropped": dropped_weak,
        "source_report": stats_by_source,
    }


def to_text(digest, tz_offset_hours=3, limit=3900):
    """Plain-text version for Telegram / email / terminal."""
    local = dt.datetime.fromisoformat(digest["generated_at"]) + dt.timedelta(hours=tz_offset_hours)
    lines = [f"Daily News - {local:%a %d %b %Y}"]
    for cat, stories in digest["sections"].items():
        lines.append(f"\n== {cat} ==")
        for s in stories:
            tag = "" if s["confirmation"] != "Single source" else f" ({s['confirmation'].lower()}: {s['lead_source']})"
            lines.append(f"- {s['title']}{tag}\n  {s['url']}")
    if not digest["sections"]:
        lines.append("\nNo confirmed stories right now. Feeds may be unreachable.")
    lines.append(f"\nSources working: {digest['feeds_ok']}/{digest['feeds_total']}")
    return "\n".join(lines)[:limit]


def to_notification(digest, per_category=3, limit=3500):
    """Short headline list for a phone notification (full links live in the app)."""
    lines = []
    for cat, stories in digest["sections"].items():
        lines.append(cat.upper())
        for s in stories[:per_category]:
            lines.append(f"- {s['title']}")
        lines.append("")
    text = "\n".join(lines).strip() or "No confirmed stories right now."
    raw = text.encode("utf-8")[:limit]
    return raw.decode("utf-8", errors="ignore")
