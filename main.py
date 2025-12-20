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
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Bot
from telegram.error import TimedOut, NetworkError
from telegram.request import HTTPXRequest


def load_cfg():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources():
    with open("sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]


async def post_selected(cfg: dict, limit: int) -> int:
    # Telegram timeouts (важно, чтобы не висело)
    request = HTTPXRequest(
        connection_pool_size=4,
        connect_timeout=20,
        read_timeout=40,
        write_timeout=40,
    )

    bot = Bot(token=cfg["telegram"]["token"], request=request)
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

        sent = False
        for attempt in range(3):  # 3 попытки
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="HTML",  # нужно для <a href="..."> и <b>
                    disable_web_page_preview=True,
                    disable_notification=True,
                )
                sent = True
                break
            except (TimedOut, NetworkError) as e:
                # 2s, 4s пауза; после 3-й попытки — сдаёмся до следующего запуска
                if attempt < 2:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                print(f"Telegram send failed (will retry next run): {type(e).__name__}: {e}")

        if not sent:
            # Не падаем. Оставляем status='selected', чтобы в следующий запуск отправить снова.
            continue

        cur.execute("UPDATE news SET status='posted' WHERE id=?", (item["id"],))
        posted += 1
        print("Posted:", item.get("headline_ru") or item.get("summary_ru") or item["id"])

    conn.commit()
    conn.close()
    return posted


async def main():
    now_msk = datetime.now(ZoneInfo("Europe/Moscow"))
    if not (7 <= now_msk.hour < 24):
        print(f"Outside work hours MSK ({now_msk:%Y-%m-%d %H:%M}), exiting.")
        return

    cfg = load_cfg()
    init_db()

    # 1) RSS -> SQLite
    sources = load_sources()
    total_saved = 0
    for src in sources:
        items = fetch_rss(src["name"], src["url"], timeout=10, max_entries=30)
        saved = save_news(items)
        total_saved += saved
        print(f"{src['name']}: +{saved}")

    print("Saved new items:", total_saved)

    # 2) new -> selected (OpenAI)
    openai_cfg = cfg.get("openai", {})
    max_batch = int(openai_cfg.get("max_items_in_batch", 25))
    new_items = fetch_new(limit=max_batch)
    print("Fetched new for OpenAI:", len(new_items))

    if new_items:
        data = summarize_items(cfg, new_items)
        selected = data.get("selected", [])
        print("Selected:", len(selected))
        if selected:
            apply_selected(selected)

    # 3) selected -> posted (Telegram)
    post_limit = int(cfg.get("telegram", {}).get("post_limit", 1))
    await post_selected(cfg, limit=post_limit)


if __name__ == "__main__":
    try:
        asyncio.run(asyncio.wait_for(main(), timeout=480))
    except asyncio.TimeoutError:
        print("❌ Main timeout: execution took too long")