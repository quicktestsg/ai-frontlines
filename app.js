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

// ─── Lazy-load X/Twitter widgets when news section scrolls into view ───
const newsSection = document.querySelector('.news-section');
if (newsSection) {
    const newsObserver = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            const s = document.createElement('script');
            s.src = 'https://platform.x.com/widgets.js';
            s.async = true;
            s.charset = 'utf-8';
            document.head.appendChild(s);
            newsObserver.unobserve(newsSection);
        }
    }, { rootMargin: '200px' });
    newsObserver.observe(newsSection);
}
