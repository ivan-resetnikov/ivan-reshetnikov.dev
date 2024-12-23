// Theme adaptation
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    // Dark mode
} else {
    // Light mode
    document.body.classList.add('light-mode');
}
