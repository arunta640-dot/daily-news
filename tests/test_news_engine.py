"""Offline tests for the Daily News engine; no network access is used."""
import datetime as dt
import unittest

import news_engine as ne

NOW = dt.datetime(2026, 11, 21, 6, 0, tzinfo=dt.timezone.utc)


def rss(*items):
    body = "".join(
        f"<item><title>{t}</title><link>{l}</link><description>{d}</description>"
        f"<pubDate>{p}</pubDate></item>" for t, l, d, p in items)
    return f"<rss><channel>{body}</channel></rss>".encode()


def when(hours_ago):
    return (NOW - dt.timedelta(hours=hours_ago)).strftime("%a, %d %b %Y %H:%M:%S +0000")


def src(name, domain, cat="World", tier="major", **kw):
    return {"name": name, "url": f"https://{domain}/feed", "domains": (domain,),
            "category": cat, "tier": tier, **kw}


def digest(feeds, sources):
    return ne.build_digest(now=NOW, fetch=lambda url: feeds[url], sources=sources)


class EngineTests(unittest.TestCase):
    def test_story_needs_two_outlets_unless_relaxed(self):
        a, b = src("A", "a.com"), src("B", "b.com")
        feeds = {
            a["url"]: rss(("Floods hit northern region, thousands evacuated", "https://a.com/1", "d", when(2)),
                          ("Lone rumour about minister resigning today", "https://a.com/2", "d", when(2))),
            b["url"]: rss(("Thousands evacuated as floods hit northern region", "https://b.com/9", "d", when(3))),
        }
        d = digest(feeds, [a, b])
        titles = [s["title"] for s in d["sections"]["World"]]
        self.assertEqual(len(titles), 1)
        self.assertIn("floods", titles[0].lower())
        self.assertEqual(d["sections"]["World"][0]["n_sources"], 2)
        self.assertEqual(d["unconfirmed_dropped"], 1)

    def test_same_outlet_two_feeds_counts_once(self):
        a1, a2 = src("A World", "a.com"), src("A Also", "a.com")
        item = ("Government announces new road safety law nationwide", "https://a.com/x", "d", when(1))
        d = digest({a1["url"]: rss(item), a2["url"]: rss(item)}, [a1, a2])
        self.assertEqual(d["total_stories"], 0)

    def test_official_source_passes_alone(self):
        pib = src("PIB", "pib.gov.in", "India", "official")
        feeds = {pib["url"]: rss(("Cabinet approves new rail corridor project", "https://pib.gov.in/1", "d", when(4)))}
        d = digest(feeds, [pib])
        self.assertEqual(d["sections"]["India"][0]["confirmation"], "Official source")

    def test_relaxed_category_allows_single_source(self):
        h = src("Health desk", "h.com", "Health")
        feeds = {h["url"]: rss(("New vaccine guidance published for adults", "https://h.com/1", "d", when(5)))}
        self.assertEqual(digest(feeds, [h])["total_stories"], 1)

    def test_off_domain_links_are_rejected(self):
        a = src("A", "a.com", "Health")
        feeds = {a["url"]: rss(("Hospital opens new wing for children", "https://evil.example/redirect?u=a.com", "d", when(1)))}
        d = digest(feeds, [a])
        self.assertEqual(d["total_stories"], 0)
        self.assertEqual(d["source_report"]["A [Health]"]["off_domain"], 1)

    def test_stale_and_undated_dropped(self):
        a = src("A", "a.com", "Health")
        feeds = {a["url"]: rss(("Old health story from two days ago", "https://a.com/1", "d", when(60)),
                               ("Undated health story with no timestamp", "https://a.com/2", "d", ""))}
        d = digest(feeds, [a])
        self.assertEqual(d["total_stories"], 0)
        self.assertEqual(d["source_report"]["A [Health]"]["stale_or_undated"], 2)

    def test_unwanted_topics_filtered(self):
        a = src("A", "a.com", "Health")
        feeds = {a["url"]: rss(
            ("Celebrity wedding photos go viral", "https://a.com/1", "d", when(1)),
            ("Top stock picks: multibagger shares to buy", "https://a.com/2", "d", when(1)),
            ("Weekly horoscope for all signs", "https://a.com/3", "d", when(1)),
            ("Why this opinion piece matters", "https://a.com/opinion/4", "d", when(1)),
            ("Clinic network expands rural screening programme", "https://a.com/5", "d", when(1)))}
        d = digest(feeds, [a])
        self.assertEqual([s["title"] for s in d["sections"]["Health"]],
                         ["Clinic network expands rural screening programme"])
        self.assertEqual(d["source_report"]["A [Health]"]["unwanted"], 4)

    def test_keyword_scoped_feed(self):
        g = src("Gulf feed", "a.com", "Bahrain & Gulf", keywords=("bahrain", "gulf"))
        feeds = {g["url"]: rss(("Bahrain opens new causeway lane", "https://a.com/1", "d", when(1)),
                               ("Parliament debates budget in Europe", "https://a.com/2", "d", when(1)))}
        d = digest(feeds, [g])
        self.assertEqual(d["total_stories"], 1)

    def test_broken_feed_does_not_stop_others(self):
        a, b = src("A", "a.com", "Health"), src("B", "b.com", "Science")
        def fetch(url):
            if url == a["url"]:
                raise TimeoutError("timed out")
            return rss(("Telescope spots distant galaxy cluster", "https://b.com/1", "d", when(2)))
        d = ne.build_digest(now=NOW, fetch=fetch, sources=[a, b])
        self.assertEqual(d["feeds_ok"], 1)
        self.assertEqual(d["total_stories"], 1)
        self.assertIn("TimeoutError", d["source_report"]["A [Health]"]["error"])

    def test_atom_feed_and_text_output(self):
        a = src("A", "a.com", "Health")
        atom = ("<feed xmlns='http://www.w3.org/2005/Atom'><entry><title>Atom health item here today</title>"
                "<link href='https://a.com/atom1'/><summary>&lt;p&gt;Short&lt;/p&gt;</summary>"
                f"<updated>{(NOW - dt.timedelta(hours=1)).isoformat()}</updated></entry></feed>").encode()
        d = digest({a["url"]: atom}, [a])
        self.assertEqual(d["sections"]["Health"][0]["summary"], "Short")
        text = ne.to_text(d)
        self.assertIn("Atom health item here today", text)
        self.assertIn("Sources working: 1/1", text)


if __name__ == "__main__":
    unittest.main()
