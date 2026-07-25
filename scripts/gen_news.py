#!/usr/bin/env python3
"""
Fetch tweet data via syndication API and generate native HTML cards
that match the AI Frontlines design system.
"""
import json
import urllib.request
import re
import sys
import html
from datetime import datetime

# ── Config ──
TWEETS = [
    ("https://x.com/claudeai/status/2080699495453528290", "Claude", "#D4A574"),
    ("https://x.com/claudeai/status/2080699515271528827", "Claude", "#D4A574"),
    ("https://x.com/elonmusk/status/2080759547753361804", "xAI", "#1DA1F2"),
    ("https://x.com/OpenAI/status/2080339982288568709", "OpenAI", "#10A37F"),
    ("https://x.com/OpenAI/status/2080378182469857576", "OpenAI", "#10A37F"),
    ("https://x.com/OpenAI/status/2079916436232036614", "OpenAI", "#10A37F"),
    ("https://x.com/OpenAI/status/2079658951264920020", "OpenAI", "#10A37F"),
    ("https://x.com/GoogleDeepMind/status/2079925576077324552", "Google", "#4285F4"),
    ("https://x.com/GoogleDeepMind/status/2079653799602368604", "Google", "#4285F4"),
    ("https://x.com/Alibaba_Qwen/status/2080270065547809133", "Qwen", "#FF6B35"),
    ("https://x.com/Kimi_Moonshot/status/2078855608565207130", "Kimi", "#6366F1"),
    ("https://x.com/AnthropicAI/status/2079256626771665098", "Anthropic", "#D4A574"),
]


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
    """Format ISO date to 'Jul 25' style."""
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return dt.strftime("%b %-d")


def process_text(text):
    """Convert tweet text to HTML — linkify URLs and @mentions."""
    text = html.escape(text)
    # Linkify URLs
    text = re.sub(
        r'https?://t\.co/\S+',
        lambda m: m.group(0),
        text
    )
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
        # Get the largest image
        photo = photos[0]
        return photo.get("url", "").replace("normal", "large") if "pbs.twimg.com" in photo.get("url", "") else photo.get("url")
    # Check media in extended_entities
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


def generate_card(url, label, badge_color, data):
    """Generate a native HTML card for a tweet."""
    user = data.get("user", {})
    name = html.escape(user.get("name", ""))
    handle = user.get("screen_name", "")
    avatar = user.get("profile_image_url_https", "").replace("_normal", "_bigger")
    verified = user.get("is_blue_verified", False)
    
    text = process_text(data.get("text", ""))
    date_str = format_date(data.get("created_at", ""))
    
    likes = format_count(data.get("favorite_count", 0))
    replies = format_count(data.get("reply_count", 0))
    retweets = format_count(data.get("retweet_count", 0))
    
    photo = get_best_photo(data)
    video_poster = get_video_poster(data)
    media_url = photo or video_poster
    
    # Build media HTML
    media_html = ""
    if media_url:
        media_html = f'''
        <a href="{url}" target="_blank" rel="noopener" class="tweet-media-link">
            <img src="{media_url}" alt="" class="tweet-media" loading="lazy" />
        </a>'''
    
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
            <div class="tweet-body">{text}</div>{media_html}
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


def main():
    cards = []
    for url, label, color in TWEETS:
        tweet_id = extract_tweet_id(url)
        if not tweet_id:
            continue
        try:
            data = fetch_tweet_data(tweet_id)
            card = generate_card(url, label, color, data)
            cards.append(card)
            print(f"✓ {label} — {data.get('text', '')[:50]}...", file=sys.stderr)
        except Exception as e:
            print(f"✗ {label} — {url}: {e}", file=sys.stderr)
    
    print("\n".join(cards))


if __name__ == "__main__":
    main()
