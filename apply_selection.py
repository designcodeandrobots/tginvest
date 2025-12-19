# apply_selection.py
import json
import sqlite3

def apply_selected(selected: list[dict]):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    for s in selected:
        tags = s.get("tags", [])
        if isinstance(tags, list):
            tags = ",".join(tags)

        cur.execute("""
            UPDATE news
            SET status='selected', headline_ru=?, summary_ru=?, tags=?
            WHERE id=?
        """, (s.get("headline_ru",""), s.get("summary_ru",""), tags, s["id"]))

    conn.commit()
    conn.close()

def main():
    # для ручного теста: python apply_selection.py out.json
    import sys
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    apply_selected(data["selected"])
    print("Applied:", len(data["selected"]))

if __name__ == "__main__":
    main()