#!/usr/bin/env python3
"""
Build index.html: takes index_template.html + generates tweet cards → index.html
Also bumps CSS version.

Reads from news_cache.json — no refetching of existing tweets.
The cron job adds new tweets to the cache via add_news.py before running this.
"""
import sys
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from gen_news import load_cache, generate_all_cards

PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATE = os.path.join(PROJECT_DIR, "index_template.html")
OUTPUT = os.path.join(PROJECT_DIR, "index.html")

CSS_VERSION = "15"


def main():
    # Read template
    with open(TEMPLATE, "r") as f:
        template = f.read()

    # Bump CSS version
    template = re.sub(r'style\.css\?v=\d+', f'style.css?v={CSS_VERSION}', template)

    # Load cache and generate cards (no API calls for existing tweets)
    cache = load_cache()
    print(f"Loaded {len(cache['tweets'])} tweets from cache", file=sys.stderr)

    cards = generate_all_cards(cache)
    news_html = "\n\n".join(cards)

    # Replace NEWS_INSERT placeholder
    result = template.replace("<!-- NEWS_INSERT -->", news_html)

    # Write output
    with open(OUTPUT, "w") as f:
        f.write(result)

    print(f"\nGenerated {len(cards)} cards → {OUTPUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
