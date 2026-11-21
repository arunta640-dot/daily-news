import datetime as dt
import os
import tempfile
import unittest
from unittest.mock import patch

import news_engine as ne
import news_history as nh
import news_ui
import notify
from tests.test_news_engine import NOW, rss, src, when, digest


def story(title, cat="World", n=2, official=False, day="2026-11-20"):
    return {"category": cat, "title": title, "summary": "", "url": "https://a.com/" + title[:4], "lead_source": "A",
            "sources": [{"name": "A", "url": "u"}], "n_sources": n, "official": official,
            "published": day + "T05:00:00+00:00", "score": 10, "confirmation": "x"}


class ExplainedTests(unittest.TestCase):
    def test_explainer_single_source_ok_and_longer_age(self):
        e = src("Explained desk", "e.com", "Explained")
        feeds = {e["url"]: rss(("Why the fuel price formula changes every fortnight", "https://e.com/1", "d", when(70)))}
        d = digest(feeds, [e])
        self.assertEqual(d["sections"]["Explained"][0]["confirmation"], "Explainer")

    def test_explainer_never_leads_page(self):
        e = src("Explained desk", "e.com", "Explained")
        feeds = {e["url"]: rss(("Why the fuel price formula changes every fortnight", "https://e.com/1", "d", when(5)))}
        out = news_ui.page_html(digest(feeds, [e]), NOW)
        self.assertNotIn('class="lead', out)
        self.assertIn("Explainer", out)


class MustKnowTests(unittest.TestCase):
    def test_persistent_story_qualifies_ranks_first_and_merges(self):
        hist = [
            {"date": "2026-11-18", "sections": {"World": [story("Floods hit northern region thousands evacuated", day="2026-11-18"),
                                                          story("Minor trade fair opens in capital city", n=2, day="2026-11-18")]}},
            {"date": "2026-11-19", "sections": {"World": [story("Thousands evacuated as floods hit northern region", day="2026-11-19")]}},
            {"date": "2026-11-20", "sections": {"World": [story("Northern region floods: thousands evacuated again", day="2026-11-20")]}},
        ]
        r = nh.build_must_know(hist)
        self.assertEqual(len(r["stories"]), 1)   # the one-day, 2-outlet trade fair does not qualify
        top = r["stories"][0]
        self.assertEqual((top["days_seen"], top["first_day"], top["last_day"]), (3, "2026-11-18", "2026-11-20"))
        self.assertIn("3 days in the news", nh.must_know_text(r))

    def test_official_or_three_outlets_qualify_on_day_one(self):
        hist = [{"date": "2026-11-20", "sections": {
            "India": [story("Cabinet approves new rail corridor project", cat="India", n=1, official=True)],
            "Health": [story("Clinic network expands rural screening programme", cat="Health", n=3)],
            "World": [story("Two outlet only story about trade talks", n=2)]}}]
        titles = [s["title"] for s in nh.build_must_know(hist)["stories"]]
        self.assertEqual(len(titles), 2)
        self.assertNotIn("Two outlet only story about trade talks", titles)

    def test_only_citizen_categories(self):
        hist = [{"date": "2026-11-20", "sections": {"Sports": [story("Final won by late goal today", cat="Sports", n=5)],
                                                    "Explained": [story("Why fuel prices change often", cat="Explained", n=5)]}}]
        self.assertEqual(nh.build_must_know(hist)["stories"], [])

    def test_per_category_and_total_limits(self):
        words = ["alpha bravo charlie", "delta echo foxtrot", "golf hotel india", "juliet kilo lima", "mike november oscar",
                 "papa quebec romeo", "sierra tango uniform", "victor whiskey xray", "yankee zulu amber", "bronze copper dolphin"]
        hist = [{"date": "2026-11-20", "sections": {"World": [story(w + " news today", n=4) for w in words]}}]
        self.assertEqual(len(nh.build_must_know(hist)["stories"]), 4)

    def test_save_load_and_prune(self):
        with tempfile.TemporaryDirectory() as folder:
            for day in ("2026-09-01", "2026-11-19", "2026-11-20"):
                nh.save_digest({"generated_at": day + "T03:00:00+00:00", "sections": {"World": [story("Some headline words here", day=day)]}},
                               directory=folder)
            self.assertFalse(os.path.exists(os.path.join(folder, "2026-09-01.json")))  # older than 30 days
            days = nh.load_days(folder, days=7, today=dt.date(2026, 11, 20))
            self.assertEqual([d["date"] for d in days], ["2026-11-19", "2026-11-20"])

    def test_damaged_day_is_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, "2026-11-20.json"), "w") as fh:
                fh.write("{broken")
            self.assertEqual(nh.load_days(folder, today=dt.date(2026, 11, 20)), [])

    def test_page_empty_state_and_escaping(self):
        self.assertIn("Nothing qualifies yet", news_ui.must_know_html(nh.build_must_know([])))
        hist = [{"date": "2026-11-20", "sections": {"World": [story("<b>bold</b> headline words here", n=4)]}}]
        html_out = news_ui.must_know_html(nh.build_must_know(hist))
        self.assertNotIn("<b>bold</b>", html_out)
        self.assertIn("4 outlets", html_out)
        self.assertNotIn("reported it", html_out)


class NotifyTests(unittest.TestCase):
    @patch.dict(os.environ, {"NTFY_TOPIC": "t-test", "NEWS_APP_URL": "https://x.example"}, clear=False)
    @patch("notify.urllib.request.urlopen")
    def test_push_builds_request(self, urlopen):
        urlopen.return_value.__enter__.return_value.status = 200
        self.assertTrue(notify.push("Daily News – 21 Nov", "body न"))
        req = urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://ntfy.sh/t-test")
        self.assertEqual(req.get_header("Click"), "https://x.example")
        self.assertEqual(req.data.decode("utf-8"), "body न")

    @patch.dict(os.environ, {"NTFY_TOPIC": ""}, clear=False)
    def test_no_topic_prints_instead(self):
        self.assertFalse(notify.push("t", "b"))


if __name__ == "__main__":
    unittest.main()
