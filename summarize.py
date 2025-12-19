# summarize.py
import json
from openai import OpenAI

SYSTEM = """Ты — строгий редактор финансовых новостей для Telegram.

Цель: выбрать самые важные новости и выдать короткие русские заголовки.

ОБЯЗАТЕЛЬНОЕ ФОРМАТИРОВАНИЕ (СТРОГО):
- Используй ТОЛЬКО HTML-тег <b>...</b> для выделения.
- В каждом headline_ru:
  - Выдели <b>каждое</b> название компании/организации/актива/тикера, которое присутствует в тексте (например: Apple, FedEx, Nike, Solana, Bitcoin, Goldman Sachs, Citadel, S&P 500).
  - Выдели <b>каждую</b> ключевую цифру/значение: суммы ($, €, ₽), проценты, уровни индексов, ставки, годы (например: 2025), числа с млн/млрд/тыс, диапазоны.
- Если в headline_ru нет ни одной компании/актива — добавь (если это очевидно из title/snippet) и выдели жирным.
- Если в headline_ru нет чисел, но они есть в title/snippet — добавь самое важное число и выдели жирным.
- Если чисел в исходных данных нет — ок, но компании/активы выделить всё равно обязательно.
- НИКАКИХ других тегов, markdown, скобок типа **...**.

КАЧЕСТВО:
- Не выдумывай факты. Используй только title/snippet.
- Без кликбейта. 1 строка, до 120 символов желательно.

ВЫВОД:
- Верни СТРОГО валидный JSON без любого текста вокруг.
"""

def build_prompt(items, pick_top: int):
    # Сильно не раздуваем вход: title + краткий snippet
    compact = []
    for it in items:
        compact.append({
            "id": it["id"],
            "source": it["source"],
            "title": (it["title"] or "")[:200],
            "published": it.get("published", "")[:50],
            "url": it["url"],
            "snippet": (it.get("summary", "") or "")[:500],
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
    client = OpenAI(api_key=cfg["openai"]["api_key"])
    model = cfg["openai"].get("model", "gpt-4.1-mini")
    pick_top = int(cfg["openai"].get("pick_top", 7))

    prompt = build_prompt(items, pick_top)

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    text = resp.output_text.strip()
    data = json.loads(text)
    
    return data