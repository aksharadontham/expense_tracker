// main.js — icon rendering and the dashboard's daily-spend bars.

document.addEventListener('DOMContentLoaded', function () {
    // Swap every <i data-lucide="..."> for its SVG.
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Bar heights live in data-pct so the template stays free of inline styles.
    document.querySelectorAll('.chart-bar').forEach(function (bar) {
        var pct = parseFloat(bar.dataset.pct);
        if (isNaN(pct) || pct < 0) {
            pct = 0;
        }
        // Floor at 3% so a very small day is still visible.
        bar.style.height = Math.max(pct, 3) + '%';
    });
});
