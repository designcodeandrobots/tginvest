# select_new.py
import re
import sqlite3
from collections import defaultdict
from typing import Dict, List, Optional

# Приоритет для новостей про сильные движения цены/котировок
MOVE_PCT_RE = re.compile(r'([+-]?\d{1,3}(?:[.,]\d+)?)\s*%')
MOVE_WORDS = (
    "up", "down", "surge", "surges", "plunge", "plunges", "rally", "selloff",
    "jump", "jumps", "drop", "drops", "soar", "soars", "slump", "slumps",
    "вырос", "выросли", "рост", "растет", "растут", "подскочил", "подскочили",
    "упал", "упали", "падение", "обвал", "обвалился", "обвалилась", "обвалились",
)
MARKET_HINTS = (
    "%", "shares", "stock", "stocks", "equities", "nasdaq", "s&p", "dow",
    "акции", "котировки", "индекс", "биржа", "рынок",
    "btc", "bitcoin", "eth", "ethereum", "crypto", "крипто",
)

def _score_item(it: Dict) -> int:
    """
    Чем выше score, тем вероятнее новость попадёт в батч для OpenAI.
    Приоритет: наличие % + слова про рост/падение + рыночные подсказки.
    """
    title = (it.get("title") or "")
    summ = (it.get("summary") or it.get("snippet") or "")
    text = f"{title} {summ}".lower()

    score = 0

    if MOVE_PCT_RE.search(text):
        score += 200

    if any(w in text for w in MOVE_WORDS):
        score += 60

    if any(h in text for h in MARKET_HINTS):
        score += 30

    # Небольшой бонус, если похоже на тикер (AAPL, INTC, TSLA)
    if re.search(r"\b[A-Z]{2,5}\b", title):
        score += 10

    return score


def fetch_new(
    limit: int = 25,
    per_source: int = 7,
    prefer_sources: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Берём кандидатов из news.status='new' с балансировкой по источникам,
    но при этом приоритизируем новости про сильные движения котировок.

    1) Тянем окно последних new (limit*6 или минимум 150)
    2) Балансируем per_source на источник (опционально сначала prefer_sources)
    3) Внутри каждой группы сортируем по score (движения котировок вверх)
    4) Добираем по score/свежести до limit
    """
    conn = sqlite3.connect("news.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    window = max(limit * 6, 150)
    cur.execute(
        """
        SELECT id, source, title, url, published, summary
        FROM news
        WHERE status='new'
        ORDER BY id DESC
        LIMIT ?
        """,
        (window,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    if not rows:
        return []

    # группируем по источнику
    by_source = defaultdict(list)
    for r in rows:
        by_source[r.get("source", "")].append(r)

    # внутри каждого источника — сортируем по score, затем по свежести
    for src in list(by_source.keys()):
        by_source[src].sort(key=lambda x: (_score_item(x), x["id"]), reverse=True)

    picked: List[Dict] = []
    used_ids = set()

    # 1) приоритетные источники (если заданы)
    if prefer_sources:
        for src in prefer_sources:
            for r in by_source.get(src, [])[:per_source]:
                if r["id"] not in used_ids:
                    picked.append(r)
                    used_ids.add(r["id"])

    # 2) равномерно по всем источникам
    for src, items in sorted(by_source.items(), key=lambda x: x[0].lower()):
        already = sum(1 for p in picked if p.get("source") == src)
        remaining = max(0, per_source - already)
        if remaining <= 0:
            continue
        for r in items[:remaining]:
            if r["id"] not in used_ids:
                picked.append(r)
                used_ids.add(r["id"])

    # 3) добираем до limit: сначала по score, потом по свежести
    # (собираем оставшиеся, сортируем и добираем)
    if len(picked) < limit:
        leftovers = [r for r in rows if r["id"] not in used_ids]
        leftovers.sort(key=lambda x: (_score_item(x), x["id"]), reverse=True)
        for r in leftovers:
            picked.append(r)
            used_ids.add(r["id"])
            if len(picked) >= limit:
                break

    return picked[:limit]