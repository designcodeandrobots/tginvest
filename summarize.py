import json
from openai import OpenAI

SYSTEM = """Ты — строгий редактор финансовых новостей для Telegram.

Цель: выбрать самые важные новости и выдать короткие русские заголовки.

Правила:
- Не выдумывай факты. Используй только title/snippet.
- headline_ru: одна строка, до ~140 символов.
- headline_ru ДОЛЖЕН начинаться с одного подходящего эмодзи и пробела.
- ВАЖНО: в headline_ru ОБЯЗАТЕЛЬНО должна быть ОДНА HTML-ссылка
  вида <a href="URL">слово</a>.
  - URL бери из поля url соответствующей новости.
  - Ссылку вставляй ВНУТРЬ предложения, на глаголе или ключевом слове
    (например: "побили", "выросли", "обвалились", "заявил", "покупает").
  - Только один тег <a>, без вложенности.
- Можно использовать <b>...</b> для выделения компаний/активов.
- Никаких других HTML-тегов.
- tags: 1–2 коротких тега в нижнем регистре (например: "рынки", "крипто", "макро").

ВЫВОД:
- Верни СТРОГО валидный JSON без любого текста вокруг.

Формат:
{
  "selected": [
    {
      "id": 123,
      "headline_ru": "📈 ... <a href=\\"URL\\">...</a> ...",
      "summary_ru": "...",
      "tags": ["..."]
    }
  ]
}
"""

def build_prompt(items, pick_top: int):
    compact = []
    for it in items:
        compact.append({
            "id": it["id"],
            "source": it.get("source", ""),
            "title": (it.get("title") or "")[:200],
            "published": (it.get("published") or "")[:50],
            "url": it.get("url", ""),
            "snippet": (it.get("summary") or "")[:500],
        })

    schema = {
        "selected": [
            {
                "id": 123,
                "emoji": "📰",
                "headline_ru": "…",
                "summary_ru": "…",
                "tags": ["рынки", "макро"]
            }
        ]
    }

    user = {
        "task": f"Выбери топ-{pick_top} новостей.",
        "items": compact,
        "output_schema_example": schema
    }
    return json.dumps(user, ensure_ascii=False)

def summarize_items(cfg: dict, items: list[dict]):
    if not items:
        return {"selected": []}

    openai_cfg = cfg.get("openai", {})
    api_key = openai_cfg.get("api_key")
    if not api_key:
        raise ValueError("Missing openai.api_key in config.yaml")

    client = OpenAI(api_key=api_key, timeout=30.0)
    model = openai_cfg.get("model", "gpt-4.1-mini")
    pick_top = int(openai_cfg.get("pick_top", 1))

    prompt = build_prompt(items, pick_top)

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    text = (resp.output_text or "").strip()
    if not text:
        return {"selected": []}

    return json.loads(text)