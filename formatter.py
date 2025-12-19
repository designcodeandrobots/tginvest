# formatter.py
from emoji import emoji_for_tag

def format_post(item: dict) -> str:
    """
    Формат:
    #тег
    🤝 Новость <a href="url">–Источник</a>
    """

    raw_tags = item.get("tags") or ""
    tag = raw_tags.split(",")[0].strip().lower() if raw_tags else "новости"
    hashtag = f"#{tag.replace(' ', '_')}"

    emoji = emoji_for_tag(tag)

    # ❗ НЕ ЭКРАНИРУЕМ
    text = item.get("headline_ru") or item.get("summary_ru") or ""

    source = item.get("source", "Источник")
    url = item.get("url", "")

    source_link = f'<a href="{url}">–{source}</a>'

    return f"{hashtag}\n{emoji} {text} {source_link}"