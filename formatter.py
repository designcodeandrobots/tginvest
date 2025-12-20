from emoji import emoji_for_tag

CHANNEL_USERNAME = "investnewsbottoday"

def format_post(item: dict) -> str:
    """
    Формат:
    #тег@channel
    📰 Новость <a href="url">–Источник</a>
    """

    raw_tags = item.get("tags") or ""
    tag = raw_tags.split(",")[0].strip().lower() if raw_tags else "новости"
    hashtag = f"#{tag.replace(' ', '_')}@{CHANNEL_USERNAME}"

    emoji = emoji_for_tag(tag)

    text = item.get("headline_ru") or item.get("summary_ru") or ""
    source = item.get("source", "Источник")
    url = item.get("url", "")
    source_link = f'<a href="{url}">–{source}</a>'

    # ⬇⬇⬇ ВАЖНО: меняем порядок строк
    return (
        f"{hashtag}\n"
        f"{emoji} {text} {source_link}"
    )