# AGENTS.md — AI Frontlines Operating Manual

> **Read this before touching anything.** This file is injected into every agent session working in this repo.

## Architecture: Modular Build System

```
Content Sources (Agent edits these)          Build (Agent runs this)         Output (NEVER touch)
─────────────────────────────────         ──────────────────────────      ─────────────────────
scripts/posts.json                         python3 scripts/build_index.py  →  index.html
  ↳ post metadata (date, title, slug)                                         (AUTO-GENERATED)

posts/YYYY-MM-DD-slug.html                                                   ⚠️ DO NOT EDIT
  ↳ full article HTML (SVG diagrams, i18n)

scripts/news_cache.json
  ↳ tweet data + translations
```

## The Golden Rule

**`index.html` is AUTO-GENERATED. NEVER edit it directly.**

It is rebuilt from scratch on every `python3 scripts/build_index.py` run. Any manual edit will be lost.

A git pre-commit hook will **block** any commit where `index.html` lacks the `AUTO-GENERATED` header.

---

## How to Add a Blog Post

### 1. Write the post file

Create `posts/YYYY-MM-DD-slug.html`. Study an existing post for the exact structure:
- Nav is **OUTSIDE** the `.wrap` div
- SVG diagrams (3+) using **CSS variables** (`var(--accent)`, `var(--bg-surface)` — never hardcoded colors)
- Full **i18n**: every element has `data-en` / `data-zh` attributes (including SVG `<text>`)
- Cinematic design matching `style.css` (glassmorphism, mesh background, gradient accents)

### 2. Add metadata to `scripts/posts.json`

Prepend one entry to the JSON array (order doesn't matter — build script sorts by date):

```json
{
  "date": "2026-08-01",
  "slug": "your-slug",
  "title_en": "English Title",
  "title_zh": "中文标题",
  "read_time": 8,
  "excerpt_en": "1-2 sentence English excerpt for the listing card.",
  "excerpt_zh": "1-2句中文摘要。"
}
```

### 3. Rebuild and push

```bash
python3 scripts/build_index.py
git add -A && git commit -m "Daily post: TITLE" && git push
```

**That's it.** The build script handles all sorting, card generation, preview selection, CSS version bumping, and assembly.

---

## How to Add News Items

### 1. Check what's already cached

```bash
python3 -c "import json; c=json.load(open('scripts/news_cache.json')); [print(f'{t[\"id\"]} {t[\"label\"]}') for t in c['tweets']]"
```

### 2. Search for new tweets

```bash
/opt/homebrew/bin/bird search "from:OpenAI OR from:AnthropicAI OR from:GoogleDeepMind OR from:xai OR from:Zai_org OR from:Kimi_Moonshot OR from:Alibaba_Qwen OR from:deepseek_ai" -n 30 --plain
```

### 3. Add new tweets

Edit `scripts/add_news.py` → set `NEW_TWEETS` list:

```python
NEW_TWEETS = [
    ("https://x.com/OpenAI/status/XXXXXXXX", "OpenAI", "#10A37F"),
]
```

Badge colors: OpenAI=#10A37F, Claude=#D4A574, Anthropic=#D4A574, Google=#4285F4, xAI=#1DA1F2, GLM=#7C3AED, Kimi=#6366F1, Qwen=#FF6B35, DeepSeek=#0EA5E9

### 4. Add Chinese translations

```bash
python3 -c "
import json
cache = json.load(open('scripts/news_cache.json'))
trans = { 'TWEET_ID': '中文翻译' }
for t in cache['tweets']:
    if t['id'] in trans:
        t['translation_zh'] = trans[t['id']]
json.dump(cache, open('scripts/news_cache.json','w'), ensure_ascii=False, indent=2)
"
```

### 5. Run add_news.py (fetches new tweets, updates cache, rebuilds)

```bash
python3 scripts/add_news.py
```

### 6. Clear NEW_TWEETS and rebuild

```bash
# Edit scripts/add_news.py → set NEW_TWEETS = []
python3 scripts/build_index.py
git add -A && git commit -m "News update (N new)" && git push
```

---

## File Reference

| File | Editable? | Purpose |
|------|-----------|---------|
| `scripts/posts.json` | ✅ Yes | Post metadata manifest |
| `posts/*.html` | ✅ Yes | Full article pages (SVG, i18n) |
| `scripts/news_cache.json` | ✅ Yes | Cached tweet data + translations |
| `scripts/add_news.py` | ✅ Yes (temporarily) | Add new tweets, then clear `NEW_TWEETS` |
| `scripts/build_index.py` | ⚠️ Careful | The build engine. Edit only to change build logic. |
| `scripts/gen_news.py` | ⚠️ Careful | Tweet card generator + date formatting (UTC→SGT) |
| `index_template.html` | ⚠️ Structure only | HTML skeleton with placeholders. Edit CSS/layout, but **never** add post or news HTML here. |
| `index.html` | ❌ NEVER | Auto-generated. Overwritten on every build. |
| `style.css` | ✅ Yes | Shared styles |
| `app.js` | ✅ Yes | Theme toggle, tab switching, i18n logic |

---

## Cron Schedule

| Time (SGT) | Job |
|------------|-----|
| **04:00** | Write daily blog post + fetch news |
| **16:00** | Fetch news only (catch US afternoon announcements) |

---

## Do NOT

- **Do NOT** edit `index.html` — it's generated and will be overwritten.
- **Do NOT** add post/news HTML to `index_template.html` — use the JSON manifests.
- **Do NOT** touch `posts/*.html` unless writing/editing that specific article.
- **Do NOT** hardcode colors in SVG — always use CSS variables (`var(--accent)` etc).
- **Do NOT** use first person "I" — posts are anonymous.
- **Do NOT** write news recaps as blog posts — posts are original analysis only.
