"""Daily news digest -> phone notification (ntfy) or terminal.

  python daily_news.py --print          # show the digest in the terminal
  python daily_news.py                  # push to your phone via ntfy
  python daily_news.py --save           # also keep today's digest for the weekly review

Environment variables: NTFY_TOPIC (required to send), NTFY_SERVER, NTFY_TOKEN, NEWS_APP_URL.
"""
import argparse
import datetime as dt
import json

import news_engine
import news_history
import notify

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()
    digest = news_engine.build_digest()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(digest, fh, ensure_ascii=False, indent=2)
    if args.save and digest["total_stories"]:
        news_history.save_digest(digest)
    if args.print:
        print(news_engine.to_text(digest))
    else:
        local = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=3)
        notify.push(f"Daily News {local:%d %b}", news_engine.to_notification(digest))
