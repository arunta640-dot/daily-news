import datetime as dt
import unittest

import news_ui

NOW = dt.datetime(2026, 11, 21, 5, 0, tzinfo=dt.timezone.utc)


def story(title, **kw):
    base = {"category": "World", "title": title, "summary": "", "url": "https://a.com/1", "lead_source": "A",
            "sources": [{"name": "A", "url": "u"}, {"name": "B", "url": "u"}], "n_sources": 2, "official": False,
            "published": (NOW - dt.timedelta(hours=2)).isoformat(), "score": 20}
    return {**base, **kw}


class UITests(unittest.TestCase):
    def test_text_from_feeds_is_escaped(self):
        d = {"sections": {"World": [story("<script>alert(1)</script> & more", summary='"><img src=x onerror=1>')]},
             "total_stories": 1, "unconfirmed_dropped": 0, "feeds_ok": 1, "feeds_total": 1}
        out = news_ui.page_html(d, NOW)
        self.assertNotIn("<script>", out)
        self.assertNotIn("<img", out)
        self.assertIn("&lt;script&gt;", out)

    def test_empty_digest_shows_guidance(self):
        d = {"sections": {}, "total_stories": 0, "unconfirmed_dropped": 0, "feeds_ok": 0, "feeds_total": 5}
        self.assertIn("No confirmed stories right now", news_ui.page_html(d, NOW))

    def test_no_indented_html_that_markdown_could_treat_as_code(self):
        d = {"sections": {"World": [story("Headline here")]}, "total_stories": 1, "unconfirmed_dropped": 0,
             "feeds_ok": 1, "feeds_total": 1}
        self.assertNotIn("\n", news_ui.page_html(d, NOW))

    def test_ago(self):
        self.assertEqual(news_ui.ago((NOW - dt.timedelta(minutes=5)).isoformat(), NOW), "5 min ago")
        self.assertEqual(news_ui.ago((NOW - dt.timedelta(hours=3)).isoformat(), NOW), "3 h ago")


if __name__ == "__main__":
    unittest.main()
