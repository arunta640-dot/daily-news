"""Must-know review of the last 7 days -> phone notification (ntfy) or terminal.
python weekly_news.py [--print]"""
import argparse
import datetime as dt

import news_history
import notify

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", action="store_true")
    args = ap.parse_args()
    result = news_history.build_must_know(news_history.load_days(days=7))
    text = news_history.must_know_text(result)
    if args.print:
        print(text)
    else:
        local = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=3)
        notify.push(f"Must-know this week ({local:%d %b})", text)
