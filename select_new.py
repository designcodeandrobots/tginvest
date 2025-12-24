# select_new.py
import sqlite3
from collections import defaultdict
from typing import List, Dict, Optional

def fetch_new(limit: int = 25, per_source: int = 7, prefer_sources: Optional[List[str]] = None) -> List[Dict]:
    """
    Берём до per_source новостей на источник, затем добираем до limit по свежести.
    prefer_sources: если задано, сначала набираем из этих источников.
    """
    conn = sqlite3.connect("news.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Берём чуть больше, чтобы было из чего балансировать
    cur.execute("""
        SELECT id, source, title, url, published, summary
        FROM news
        WHERE status='new'
        ORDER BY id DESC
        LIMIT ?
    """, (max(limit * 6, 150),))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    by_source = defaultdict(list)
    for r in rows:
        by_source[r["source"]].append(r)

    picked = []
    used_ids = set()

    # 1) приоритетные источники (если нужно)
    if prefer_sources:
        for src in prefer_sources:
            for r in by_source.get(src, [])[:per_source]:
                if r["id"] not in used_ids:
                    picked.append(r)
                    used_ids.add(r["id"])

    # 2) равномерно по всем источникам
    for src, items in sorted(by_source.items(), key=lambda x: x[0].lower()):
        take = per_source
        # если мы уже брали из prefer_sources, то тут не перебираем
        already = sum(1 for p in picked if p["source"] == src)
        remaining = max(0, take - already)
        for r in items[:remaining]:
            if r["id"] not in used_ids:
                picked.append(r)
                used_ids.add(r["id"])

    # 3) добираем по свежести до limit
    if len(picked) < limit:
        for r in rows:
            if r["id"] not in used_ids:
                picked.append(r)
                used_ids.add(r["id"])
            if len(picked) >= limit:
                break

    # финально: оставляем только limit
    return picked[:limit]