#!/usr/bin/env python3
"""
Build index.html — the single source of truth for assembly.

Reads:
  - scripts/posts.json         → blog post metadata (manifest)
  - scripts/news_cache.json    → tweet data for news cards
  - index_template.html        → HTML skeleton with placeholders

Generates:
  - index.html                 → fully assembled page

The cron agent NEVER touches index.html or index_template.html.
It only writes:
  1. posts/YYYY-MM-DD-slug.html  (the full blog post)
  2. scripts/posts.json          (append one metadata entry)
  3. scripts/news_cache.json     (via add_news.py)

Then runs: python3 scripts/build_index.py && git add -A && git commit && git push
"""
import sys
import os
import re
import json
import html as html_module
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATE = os.path.join(PROJECT_DIR, "index_template.html")
OUTPUT = os.path.join(PROJECT_DIR, "index.html")
POSTS_MANIFEST = os.path.join(SCRIPT_DIR, "posts.json")

CSS_VERSION = "19"
NEWS_PREVIEW_COUNT = 4
POSTS_PREVIEW_COUNT = 4

sys.path.insert(0, SCRIPT_DIR)
from gen_news import load_cache, generate_all_cards


# ── Date formatting ──
def format_post_date(date_str):
    """ISO date (2026-07-31) → 'July 31, 2026'"""
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%B %-d, %Y")


def escape_attr(text):
    """Escape text for use in HTML attribute value."""
    return text.replace('"', '&quot;')


# ── Post card HTML generation ──
def generate_post_card(post):
    """Generate a single post card <div> for the lists."""
    slug = post["slug"]
    href = f"posts/{post['date']}-{slug}.html"
    date_display = format_post_date(post["date"])
    read_time = post.get("read_time", 5)
    title_en = escape_attr(post["title_en"])
    title_zh = escape_attr(post.get("title_zh", post["title_en"]))
    excerpt_en = escape_attr(post["excerpt_en"])
    excerpt_zh = escape_attr(post.get("excerpt_zh", post["excerpt_en"]))
    # Short excerpt for preview (truncated display version)
    short_en = post["excerpt_en"]
    if len(short_en) > 200:
        short_en = short_en[:197].rsplit(" ", 1)[0] + "."

    return f"""        <div class="post-item fade-in">
            <a href="{href}" class="post-item-inner">
                <div class="post-meta">
                    <span class="post-date">{date_display}</span>
                    <span class="post-dot"></span>
                    <span class="post-read" data-i18n="blog.read{read_time}">{read_time} min read</span>
                </div>
                <h2 class="post-title" data-en="{title_en}" data-zh="{title_zh}">{post['title_en']}</h2>
                <p class="post-excerpt" data-en="{excerpt_en}" data-zh="{excerpt_zh}">{short_en}</p>
                <span class="post-arrow">→</span>
            </a>
        </div>"""


def generate_post_cards(posts, limit=None):
    """Generate HTML for post cards, newest first."""
    sorted_posts = sorted(posts, key=lambda p: p["date"], reverse=True)
    if limit:
        sorted_posts = sorted_posts[:limit]
    return "\n\n".join(generate_post_card(p) for p in sorted_posts)


# ── Main build ──
def main():
    # Read template
    with open(TEMPLATE, "r") as f:
        template = f.read()

    # Bump CSS version
    template = re.sub(r'style\.css\?v=\d+', f'style.css?v={CSS_VERSION}', template)
    template = re.sub(r'app\.js\?v=\d+', f'app.js?v={CSS_VERSION}', template)

    # ── POSTS ──
    with open(POSTS_MANIFEST, "r") as f:
        posts = json.load(f)

    print(f"Loaded {len(posts)} posts from manifest", file=sys.stderr)

    posts_preview_html = generate_post_cards(posts, limit=POSTS_PREVIEW_COUNT)
    posts_full_html = generate_post_cards(posts)

    template = template.replace("<!-- POSTS_PREVIEW -->", posts_preview_html)
    template = template.replace("<!-- POSTS_FULL -->", posts_full_html)

    # ── NEWS ──
    cache = load_cache()
    print(f"Loaded {len(cache['tweets'])} tweets from cache", file=sys.stderr)

    cards = generate_all_cards(cache)
    news_html = "\n\n".join(cards)

    # Full news list → NEWS_INSERT
    template = template.replace("<!-- NEWS_INSERT -->", news_html)

    # Preview news (first N) → NEWS_PREVIEW
    preview_cards = cards[:NEWS_PREVIEW_COUNT]
    news_preview_html = "\n\n".join(preview_cards)
    template = template.replace("<!-- NEWS_PREVIEW -->", news_preview_html)

    # Write output
    with open(OUTPUT, "w") as f:
        f.write(template)

    post_count = len(posts)
    news_count = len(cache['tweets'])
    print(f"\n✅ Built index.html: {post_count} posts ({POSTS_PREVIEW_COUNT} preview), {news_count} news ({NEWS_PREVIEW_COUNT} preview)", file=sys.stderr)
    print(f"   CSS version: v={CSS_VERSION}", file=sys.stderr)


if __name__ == "__main__":
    main()
