// ═══ AI Frontlines — Interactions ═══

// ─── Theme toggle ───
const themeToggle = document.getElementById('themeToggle');
const root = document.documentElement;
const savedTheme = localStorage.getItem('ai-frontlines-theme');
if (savedTheme) root.setAttribute('data-theme', savedTheme);

themeToggle?.addEventListener('click', () => {
    const current = root.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('ai-frontlines-theme', next);
});

// ─── Company filter ───
const chips = document.querySelectorAll('.filter-chip');
const cards = document.querySelectorAll('.card');
const filterBar = document.getElementById('filterBar');

chips.forEach(chip => {
    chip.addEventListener('click', () => {
        // Update active chip
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        const filter = chip.dataset.filter;
        cards.forEach(card => {
            const show = filter === 'all' || card.dataset.company === filter;
            if (show) {
                card.style.display = '';
                card.style.animation = 'none';
                // Trigger reflow then restart animation
                void card.offsetHeight;
                card.style.animation = 'cardIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// ─── Nav shrink on scroll ───
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const nav = document.getElementById('nav');
    const current = window.scrollY;
    if (current > 80) {
        nav.style.boxShadow = 'var(--shadow)';
    } else {
        nav.style.boxShadow = 'none';
    }
    lastScroll = current;
}, { passive: true });
