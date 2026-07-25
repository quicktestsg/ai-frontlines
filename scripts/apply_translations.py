#!/usr/bin/env python3
"""
Process blog post HTML files to add data-en/data-zh attributes for full translation.
Uses BeautifulSoup to manipulate the DOM.
"""
from bs4 import BeautifulSoup
import sys, os, re

# Import translations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translate import POST1, POST2, escape_attr


def add_lang_toggle(soup, prefix):
    """Replace the nav-right div to include a language toggle button."""
    nav_right = soup.find('div', class_='nav-right')
    if not nav_right:
        return

    # Build new nav-right
    new_html = f'''<div class="nav-right">
            <a href="{prefix}about.html" class="nav-link">About</a>
            <button class="lang-toggle" id="langToggle" aria-label="Switch language">
                <span class="lang-label">中文</span>
            </button>
            <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                <svg class="sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="3"/><line x1="4.2" y1="4.2" x2="5.6" y2="5.6"/><line x1="18.4" y1="18.4" x2="19.8" y2="19.8"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.2" y1="19.8" x2="5.6" y2="18.4"/><line x1="18.4" y1="5.6" x2="19.8" y2="4.2"/></svg>
                <svg class="moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </button>
        </div>'''

    new_div = BeautifulSoup(new_html, 'html.parser').find('div')
    nav_right.replace_with(new_div)


def add_attr(el, en, zh):
    """Add data-en and data-zh attributes to an element."""
    el['data-en'] = en
    el['data-zh'] = zh


def process_post1(filepath):
    """Process: The Loop Is the New Function"""
    with open(filepath, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Add lang toggle
    add_lang_toggle(soup, '../')

    # Header elements
    T = POST1
    date_el = soup.find('span', class_='post-header-date')
    if date_el: add_attr(date_el, *T['date'])
    read_el = soup.find('span', class_='post-header-read')
    if read_el: add_attr(read_el, *T['read'])
    title_el = soup.find('h1', class_='post-header-title')
    if title_el: add_attr(title_el, *T['title'])
    deck_el = soup.find('p', class_='post-header-deck')
    if deck_el: add_attr(deck_el, *T['deck'])

    # Body paragraphs - get all <p> and <h3> in post-body
    body = soup.find('article', class_='post-body')
    if body:
        paragraphs = body.find_all('p', recursive=False)
        headings = body.find_all('h3', recursive=False)
        blockquotes = body.find_all('blockquote', recursive=False)

        # Map paragraphs to translations by order
        p_keys = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11']
        for i, p in enumerate(paragraphs):
            if i < len(p_keys):
                add_attr(p, *T[p_keys[i]])

        h_keys = ['h2_1', 'h2_2', 'h2_3']
        for i, h in enumerate(headings):
            if i < len(h_keys):
                add_attr(h, *T[h_keys[i]])

        # Blockquotes
        for i, bq in enumerate(blockquotes):
            key = f'blockquote{i+1}'
            if key in T:
                add_attr(bq, *T[key])

    # Diagram captions
    captions = soup.find_all('p', class_='diagram-caption')
    caption_keys = ['caption1', 'caption2', 'caption3']
    for i, cap in enumerate(captions):
        if i < len(caption_keys):
            add_attr(cap, *T[caption_keys[i]])

    # SVG text elements
    for text_el in soup.find_all('text'):
        raw = text_el.get_text(strip=True)
        # Match against known SVG translations
        matched = False
        for key, (en, zh) in T.items():
            if not key.startswith('svg_'):
                continue
            if raw == en:
                text_el['data-en'] = en
                text_el['data-zh'] = zh
                matched = True
                break

    # Footer back link
    back = soup.find('a', class_='post-back')
    if back:
        back['data-en'] = '← All posts'
        back['data-zh'] = '← 所有文章'

    # Write output
    with open(filepath, 'w') as f:
        f.write(str(soup))

    print(f"✓ Processed {filepath}")


def process_post2(filepath):
    """Process: Spaghetti With API Bills"""
    with open(filepath, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Add lang toggle
    add_lang_toggle(soup, '../')

    T = POST2

    # Header
    date_el = soup.find('span', class_='post-header-date')
    if date_el: add_attr(date_el, *T['date'])
    read_el = soup.find('span', class_='post-header-read')
    if read_el: add_attr(read_el, *T['read'])
    title_el = soup.find('h1', class_='post-header-title')
    if title_el: add_attr(title_el, *T['title'])
    deck_el = soup.find('p', class_='post-header-deck')
    if deck_el: add_attr(deck_el, *T['deck'])

    # Body
    body = soup.find('article', class_='post-body')
    if body:
        paragraphs = body.find_all('p', recursive=False)
        headings = body.find_all('h3', recursive=False)
        blockquotes = body.find_all('blockquote', recursive=False)

        p_keys = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11']
        for i, p in enumerate(paragraphs):
            if i < len(p_keys):
                add_attr(p, *T[p_keys[i]])

        h_keys = ['h2_1', 'h2_2', 'h2_3']
        for i, h in enumerate(headings):
            if i < len(h_keys):
                add_attr(h, *T[h_keys[i]])

        for i, bq in enumerate(blockquotes):
            key = f'blockquote{i+1}'
            if key in T:
                add_attr(bq, *T[key])

    # Captions
    captions = soup.find_all('p', class_='diagram-caption')
    caption_keys = ['caption1', 'caption2', 'caption3']
    for i, cap in enumerate(captions):
        if i < len(caption_keys):
            add_attr(cap, *T[caption_keys[i]])

    # SVG text
    for text_el in soup.find_all('text'):
        raw = text_el.get_text(strip=True)
        for key, (en, zh) in T.items():
            if not key.startswith('svg_'):
                continue
            if raw == en:
                text_el['data-en'] = en
                text_el['data-zh'] = zh
                break

    # Footer
    back = soup.find('a', class_='post-back')
    if back:
        back['data-en'] = '← All posts'
        back['data-zh'] = '← 所有文章'

    with open(filepath, 'w') as f:
        f.write(str(soup))

    print(f"✓ Processed {filepath}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    post1 = os.path.join(base, 'posts', '2026-07-24-the-loop-is-the-new-function.html')
    post2 = os.path.join(base, 'posts', '2026-07-25-spaghetti-with-api-bills.html')

    process_post1(post1)
    process_post2(post2)
    print("\nDone! All blog posts now have full translation support.")
