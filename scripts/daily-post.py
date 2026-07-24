#!/usr/bin/env python3
"""
AI Frontlines — Daily blog post generator
Runs via cron at 12:00 PM SGT daily.
Fetches today's AI news from X/Twitter via bird CLI, picks ONE topic,
writes a personal blog post with SVG diagram, and pushes to GitHub.
"""
import subprocess, json, sys, os, re
from datetime import datetime, date

BLOG_DIR = "/Users/admin/Projects/ai-frontlines"
INDEX_PATH = os.path.join(BLOG_DIR, "index.html")

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.stdout + r.stderr

# ─── Step 1: Fetch today's AI news ───
print("Fetching AI news from X/Twitter...")

searches = [
    ("bird", ["search", "(from:OpenAI OR from:sama)", "-n", "5", "--plain"]),
    ("bird", ["search", "(from:AnthropicAI OR from:claudecode)", "-n", "5", "--plain"]),
    ("bird", ["search", "(from:GoogleAI OR from:GoogleDeepMind)", "-n", "5", "--plain"]),
    ("bird", ["search", "(from:elonmusk OR from:xai) Grok", "-n", "5", "--plain"]),
]

all_tweets = []
for label, cmd in searches:
    try:
        out = run(cmd)
        if out.strip():
            all_tweets.append({"source": label, "raw": out.strip()})
    except:
        pass

news_summary = "\n\n".join(f"[{t['source']}]\n{t['raw'][:800]}" for t in all_tweets)
print(f"Collected {len(all_tweets)} tweet batches")

if not news_summary.strip():
    print("WARNING: No tweets collected. Using fallback topic.")
    news_summary = "No news fetched today."

# ─── Step 2: Generate post via hermes agent ───
today = date.today().isoformat()
date_display = date.today().strftime("%B %d, %Y")

# The prompt that the cron agent will use
print(f"\nGenerating blog post for {today}...")
print(f"News context collected: {len(news_summary)} chars")
print("Handing off to agent for writing...")
