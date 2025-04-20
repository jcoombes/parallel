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
        "O, that this too, too solid flesh would melt, Thaw and resolve itself into a dew!",
        "Hamlet",
        1, 2
    ),
    Quote(
        "Neither a borrower nor a lender be, For loan oft loses both itself and friend, And borrowing dulls the edge of husbandry.",
        "Polonius",
        1, 3
    ),
    Quote(
        "though I am native here And to the manner born, it is a custom More honoured in the breach than the observance.",
        "Hamlet",
        1, 4
    ),
    Quote(
        "Something is rotten in the state of Denmark.",
        "Marcellus",
        1, 4
    ),
    Quote(
        "That one may smile and smile and be a villain.",
        "Hamlet",
        1, 5
    ),
    Quote(
        "There are more things in heaven and earth, Horatio, Than are dreamt of in our philosophy.",
        "Hamlet",
        1, 5
    ),
    Quote(
        "Brevity is the soul of wit.",
        "Polonius",
        2, 2
    ),
    Quote(
        "Though this be madness, yet there is method in't.",
        "Polonius",
        2, 2
    ),
    Quote(
        "There is nothing either good or bad but thinking makes it so.",
        "Hamlet",
        2, 2
    ),
    Quote(
        "O, what a rogue and peasant slave am I!",
        "Hamlet",
        2, 2
    ),
    Quote(
        "To be, or not to be, that is the question.",
        "Hamlet",
        3, 1
    ),
    Quote(
        "The lady protests too much, methinks.",
        "Gertrude",
        3, 2
    ),
    Quote(
        "How all occasions do inform against me, and spur my dull revenge.",
        "Hamlet",
        4, 3
    ),
    Quote(
        "Alas, poor Yorick! I knew him, Horatio: A fellow of infinite jest.",
        "Hamlet",
        5, 1
    ),
    Quote(
        "If it be now, 'tis not to come: if it be not to come, it will be now: if it be not now, yet it will come: the readiness is all.",
        "Hamlet",
        5, 2
    ),
    Quote(
        "The rest is silence.",
        "Hamlet",
        5, 2
    ),
    Quote(
        "Goodnight, sweet prince, And flights of angels sing thee to thy rest!",
        "Horatio",
        5, 2
    )
]

def find_quote_locations(text: str) -> List[Quote]:
    """Find the locations of all quotes in the given text."""
    found_quotes = []
    
    for quote in QUOTES:
        # Clean the quote text for searching (remove extra spaces, normalize quotes)
        search_text = re.sub(r'\s+', ' ', quote.text).strip()
        # Create a regex pattern that's more flexible with whitespace and punctuation
        pattern = re.escape(search_text)
        pattern = pattern.replace(r'\ ', r'\s+')  # Allow any whitespace between words
        pattern = pattern.replace(r'\?', r'\?')   # Make punctuation optional
        pattern = pattern.replace(r'\!', r'\!')
        pattern = pattern.replace(r'\.', r'\.')
        pattern = pattern.replace(r'\,', r'\,')
        
        # Search for the pattern
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quote.location = match.start()
            found_quotes.append(quote)
    
    return sorted(found_quotes, key=lambda q: q.location)

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
    """Find quotes in the text and return formatted strings showing the context around each quote."""
    found_quotes = find_quote_locations(text)
    results = []
    
    for quote in found_quotes:
        if quote.location is not None:
            start = max(0, quote.location - window_size)
            end = min(len(text), quote.location + len(quote.text) + window_size)
            context = text[start:end]
            results.append(f"Found quote at position {quote.location}:\n{context}\n{format_quote(quote)}\n")
    
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python hamlet_quotes.py <text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as file:
            text = file.read()
        
        quotes = peek_quotes(text)
        if quotes:
            print("\n".join(quotes))
        else:
            print("No famous quotes found in the text.")
            
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    main() 