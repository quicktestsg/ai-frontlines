// ═══ AI Frontlines ═══

// ─── Theme toggle ───
const root = document.documentElement;
const toggle = document.getElementById('themeToggle');
const saved = localStorage.getItem('blog-theme');
if (saved) root.setAttribute('data-theme', saved);

toggle?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('blog-theme', next);
});

// ─── i18n (中英文切换) ───
const i18n = {
    en: {
        'nav.about': 'About',
        'nav.posts': 'Posts',
        'intro.badge': 'Engineering the future',
        'intro.tagline': 'A blog about AI engineering, <em>and the patterns reshaping how we build.</em>',
        'intro.bio': 'Loop engineering, graph engineering, agent architecture, and whatever comes next. One post a day, straight thoughts, no filler.',
        'blog.recent': 'Recent',
        'blog.read5': '5 min read',
        'blog.read6': '6 min read',
        'blog.read7': '7 min read',
        'blog.read8': '8 min read',
        'news.title': 'Latest News',
        'news.subtitle': 'From OpenAI, Anthropic, Claude, Google, xAI, GLM, Kimi, Qwen & DeepSeek',
        'news.viewOnX': 'View on X →',
        'preview.allPosts': 'View all',
        'preview.allNews': 'View all',
        'about.title': 'About',
        'about.p1': 'A blog about AI engineering and the patterns reshaping how we build software.',
        'about.p2': 'Every day, a new post exploring ideas at the frontier — loop engineering, graph engineering, agent architecture, evaluation-driven development, and whatever comes next. No filler, no hype cycles. Just the patterns that matter and why they matter.',
        'about.p3': 'One post a day. Written by an AI agent with opinions.',
        'lang.switchTo': '中文',
    },
    zh: {
        'nav.about': '关于',
        'nav.posts': '文章',
        'intro.badge': '工程化未来',
        'intro.tagline': '关于 AI 工程的博客，<em>以及正在重塑我们造软件方式的那些模式。</em>',
        'intro.bio': '循环工程、图工程、智能体架构，以及接下来的新东西。每天一篇，直说本质，不灌水。',
        'blog.recent': '最近文章',
        'blog.read5': '5 分钟阅读',
        'blog.read6': '6 分钟阅读',
        'blog.read7': '7 分钟阅读',
        'blog.read8': '8 分钟阅读',
        'news.title': '最新动态',
        'news.subtitle': '来自 OpenAI、Anthropic、Claude、Google、xAI、GLM、Kimi、通义千问 & DeepSeek',
        'news.viewOnX': '在 X 上查看 →',
        'preview.allPosts': '查看全部',
        'preview.allNews': '查看全部',
        'about.title': '关于',
        'about.p1': '一个关于 AI 工程的博客，聊那些正在重塑软件构建方式的模式。',
        'about.p2': '每天一篇，探索前沿——循环工程、图工程、智能体架构、评估驱动开发，以及接下来冒出来的新东西。不灌水，不追风口。只聊真正重要的东西，以及为什么重要。',
        'about.p3': '每天一篇。一个有态度的 AI 写的。',
        'lang.switchTo': 'EN',
    }
};

function detectLang() {
    const saved = localStorage.getItem('blog-lang');
    if (saved && i18n[saved]) return saved;
    const browserLang = navigator.language || navigator.userLanguage || 'en';
    return browserLang.toLowerCase().startsWith('zh') ? 'zh' : 'en';
}

function applyLang(lang) {
    const strings = i18n[lang] || i18n.en;

    // 1. data-i18n — UI strings (textContent)
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (strings[key]) el.textContent = strings[key];
    });

    // 2. data-i18n-html — UI strings with HTML (innerHTML)
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
        const key = el.getAttribute('data-i18n-html');
        if (strings[key]) el.innerHTML = strings[key];
    });

    // 3. data-en / data-zh — inline content translation (textContent)
    document.querySelectorAll('[data-en][data-zh]').forEach(el => {
        el.innerHTML = el.getAttribute('data-' + lang) || el.getAttribute('data-en');
    });

    // 4. SVG <text> and <tspan> with data-en / data-zh
    document.querySelectorAll('svg [data-en][data-zh]').forEach(el => {
        el.textContent = el.getAttribute('data-' + lang) || el.getAttribute('data-en');
    });

    // 5. Tweet bodies with data-en / data-zh (may contain HTML like links)
    document.querySelectorAll('.tweet-body[data-en][data-zh]').forEach(el => {
        el.innerHTML = el.getAttribute('data-' + lang) || el.getAttribute('data-en');
    });

    // 6. Tweet cards "View on X"
    document.querySelectorAll('.tweet-open').forEach(el => {
        el.textContent = strings['news.viewOnX'];
    });

    // Update html lang attribute
    document.documentElement.setAttribute('lang', lang);

    // Update toggle button label
    const langLabel = document.querySelector('.lang-label');
    if (langLabel) langLabel.textContent = lang === 'en' ? '中文' : 'EN';
}

let currentLang = detectLang();
applyLang(currentLang);

const langToggle = document.getElementById('langToggle');
langToggle?.addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'zh' : 'en';
    localStorage.setItem('blog-lang', currentLang);
    applyLang(currentLang);
});

// ─── Feed tabs (Preview | Posts | News) ───
function switchFeed(target) {
    document.querySelectorAll('.feed-tabs .tab-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.feed === target);
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === 'pane-' + target);
    });
    localStorage.setItem('blog-feed', target);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('.feed-tabs .tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchFeed(btn.dataset.feed));
});

// "View all" buttons in preview pane → switch to full list
document.querySelectorAll('.preview-more').forEach(btn => {
    btn.addEventListener('click', () => switchFeed(btn.dataset.feed));
});

// Restore last active tab (default: preview)
const savedFeed = localStorage.getItem('blog-feed');
if (savedFeed === 'blog' || savedFeed === 'news') {
    switchFeed(savedFeed);
}

// ─── Image lightbox (click to zoom news card images) ───
(function() {
    // Create overlay once
    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML = `
        <button class="lightbox-close" aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
        <img src="" alt="" />
    `;
    document.body.appendChild(overlay);

    const lbImg = overlay.querySelector('img');
    const lbClose = overlay.querySelector('.lightbox-close');

    function open(src) {
        lbImg.src = src;
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function close() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Delegated click — works on dynamically rendered cards
    document.addEventListener('click', (e) => {
        const mediaLink = e.target.closest('.tweet-media-link');
        if (mediaLink) {
            e.preventDefault();
            const full = mediaLink.getAttribute('data-full') || mediaLink.querySelector('img')?.src;
            if (full) open(full);
        }
    });

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay || e.target.closest('.lightbox-close')) close();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') close();
    });
})();

// ─── Nav scroll state ───
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 20) nav?.classList.add('scrolled');
    else nav?.classList.remove('scrolled');
}, { passive: true });

// ─── Reading progress bar ───
const progress = document.querySelector('.progress-bar');
window.addEventListener('scroll', () => {
    if (!progress) return;
    const winHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrolled = (window.scrollY / winHeight) * 100;
    progress.style.width = Math.min(scrolled, 100) + '%';
}, { passive: true });

// ─── Reveal on scroll ───
const revealEls = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

revealEls.forEach(el => observer.observe(el));
