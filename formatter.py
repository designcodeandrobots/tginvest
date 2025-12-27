import re

META_MARK = '<i>*принадлежит Meta, признана экстремистской на территории РФ.</i>'

META_PATTERNS = [
    r"\bmeta\b",
    r"\bfacebook\b",
    r"\binstagram\b",
    r"\bwhatsapp\b",
    r"\bzuckerberg\b",
    r"цукерберг",
]

OPINION_TAGS = {"акции", "рынки", "крипто", "сделки"}

MOVE_RE = re.compile(
    r"(\+\d+%|-\d+%|вырос|упал|подскочил|обвалился|снизил(ся|ись)|рост|падени)",
    re.IGNORECASE
)

def _has_meta_mention(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in META_PATTERNS)

def _allow_opinion(tag: str, headline: str) -> bool:
    if tag not in OPINION_TAGS:
        return False
    return bool(MOVE_RE.search(headline or ""))

def format_post(item: dict) -> str:
    raw_tags = item.get("tags") or ""
    tag = raw_tags.split(",")[0].strip().lower() if raw_tags else "новости"
    hashtag = f"#{tag.replace(' ', '_')}"

    headline = (item.get("headline_ru") or "").strip()

    # ✅ выводим ТОЛЬКО opinion-строку, но НЕ summary
    opinion_block = ""
    summary_ru = (item.get("summary_ru") or "").strip()
    if summary_ru.startswith("💬 Мнение AI:") and _allow_opinion(tag, headline):
        opinion_block = summary_ru

    post = f"{headline} {hashtag}"
    if opinion_block:
        post = f"{post}\n{opinion_block}"

    if _has_meta_mention(post):
        post = f"{post}\n{META_MARK}"

    return post