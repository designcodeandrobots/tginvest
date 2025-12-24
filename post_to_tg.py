# post_to_tg.py
import asyncio
import sqlite3
import yaml
from telegram import Bot
from formatter import format_post
from select_selected import fetch_selected

async def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    bot = Bot(token=cfg["telegram"]["token"])
    chat_id = cfg["telegram"]["chat_id"]

    items = fetch_selected(limit=5)
    if not items:
        print("Нет selected новостей")
        return

    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    for item in items:
        text = format_post(item)

        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",              
            disable_web_page_preview=True,
            disable_notification=True,
        )

        cur.execute(
            "UPDATE news SET status='posted' WHERE id=?",
            (item["id"],)
        )

        print("Posted:", item["headline_ru"])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    asyncio.run(main())