# test_openai_pick.py
import json
import yaml
from select_new import fetch_new
from summarize import summarize_items
from apply_selection import apply_selected

def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    items = fetch_new(limit=int(cfg["openai"].get("max_items_in_batch", 25)))
    print("Fetched new:", len(items))

    data = summarize_items(cfg, items)

    with open("last_selection.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    apply_selected(data["selected"])
    print("Selected:", len(data["selected"]))
    for s in data["selected"]:
        print("-", s["headline_ru"])

if __name__ == "__main__":
    main()