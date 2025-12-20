import sqlite3

def fetch_selected(limit: int = 1):
    conn = sqlite3.connect("news.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT id, headline_ru, summary_ru, tags, source, url
        FROM news
        WHERE status='selected'
        ORDER BY id ASC
        LIMIT ?
    """, (limit,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows