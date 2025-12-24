# formatter.py

def format_post(item: dict) -> str:
    # тег
    raw_tags = item.get("tags") or ""
    tag = raw_tags.split(",")[0].strip().lower() if raw_tags else "новости"
    hashtag = f"#{tag.replace(' ', '_')}"

    # текст (OpenAI уже добавляет эмодзи в начале headline_ru)
    text = (item.get("headline_ru") or item.get("summary_ru") or "").strip()

    # на всякий случай: если в конце нет точки — добавим
    if text and text[-1] not in ".!?…":
        text += "."

    # одинлайн формат
    return f"{text} {hashtag}"