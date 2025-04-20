from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder(width, height, text, output_path):
    # Create a new image with a light gray background
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Add a border
    draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 200, 200))
    
    # Add text
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Center the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill=(100, 100, 100), font=font)
    
    # Save the image
    img.save(output_path)

# Create images directory if it doesn't exist
os.makedirs('images', exist_ok=True)

# Generate placeholder images
placeholders = {
    'tokio-event-loop.png': 'Tokio Event Loop Diagram',
    'pypi-rust-growth.png': 'PyPI Rust Growth Graph',
    'concurrency-parallelism.png': 'Concurrency vs Parallelism',
    'crossover-visualization.png': 'Crossover Visualization',
    'parallel-fitness.png': 'Parallel Fitness Calculation',
    'flame-graph.png': 'Flame Graph Comparison'
}

for filename, text in placeholders.items():
    create_placeholder(800, 600, text, f'images/{filename}')
    print(f'Created placeholder: {filename}') 