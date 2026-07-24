// ═══ AI Frontlines — Personal Blog ═══

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
