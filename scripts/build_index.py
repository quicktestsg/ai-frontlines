#!/usr/bin/env python3
"""
Build index.html: takes index_template.html + generates tweet cards → index.html
Also bumps CSS version.
"""
import sys
import os
import re

# Add the gen_news module's directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from gen_news import TWEETS, extract_tweet_id, fetch_tweet_data, generate_card

PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATE = os.path.join(PROJECT_DIR, "index_template.html")
OUTPUT = os.path.join(PROJECT_DIR, "index.html")

CSS_VERSION = "11"


def main():
    # Read template
    with open(TEMPLATE, "r") as f:
        template = f.read()

    # Bump CSS version
    template = re.sub(r'style\.css\?v=\d+', f'style.css?v={CSS_VERSION}', template)

    # Generate cards
    cards = []
    for url, label, color in TWEETS:
        tweet_id = extract_tweet_id(url)
        if not tweet_id:
            continue
        try:
            data = fetch_tweet_data(tweet_id)
            card = generate_card(url, label, color, data)
            cards.append(card)
            print(f"  OK {label} — {data.get('text', '')[:50]}...", file=sys.stderr)
        except Exception as e:
            print(f"  FAIL {label} — {url}: {e}", file=sys.stderr)

    # Replace NEWS_INSERT placeholder
    news_html = "\n\n".join(cards)
    result = template.replace("<!-- NEWS_INSERT -->", news_html)

    # Write output
    with open(OUTPUT, "w") as f:
        f.write(result)

    print(f"\nGenerated {len(cards)} cards → {OUTPUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
