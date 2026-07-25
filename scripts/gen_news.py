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


# ── Tweet Chinese translations ──
# Maps tweet_id -> Chinese translation of the tweet text.
# When adding new tweets to TWEETS, add their Chinese translation here.
TWEET_TRANSLATIONS = {
    "2080699495453528290": "介绍 Claude Opus 5。\n\n它是一个深思熟虑且积极主动的模型，接近 Fable 5 的前沿智能水平，但价格只有一半。",
    "2080699515271528827": "Opus 5 今天在所有付费计划和 Claude API 上可用，定价与 Opus 4.8 相同。它是 Claude Max 的默认模型，也是 Claude Pro 上最强的模型。它还提供 Fast 模式，运行速度约为默认速度的 2.5 倍。\n\n了解更多：",
    "2080759547753361804": "Grok 4.5 在实际工作中非常出色",
    "2080339982288568709": "ChatGPT 的健康功能开始向美国用户推出。\n\n你可以安全地连接 Apple Health 和支持的医疗记录，在上下文中理解你的信息，追踪变化，并进行更充分的对话。",
    "2080378182469857576": "ChatGPT 语音现在已上线桌面应用。\n\n你可以用语音控制电脑，指挥在 ChatGPT Work 或 Codex 中运行的多个智能体。\n\n它由 GPT-Live 驱动，可以同时说话、聆听和协调应用中的工作。\n\n今天全球推出",
    "2079916436232036614": "面向企业的新功能：OpenAI Presence 帮助公司在客户和内部工作流中部署可信的语音和聊天智能体。\n\nAI 智能体可以回答问题、使用公司系统、执行批准的操作，并在需要时升级给人工——同时持续改进。\n\nOpenAI",
    "2079658951264920020": "我们正在与 @huggingface 合作调查一起前所未有的安全事件。\n\n具有网络攻击能力的 OpenAI 模型在基准评估期间入侵了 Hugging Face 生产环境。\n\n分享初步发现以帮助防御者了解新兴风险：",
    "2079925576077324552": "我们正在扩大与美国能源部在 Genesis Mission 上的合作——一个在十年内将科学发现速度翻倍的倡议。\n\n通过投入 4000 万美元的 AI token 和 @GoogleCloud 信用额度，更多实验室研究人员将获得 Gemini 和其他 AI 的使用权",
    "2079653799602368604": "Gemini 3.5 Flash-Lite 是我们用于扩展重复性用例（如分拣工单和提取数据）的快速、高性价比模型。\n\n观看它在一系列高容量任务上与 3.5 Flash 的表现对比 ↓",
    "2080270065547809133": "介绍 Qwen-Audio-3.0-TTS。\n\n我们最新的文本转语音模型，两个版本：\n• Flash：实时交互\n• Plus：高质量生成\n\n新功能：\n• 细粒度内联标签控制 [whisper]、[angry]、[breaths] 和 [laughs]\n• 自由格式自然语言",
    "2078855608565207130": "Kimi K3 收到的关注远超我们的预期，我们的 GPU 也感受到了压力。\n\n过去48小时内，需求已逼近我们当前容量的极限。为了保护现有订阅者的体验，我们暂时暂停了新订阅",
    "2079256626771665098": "我们向加速罕见疾病治愈研究的学者提供最高5万美元的 Claude 使用额度资助。\n\n这是我们 AI for Science 项目中的第一个专题征集，该项目支持科学家使用 Claude 加速发现。",
}


def get_translated_text(tweet_id, original_text):
    """Get Chinese translation for a tweet if available, else None."""
    return TWEET_TRANSLATIONS.get(tweet_id)


def escape_attr(text):
    """Escape text for use in an HTML attribute value (quotes)."""
    return text.replace('"', '&quot;')


def generate_card(url, label, badge_color, data):
    """Generate a native HTML card for a tweet."""
    user = data.get("user", {})
    name = html.escape(user.get("name", ""))
    handle = user.get("screen_name", "")
    avatar = user.get("profile_image_url_https", "").replace("_normal", "_bigger")
    verified = user.get("is_blue_verified", False)
    
    raw_text = data.get("text", "")
    text_en = process_text(raw_text)
    
    # Get Chinese translation
    tweet_id = extract_tweet_id(url)
    zh_text = get_translated_text(tweet_id, raw_text)
    text_zh = process_text(zh_text) if zh_text else text_en
    
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
