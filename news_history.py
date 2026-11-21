"""Keeps a small history of daily digests so the app can show 'This week'."""
import datetime as dt
import json
import os
import tempfile

import news_config as cfg
import news_engine

HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_history")


def save_digest(digest, directory=HISTORY_DIR, keep_days=30):
    os.makedirs(directory, exist_ok=True)
    day = digest["generated_at"][:10]
    slim = {"date": day, "sections": digest["sections"]}
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(slim, fh, ensure_ascii=False)
    os.replace(tmp, os.path.join(directory, f"{day}.json"))
    cutoff = (dt.date.fromisoformat(day) - dt.timedelta(days=keep_days)).isoformat()
    for name in os.listdir(directory):
        if name.endswith(".json") and name[:-5] < cutoff:
            os.remove(os.path.join(directory, name))


def load_days(directory=HISTORY_DIR, days=7, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    start = (today - dt.timedelta(days=days - 1)).isoformat()
    out = []
    if not os.path.isdir(directory):
        return out
    for name in sorted(os.listdir(directory)):
        if name.endswith(".json") and start <= name[:-5] <= today.isoformat():
            try:
                with open(os.path.join(directory, name), encoding="utf-8") as fh:
                    out.append(json.load(fh))
            except (OSError, ValueError):
                continue  # a damaged day never breaks the week
    return out


def _merge_stories(history):
    """Merge the same story across days. Returns one record per story with how long it stayed in the news."""
    groups = []
    for day in history:
        for cat, stories in day["sections"].items():
            for s in stories:
                tokens = news_engine._tokens(s["title"])
                for g in groups:
                    if g["category"] == cat and news_engine._same_story(g["tokens"], tokens):
                        g["items"].append((day["date"], s)); g["tokens"] |= tokens
                        break
                else:
                    groups.append({"category": cat, "tokens": set(tokens), "items": [(day["date"], s)]})
    stories = []
    for g in groups:
        days = sorted({d for d, _ in g["items"]})
        best = max((s for _, s in g["items"]), key=lambda s: (s["n_sources"], s["published"]))
        max_sources = max(s["n_sources"] for _, s in g["items"])
        official = any(s["official"] for _, s in g["items"])
        stories.append({**best, "official": official, "days_seen": len(days), "first_day": days[0],
                        "last_day": days[-1], "max_sources": max_sources,
                        "week_score": 3 * len(days) + max_sources + (4 if official else 0)})
    return stories


def build_must_know(history):
    """The short list of stories every citizen should know from the last days (see news_config.MUST_KNOW_*)."""
    qualified = [s for s in _merge_stories(history)
                 if s["category"] in cfg.MUST_KNOW_CATEGORIES
                 and (s["official"] or s["max_sources"] >= cfg.MUST_KNOW_MIN_OUTLETS
                      or s["days_seen"] >= cfg.MUST_KNOW_MIN_DAYS)]
    qualified.sort(key=lambda s: -s["week_score"])
    picked, per_cat = [], {}
    for s in qualified:
        if per_cat.get(s["category"], 0) >= cfg.MUST_KNOW_PER_CATEGORY:
            continue
        per_cat[s["category"]] = per_cat.get(s["category"], 0) + 1
        picked.append(s)
        if len(picked) >= cfg.MUST_KNOW_LIMIT:
            break
    return {"from": history[0]["date"] if history else None, "to": history[-1]["date"] if history else None,
            "days_covered": len(history), "stories": picked}


def must_know_text(result, limit=3500):
    if not result["stories"]:
        return "Nothing qualifies as must-know yet. It fills in after the daily news has run for a few days."
    lines = []
    for s in result["stories"]:
        span = f" ({s['days_seen']} days in the news)" if s["days_seen"] > 1 else ""
        lines.append(f"- [{s['category']}] {s['title']}{span}")
    return "\n".join(lines).encode("utf-8")[:limit].decode("utf-8", errors="ignore")
