import sqlite3

def fetch_new(limit: int = 25):
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