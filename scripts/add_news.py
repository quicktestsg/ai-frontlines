#!/usr/bin/env python3
"""
Add new tweets to the news cache and rebuild index.html.

Usage:
  python3 add_news.py

This script:
1. Loads news_cache.json
2. Adds any tweets listed in NEW_TWEETS below (skipping duplicates)
3. Saves the cache
4. Rebuilds index.html from the cache + template

The cron job edits the NEW_TWEETS list below before running this script.
Existing tweets are NEVER refetched — they stay cached.
"""
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from gen_news import (
    load_cache,
    save_cache,
    add_tweets_to_cache,
    generate_all_cards,
)
import build_index

# ── Tweets to add today (edit this list) ──
# Format: (url, label, badge_color)
# Duplicate tweet IDs are automatically skipped.
# Leave empty [] to just rebuild from existing cache.
NEW_TWEETS = [
]


def main():
    cache = load_cache()
    before = len(cache["tweets"])

    if NEW_TWEETS:
        cache, num_new, num_skipped = add_tweets_to_cache(NEW_TWEETS, cache)
        save_cache(cache)
        print(f"\nAdded {num_new} new tweets, skipped {num_skipped} duplicates", file=sys.stderr)
    else:
        print("No new tweets to add — rebuilding from cache only", file=sys.stderr)

    print(f"Cache: {before} → {len(cache['tweets'])} tweets total", file=sys.stderr)

    # Rebuild index.html
    build_index.main()


if __name__ == "__main__":
    main()
