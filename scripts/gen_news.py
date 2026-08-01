#!/usr/bin/env python3
"""
Fetch tweet data via syndication API and generate native HTML cards
that match the AI Frontlines design system.

INCREMENTAL MODE:
- Tweets are stored persistently in news_cache.json
- Only NEW tweet URLs need to be fetched — existing ones reuse cached data
- Dedup by tweet ID — if a tweet is already in the cache, it's skipped
- The cron job only needs to pass new URLs; old news stays
"""
import json
import urllib.request
import re
import sys
import html
import os
from datetime import datetime, timezone

# ── Paths ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(SCRIPT_DIR, "news_cache.json")

# ── Badge colors for known accounts ──
BADGE_COLORS = {
    "OpenAI": "#10A37F",
    "Claude": "#D4A574",
    "Anthropic": "#D4A574",
    "Google": "#4285F4",
    "xAI": "#1DA1F2",
    "GLM": "#7C3AED",
    "Kimi": "#6366F1",
    "Qwen": "#FF6B35",
    "DeepSeek": "#0EA5E9",
}

# ── New tweets to add (set by cron job or manual run) ──
# Format: list of (url, label, badge_color) tuples
# Leave empty to just rebuild from cache
NEW_TWEETS = []


def load_cache():
    """Load the persistent news cache. Returns dict with 'tweets' list."""
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {"tweets": []}


def save_cache(cache):
    """Save the persistent news cache."""
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def extract_tweet_id(url):
    match = re.search(r'/status/(\d+)', url)
    return match.group(1) if match else None


def fetch_tweet_data(tweet_id):
    """Fetch structured tweet data from Twitter's syndication API."""
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=a"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def format_count(n):
    """Format like/reply counts (1234 -> 1.2K)."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_date(date_str):
    """Format ISO date to 'Jul 25' style, converted to SGT (UTC+8)."""
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    # Convert UTC to Singapore time (UTC+8)
    from datetime import timedelta
    sgt = dt + timedelta(hours=8)
    return sgt.strftime("%b %-d")


def process_text(text):
    """Convert tweet text to HTML — linkify URLs and @mentions."""
    text = html.escape(text)
    # Linkify @mentions
    text = re.sub(
        r'@(\w+)',
        r'<a href="https://x.com/\1" target="_blank" rel="noopener">@\1</a>',
        text
    )
    return text


def get_best_photo(tweet):
    """Get the highest quality photo from tweet."""
    photos = tweet.get("photos", [])
    if photos:
        photo = photos[0]
        return photo.get("url", "").replace("normal", "large") if "pbs.twimg.com" in photo.get("url", "") else photo.get("url")
    for media in tweet.get("media", []):
        if media.get("type") == "photo":
            return media.get("media_url_https", "").replace("normal", "large")
    return None


def get_video_poster(tweet):
    """Get video thumbnail."""
    video = tweet.get("video", {})
    if video:
        return video.get("poster", "")
    for media in tweet.get("media", []):
        if media.get("type") == "video":
            return media.get("media_url_https", "")
    return None


def escape_attr(text):
    """Escape text for use in an HTML attribute value (quotes)."""
    return text.replace('"', '&quot;')


def generate_card(url, label, badge_color, data, translation_zh=""):
    """Generate a native HTML card for a tweet."""
    user = data.get("user", {})
    name = html.escape(user.get("name", ""))
    handle = user.get("screen_name", "")
    avatar = user.get("profile_image_url_https", "").replace("_normal", "_bigger")
    verified = user.get("is_blue_verified", False)

    raw_text = data.get("text", "")
    text_en = process_text(raw_text)

    # Use provided translation, or fall back to English
    text_zh = process_text(translation_zh) if translation_zh else text_en

    # Escape for attribute embedding
    attr_en = escape_attr(text_en)
    attr_zh = escape_attr(text_zh)

    date_str = format_date(data.get("created_at", ""))

    likes = format_count(data.get("favorite_count", 0))
    replies = format_count(data.get("reply_count", 0))
    retweets = format_count(data.get("retweet_count", 0))

    photo = get_best_photo(data)
    video_poster = get_video_poster(data)
    media_url = photo or video_poster

    # Build media HTML — click to zoom (lightbox), not navigate to X
    media_html = ""
    if media_url:
        media_html = f'''
        <div class="tweet-media-link" data-full="{media_url}">
            <img src="{media_url}" alt="" class="tweet-media" loading="lazy" />
        </div>'''

    # Verified badge
    verified_html = ""
    if verified:
        verified_html = '<svg class="verified-badge" width="16" height="16" viewBox="0 0 22 22" fill="none"><path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.972.854-1.245 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" fill="currentColor"/></svg>'

    return f'''        <article class="tweet-card fade-in">
            <div class="tweet-header">
                <img src="{avatar}" alt="" class="tweet-avatar" loading="lazy" />
                <div class="tweet-author">
                    <span class="tweet-name">{name}{verified_html}</span>
                    <span class="tweet-handle">@{handle} · {date_str}</span>
                </div>
                <span class="news-badge" style="background:{badge_color}">{label}</span>
            </div>
            <div class="tweet-body" data-en="{attr_en}" data-zh="{attr_zh}">{text_en}</div>{media_html}
            <div class="tweet-footer">
                <a href="{url}" target="_blank" rel="noopener" class="tweet-stat">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 1.999l-8.12 8.12L12 13.87l-2.88-2.75L1 1.999M1 9.999l6.12 6.12L11 19.87l2.88-2.75L23 9.999"/></svg>
                    {replies}
                </a>
                <a href="{url}" target="_blank" rel="noopener" class="tweet-stat">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 014-4h14M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>
                    {retweets}
                </a>
                <a href="{url}" target="_blank" rel="noopener" class="tweet-stat">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
                    {likes}
                </a>
                <a href="{url}" target="_blank" rel="noopener" class="tweet-open" data-i18n="news.viewOnX">
                    View on X →
                </a>
            </div>
        </article>'''


def add_tweets_to_cache(new_tweets, cache):
    """
    Add new tweets to cache, skipping duplicates.
    new_tweets: list of (url, label, color) tuples
    Returns: (updated_cache, num_new, num_skipped)
    """
    existing_ids = {t["id"] for t in cache["tweets"]}
    num_new = 0
    num_skipped = 0
    now = datetime.now(timezone.utc).isoformat()

    for url, label, color in new_tweets:
        tweet_id = extract_tweet_id(url)
        if not tweet_id:
            print(f"  SKIP — could not extract ID from {url}", file=sys.stderr)
            continue
        if tweet_id in existing_ids:
            num_skipped += 1
            print(f"  DEDUP {label} — {tweet_id} already in cache", file=sys.stderr)
            continue
        try:
            data = fetch_tweet_data(tweet_id)
            cache["tweets"].append({
                "id": tweet_id,
                "url": url,
                "label": label,
                "color": color,
                "fetched_at": now,
                "translation_zh": "",
                "tweet_data": data,
            })
            existing_ids.add(tweet_id)
            num_new += 1
            print(f"  NEW {label} — {data.get('text', '')[:60]}...", file=sys.stderr)
        except Exception as e:
            print(f"  FAIL {label} — {url}: {e}", file=sys.stderr)

    # Sort by tweet's actual created_at timestamp, newest first
    cache["tweets"] = _sort_by_date(cache["tweets"])
    return cache, num_new, num_skipped


def _sort_by_date(tweets):
    """Sort tweets by created_at descending (newest first)."""
    def get_date(entry):
        created = entry.get("tweet_data", {}).get("created_at", "")
        return created or ""
    return sorted(tweets, key=get_date, reverse=True)


def generate_all_cards(cache):
    """Generate HTML cards for all cached tweets (newest first by tweet date)."""
    sorted_tweets = _sort_by_date(cache["tweets"])
    cards = []
    for entry in sorted_tweets:
        card = generate_card(
            entry["url"],
            entry["label"],
            entry["color"],
            entry["tweet_data"],
            entry.get("translation_zh", ""),
        )
        cards.append(card)
    return cards


def main():
    """Standalone: rebuild cards from cache (no new tweets to add)."""
    cache = load_cache()
    print(f"Loaded {len(cache['tweets'])} tweets from cache", file=sys.stderr)
    cards = generate_all_cards(cache)
    print(f"Generated {len(cards)} cards", file=sys.stderr)
    print("\n\n".join(cards))


if __name__ == "__main__":
    main()
