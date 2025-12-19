import asyncio
import sqlite3
import yaml

from db import init_db
from rss import fetch_rss
from storage import save_news
from select_new import fetch_new
from summarize import summarize_items
from apply_selection import apply_selected
from select_selected import fetch_selected
from formatter import format_post

from telegram import Bot


def load_cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources():
    with open("sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]


def mark_new_as_skipped(ids: list[int]):
    if not ids:
        return
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.executemany("UPDATE news SET status='skipped' WHERE id=?", [(i,) for i in ids])
    conn.commit()
    conn.close()


async def post_selected(cfg: dict, limit: int) -> int:
    bot = Bot(token=cfg["telegram"]["token"])
    chat_id = cfg["telegram"]["chat_id"]

    items = fetch_selected(limit=limit)
    if not items:
        print("Нет selected новостей для постинга")
        return 0

    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    posted = 0
    for item in items:
        text = format_post(item)

        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",  # важно для <b> и <a>
            disable_web_page_preview=True,
        )

        cur.execute("UPDATE news SET status='posted' WHERE id=?", (item["id"],))
        posted += 1
        print("Posted:", item.get("headline_ru") or item.get("summary_ru") or item["id"])

    conn.commit()
    conn.close()
    return posted


async def main():
    cfg = load_cfg()
    init_db()

    # --- 1) RSS -> SQLite ---
    sources = load_sources()
    total_saved = 0
    for src in sources:
        items = fetch_rss(src["name"], src["url"])
        saved = save_news(items)
        total_saved += saved
        print(f"{src['name']}: +{saved}")

    print("Saved new items:", total_saved)

    # --- 2) new -> selected (через OpenAI) ---
    openai_cfg = cfg.get("openai", {})
    max_batch = int(openai_cfg.get("max_items_in_batch", 25))
    pick_top = int(openai_cfg.get("pick_top", 5))

    new_items = fetch_new(limit=max_batch)
    print("Fetched new for OpenAI:", len(new_items))

    if new_items:
        data = summarize_items(cfg, new_items)
        selected = data.get("selected", [])
        print("Selected:", len(selected))

        if selected:
            apply_selected(selected)

            # (опционально) чтобы “не крутить” одни и те же new снова и снова:
            selected_ids = {s["id"] for s in selected if "id" in s}
            leftovers = [it["id"] for it in new_items if it["id"] not in selected_ids]
            # Можно либо оставить их new, либо пометить skipped.
            # Я рекомендую skipped, чтобы не гонять снова в тестах.
            mark_new_as_skipped(leftovers)
        else:
            print("OpenAI ничего не выбрал — оставляем new как есть")
    else:
        print("Нет new новостей для OpenAI")

    # --- 3) selected -> posted (Telegram) ---
    post_limit = int(cfg.get("telegram", {}).get("post_limit", pick_top))
    await post_selected(cfg, limit=post_limit)


if __name__ == "__main__":
    asyncio.run(main())