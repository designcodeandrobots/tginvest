# rss.py
import feedparser
import socket

def fetch_rss(source_name: str, url: str, timeout: int = 10, max_entries: int = 30) -> list[dict]:
    socket.setdefaulttimeout(timeout)

    feed = feedparser.parse(url)
    items = []

    entries = getattr(feed, "entries", [])[:max_entries]  # <-- лимит!
    for entry in entries:
        items.append({
            "source": source_name,
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", "")[:1000],
        })

    return items