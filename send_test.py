import asyncio
import yaml
from telegram import Bot

async def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    token = cfg["telegram"]["token"]
    chat_id = cfg["telegram"]["chat_id"]
    parse_mode = cfg.get("app", {}).get("parse_mode", "HTML")

    bot = Bot(token=token)

    await bot.send_message(
        chat_id=chat_id,
        text="✅ Тест из Python: бот постит в канал",
        parse_mode=parse_mode,
        disable_web_page_preview=True,
    )

if __name__ == "__main__":
    asyncio.run(main())