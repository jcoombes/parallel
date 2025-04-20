document.addEventListener('DOMContentLoaded', () => {
    // Initialize reveal.js
    Reveal.initialize({
        hash: true,
        slideNumber: true,
        transition: 'slide',
        backgroundTransition: 'fade',
        plugins: [
            RevealMarkdown,
            RevealHighlight,
            RevealNotes,
            RevealMath
        ]
    });

    // Add Ferris to the corner
    const ferris = document.createElement('img');
    ferris.src = 'https://rustacean.net/assets/rustacean-flat-happy.svg';
    ferris.className = 'ferris-corner';
    document.body.appendChild(ferris);

    // Theme toggle state
    let isDarkMode = false;

    // Add keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        if (event.key === 'f' || event.key === 'F') {
            // Toggle fullscreen
            const elem = document.documentElement;
            if (!document.fullscreenElement) {
                elem.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        } else if (event.key === 'b' || event.key === 'B') {
            // Toggle blackout
            document.body.classList.toggle('blackout');
        } else if (event.key === 't' || event.key === 'T') {
            // Toggle theme
            isDarkMode = !isDarkMode;
            document.body.classList.toggle('dark-mode');
            
            // Optional: Show theme change indicator
            const themeIndicator = document.createElement('div');
            themeIndicator.style.position = 'fixed';
            themeIndicator.style.top = '20px';
            themeIndicator.style.right = '20px';
            themeIndicator.style.padding = '10px 20px';
            themeIndicator.style.backgroundColor = isDarkMode ? '#0a1930' : '#B7BCBF';
            themeIndicator.style.color = isDarkMode ? '#00C8E1' : 'white';
            themeIndicator.style.borderRadius = '5px';
            themeIndicator.style.zIndex = '1000';
            themeIndicator.textContent = isDarkMode ? 'Dark Mode' : 'Light Mode';
            document.body.appendChild(themeIndicator);
            
            // Remove the indicator after 2 seconds
            setTimeout(() => {
                themeIndicator.remove();
            }, 2000);
        }
    });

    // Initialize syntax highlighting
    hljs.configure({
        languages: ['python', 'rust']
    });
    
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });
});

// Add custom styles for blackout mode
const style = document.createElement('style');
style.textContent = `
    body.blackout .reveal .slides {
        visibility: hidden;
    }
    body.blackout {
        background-color: #000;
    }
`;
document.head.appendChild(style); 