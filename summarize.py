import json
from openai import OpenAI

SYSTEM = """Ты — строгий редактор финансовых новостей для Telegram.

Цель: выбрать самые важные новости и выдать короткие русские заголовки.

Правила:
- Не выдумывай факты. Используй только title/snippet.
- Верни СТРОГО валидный JSON без любого текста вокруг.

Формат:
{
  "selected": [
    {"id": 123, "headline_ru": "...", "summary_ru": "...", "tags": ["..."]}
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