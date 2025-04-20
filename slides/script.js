// Initialize reveal.js
Reveal.initialize({
    hash: true,
    slideNumber: true,
    transition: 'slide',
    backgroundTransition: 'fade'
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Fullscreen toggle
    if (event.key === 'f') {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            document.documentElement.requestFullscreen();
        }
    }
    // Blackout mode toggle
    if (event.key === 'b') {
        document.body.classList.toggle('blackout');
    }
});

// Custom blackout mode style
document.body.classList.add('blackout');
document.body.style.backgroundColor = '#000';
document.querySelectorAll('.reveal .slides section').forEach(slide => {
    slide.style.visibility = 'hidden';
}); 