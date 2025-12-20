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
                item.get("source", ""),
                item.get("title", ""),
                item.get("url", ""),
                item.get("published", ""),
                item.get("summary", ""),
            ))
            saved += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return saved