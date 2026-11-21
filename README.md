# Daily News

Everyday news (India, Bahrain & Gulf, World, Economy, Health, Technology, Science, Sports) from a whitelist of established outlets, delivered as a phone notification and a simple web page. No investing features, no Instagram, no Telegram.

## How it works
- Reads only the feeds in `news_config.py`; links must be on the outlet's own domain.
- A story is shown only when 2+ different outlets report it, or an official source does (Health, Technology, Science, Sports and Bahrain & Gulf accept 1 reputable outlet and say so).
- Drops gossip, viral, horoscope, opinion, gallery/video pages and stock-tip chatter. Edit the lists or mute categories in `news_config.py`.
- No AI: headlines and summaries are the outlets' own text.

## Phone notifications (ntfy, free, no account)
1. Install the **ntfy** app (Android: Play Store; iPhone: App Store).
2. In the app tap **+**, subscribe to a topic with a long random name, e.g. `news-k7p2x9qv4m8d` (anyone who knows the name can read it, so keep it private and hard to guess).
3. In GitHub: **Settings > Secrets and variables > Actions**, add secret `NTFY_TOPIC` with that name. Optional: `NEWS_APP_URL` (your Streamlit app link, opened when you tap the notification).
4. **Actions > Daily news > Run workflow** to test. After that it runs every day at 06:00 Bahrain time.

GitHub may delay scheduled runs by some minutes. To change the time, edit the `cron` line (it is in UTC; Bahrain is UTC+3).

## Must know (catch up on the last 7 days)
The first tab, **Must know**, is for days you forgot to read. It shows one short list (max 10 stories) of what every citizen should know from the last 7 days, most important first.
- Only India, Bahrain & Gulf, World, Economy and Health are considered (see `MUST_KNOW_*` in `news_config.py`).
- A story qualifies if an official source reported it, 3+ outlets reported it, or it stayed in the news 2+ days. No more than 4 per category.
- The daily workflow saves each day's stories in `news_history/`; the tab merges the last 7 days plus today's live news. It works from day one using today's news, and gets better as days are saved.
- A **Must-know this week** notification arrives every Friday at 06:30 Bahrain time (`weekly_news.yml`).
- In GitHub, set **Settings > Actions > General > Workflow permissions** to *Read and write* so the daily run can save its history.

The **Today** tab has all categories, including the **Explained** section (background articles from Indian Express Explained, The Conversation and The Guardian Long Read, marked "Explainer").

## Web page
Mobile-first reader: one top story, category chips, a coloured line per category, and dots showing how many outlets reported each story (a tick for official sources). Look and feel lives in `news_ui.py`; colours are at the top of its CSS. It follows your phone's light or dark mode.

Deploy `app.py` on Streamlit Community Cloud, or run `pip install -r requirements.txt && streamlit run app.py`. The page is public news only, with no personal data.

## Terminal
`python daily_news.py --print` (today) and `python weekly_news.py --print` (must-know list)

## Check the feeds
Open *Sources and filter report* in the app after the first run. A feed showing an error needs its URL fixed in `news_config.py`.

## Tests
`python -m unittest discover -s tests -v` (offline)
