# rss.py
import feedparser

def fetch_rss(source_name: str, url: str) -> list[dict]:
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries:
        items.append({
            "source": source_name,
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", "")[:1000],
        })

    return items