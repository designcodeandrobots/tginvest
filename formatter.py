import re

META_MARK = '<i>*принадлежит Meta, признана экстремистской на территории РФ.</i>'

META_KEYWORDS = [
    r'\bmeta\b',
    r'\bfacebook\b',
    r'\binstagram\b',
    r'\bwhatsapp\b',
    r'\bzuckerberg\b',
    r'цукерберг',
]

def has_meta_mention(text: str) -> bool:
    text_l = text.lower()
    return any(re.search(k, text_l) for k in META_KEYWORDS)


def format_post(item: dict) -> str:
    raw_tags = item.get("tags") or ""
    tag = raw_tags.split(",")[0].strip().lower() if raw_tags else "новости"
    hashtag = f"#{tag.replace(' ', '_')}"

    # headline_ru уже содержит эмодзи + <a href="...">
    text = (item.get("headline_ru") or "").strip()

    post = f"{text} {hashtag}"

    # 👇 добавляем маркировку при необходимости
    if has_meta_mention(text):
        post = f"{post}\n{META_MARK}"

    return post