import sqlite3

def apply_selected(selected: list[dict]):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    for s in selected:
        tags = s.get("tags", [])
        if isinstance(tags, list):
            tags = ",".join([t.strip() for t in tags if t and str(t).strip()])
        elif tags is None:
            tags = ""

        cur.execute("""
            UPDATE news
            SET status='selected', headline_ru=?, summary_ru=?, tags=?
            WHERE id=?
        """, (
            s.get("headline_ru", ""),
            s.get("summary_ru", ""),
            tags,
            s["id"],
        ))

    conn.commit()
    conn.close()