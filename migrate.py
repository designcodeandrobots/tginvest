# migrate.py
import sqlite3

def add_column_if_missing(cur, table, col, coltype):
    cur.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cur.fetchall()}
    if col not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")

def main():
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    add_column_if_missing(cur, "news", "headline_ru", "TEXT")
    add_column_if_missing(cur, "news", "summary_ru", "TEXT")
    add_column_if_missing(cur, "news", "tags", "TEXT")

    conn.commit()
    conn.close()
    print("Migration OK")

if __name__ == "__main__":
    main()