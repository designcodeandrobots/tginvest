import yaml
from db import init_db
from rss import fetch_rss
from storage import save_news

def main():
    init_db()

    with open("sources.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    total = 0
    for src in cfg["sources"]:
        items = fetch_rss(src["name"], src["url"])
        saved = save_news(items)
        print(f"{src['name']}: +{saved}")
        total += saved

    print(f"Всего сохранено: {total}")

if __name__ == "__main__":
    main()