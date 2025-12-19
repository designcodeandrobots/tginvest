# storage.py
from db import get_conn

def save_news(items: list[dict]) -> int:
    conn = get_conn()
    cur = conn.cursor()
    saved = 0

    for item in items:
        try:
            cur.execute("""
                INSERT INTO news (source, title, url, published, summary)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item["source"],
                item["title"],
                item["url"],
                item["published"],
                item["summary"],
            ))
            saved += 1
        except Exception:
            # дубликат
            pass

    conn.commit()
    conn.close()
    return saved