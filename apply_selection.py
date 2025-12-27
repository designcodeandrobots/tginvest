# apply_selection.py
import sqlite3


def _normalize_tags(tags) -> str:
    if tags is None:
        return ""
    if isinstance(tags, list):
        return ",".join([str(t).strip() for t in tags if str(t).strip()])
    if isinstance(tags, str):
        # на случай если модель вернула "рынки, макро"
        return ",".join([t.strip() for t in tags.split(",") if t.strip()])
    return ""


def apply_selected(selected: list[dict]):
    """
    selected items shape (expected):
      {
        "id": int,
        "headline_ru": str,
        "summary_ru": str,
        "tags": list[str] | str,
        "ai_opinion_ru": str (optional)   <-- добавляем в summary_ru
      }

    Мы НЕ меняем схему БД. Если ai_opinion_ru есть, добавляем в конец summary_ru:
      💬 Мнение AI: ...
    """
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    for s in selected:
        if "id" not in s:
            continue

        tags_str = _normalize_tags(s.get("tags"))

        headline = (s.get("headline_ru") or "").strip()

        summary = (s.get("summary_ru") or "").strip()
        opinion = (s.get("ai_opinion_ru") or "").strip()

        if opinion:
            # добавляем opinion отдельной строкой
            opinion_line = f"💬 Мнение AI: {opinion}"
            summary = f"{summary}\n{opinion_line}" if summary else opinion_line

        cur.execute(
            """
            UPDATE news
            SET status='selected',
                headline_ru=?,
                summary_ru=?,
                tags=?
            WHERE id=?
            """,
            (headline, summary, tags_str, s["id"]),
        )

    conn.commit()
    conn.close()