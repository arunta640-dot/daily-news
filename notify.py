"""Push a notification to your phone through ntfy (https://ntfy.sh)."""
import os
import urllib.request


def push(title, body, click=None, tags="newspaper"):
    """Send `body` to your ntfy topic. Returns False (and prints the text) if NTFY_TOPIC is not set."""
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        print(title + "\n\n" + body + "\n\n(NTFY_TOPIC not set: printed instead of sent.)")
        return False
    server = os.environ.get("NTFY_SERVER", "").strip().rstrip("/") or "https://ntfy.sh"
    headers = {"Title": title.encode("ascii", "ignore").decode(), "Tags": tags, "Priority": "default"}
    click = click or os.environ.get("NEWS_APP_URL", "").strip()
    if click:
        headers["Click"] = click
    if os.environ.get("NTFY_TOKEN", "").strip():
        headers["Authorization"] = "Bearer " + os.environ["NTFY_TOKEN"].strip()
    req = urllib.request.Request(f"{server}/{topic}", data=body.encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("ntfy:", resp.status)
    return True
