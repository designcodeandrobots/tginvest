# select_new.py
import sqlite3

def fetch_new(limit: int = 80):
    conn = sqlite3.connect("news.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, source, title, url, published, summary
        FROM news
        WHERE status='new'
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    items = fetch_new()
    print("new:", len(items))
    for it in items[:5]:
        print("-", it["title"])