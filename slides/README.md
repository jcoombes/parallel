# Asynchronous Programming in Python and Rust Presentation

This repository contains a reveal.js presentation about asynchronous programming in Python and Rust, with a focus on genetic algorithms as a practical example.

## Setup Instructions

1. Clone this repository:
```bash
git clone https://github.com/<username>/parallel.git
cd parallel/slides
```

2. Create an `images` directory and add the following images:
- `tokio-event-loop.png`
- `pypi-rust-growth.png`
- `concurrency-parallelism.png`
- `crossover-visualization.png`
- `parallel-fitness.png`
- `flame-graph.png`

3. Serve the presentation locally:
```bash
# Using Python's built-in HTTP server
python3 -m http.server 8000

# Or using Node.js
npx serve
```

4. Open your browser and navigate to:
```
http://localhost:8000
```

## Keyboard Shortcuts

- `Space` or `→`: Next slide
- `←`: Previous slide
- `↑`: Previous slide
- `↓`: Next slide
- `F`: Toggle fullscreen
- `B`: Toggle blackout
- `Esc`: Overview mode

## Features

- Responsive design
- Syntax highlighting for code blocks
- Mermaid diagrams support
- Custom styling
- Keyboard navigation
- Progress bar
- Slide numbers
- Fragment animations

## Dependencies

- reveal.js 4.5.0
- highlight.js
- mermaid.js

All dependencies are loaded from CDN in the `index.html` file.

## Deployment

To deploy to GitHub Pages:

1. Push your changes to the `main` branch
2. Enable GitHub Pages in your repository settings
3. Set the source to the `slides` directory

The presentation will be available at:
```
https://<username>.github.io/parallel
```

## License

This presentation is licensed under the MIT License. See the LICENSE file for details. 