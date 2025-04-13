import re
from dataclasses import dataclass
from typing import List, Optional
import sys

@dataclass
class Quote:
    text: str
    speaker: str
    act: int
    scene: int
    location: Optional[int] = None  # Will store the index where the quote starts in the text

QUOTES = [
    Quote(
        "O that this too too solid flesh would melt",
        "Hamlet",
        1, 2
    ),
    Quote(
        "Neither a borrower nor a lender be",
        "Polonius",
        1, 3
    ),
    Quote(
        "Something is rotten in the state of Denmark",
        "Marcellus",
        1, 4
    ),
    Quote(
        "Brevity is the soul of wit",
        "Hamlet",
        3, 1
    ),
    Quote(
        "To be, or not to be, that is the question",
        "Hamlet",
        3, 1
    ),
    Quote(
        "Alas, poor Yorick! I knew him, Horatio",
        "Hamlet",
        5, 1
    ),
    Quote(
        "The rest is silence",
        "Hamlet",
        5, 2
    ),
    Quote(
        "Goodnight sweet prince",
        "Hamlet",
        5, 2
    )
]

def find_quote_locations(text: str) -> List[Quote]:
    """Find the locations of all quotes in the given text."""
    found_quotes = []
    
    for quote in QUOTES:
        # Clean the quote text for searching (remove extra spaces, normalize quotes)
        search_text = re.sub(r'\s+', ' ', quote.text).strip()
        
        # Create base pattern with flexible punctuation
        base_pattern = re.escape(search_text)
        base_pattern = base_pattern.replace(r'\ ', r'\s+')  # Flexible whitespace
        base_pattern = base_pattern.replace(r'\!', r'[!]*')  # Optional exclamation
        base_pattern = base_pattern.replace(r'\?', r'[?]*')  # Optional question mark
        base_pattern = base_pattern.replace(r'\,', r'[,]*')  # Optional comma
        base_pattern = base_pattern.replace(r'\.', r'[.]*')  # Optional period
        base_pattern = base_pattern.replace(r'\:', r'[:]*')  # Optional colon
        base_pattern = base_pattern.replace(r'\;', r'[;]*')  # Optional semicolon
        
        # Try the base pattern
        match = re.search(base_pattern, text, re.IGNORECASE)
        if match:
            quote.location = match.start()
            found_quotes.append(quote)
            continue
        
        # If no match, try with just the key words (strip punctuation)
        key_words = re.sub(r'[^\w\s]', '', search_text)
        if len(key_words.split()) > 2:  # Only try if we have at least 3 words
            pattern = r'\s+'.join(re.escape(word) for word in key_words.split())
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                quote.location = match.start()
                found_quotes.append(quote)
    
    return found_quotes

def get_quote_at_position(text: str, position: int) -> Optional[Quote]:
    """Get the quote that contains the given position in the text."""
    for quote in find_quote_locations(text):
        if quote.location is not None and quote.location <= position < quote.location + len(quote.text):
            return quote
    return None

def format_quote(quote: Quote) -> str:
    """Format a quote for display."""
    return f'"{quote.text}"\n({quote.speaker}, Act {quote.act} Scene {quote.scene})'

def peek_quotes(text: str, window_size: int = 50) -> List[str]:
    """Find quotes in the text and return just the quote text, one per line."""
    found_quotes = find_quote_locations(text)
    # Sort by act and scene
    found_quotes.sort(key=lambda q: (q.act, q.scene))
    return [quote.text for quote in found_quotes if quote.location is not None]

def main():
    if len(sys.argv) != 2:
        print("Usage: python hamlet_quotes.py <text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as file:
            text = file.read()
        
        quotes = peek_quotes(text)
        print("\n".join(quotes))
            
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    main() 