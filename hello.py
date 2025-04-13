import random
import string
import sys
import argparse
from tqdm import tqdm
from hamlet_quotes import QUOTES, find_quote_locations
from Levenshtein import distance

def read_hamlet(file_path='hamlet.txt'):
    with open(file_path, 'r') as file:
        return file.read()

def is_valid_character(char):
    return char in string.ascii_letters + string.punctuation + string.digits + string.whitespace

def validate_string(text):
    invalid_chars = set()
    for char in text:
        if not is_valid_character(char):
            invalid_chars.add(char)
    return len(invalid_chars) == 0, invalid_chars

def parse_args():
    parser = argparse.ArgumentParser(description='Evolve text using a genetic algorithm')
    parser.add_argument('file', nargs='?', default='hamlet.txt', help='Input text file to evolve')
    return parser.parse_args()

TARGET = read_hamlet()
POPULATION_SIZE = 100
MUTATION_RATE = 0.01
FITNESS_THRESHOLD = 0.95  # Stop when we reach 95% match

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace) for _ in range(length))

def calculate_fitness(candidate):
    """Calculate fitness by comparing characters at each position.
    Returns a score between 0 and 1."""
    matches = sum(1 for a, b in zip(candidate, TARGET) if a == b)
    return matches / len(TARGET)

def mutate(candidate):
    result = list(candidate)
    for i in range(len(result)):
        if random.random() < MUTATION_RATE:
            result[i] = random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace)
    return ''.join(result)

def crossover(parent1, parent2):
    split_point = random.randint(0, len(parent1))
    child = parent1[:split_point] + parent2[split_point:]
    return child

def format_quote_excerpt(candidate: str, quote, window_size: int = 20) -> str:
    """Format a quote excerpt with context, showing correct characters in green."""
    if quote.location is None:
        return f"{quote.speaker} (Act {quote.act} Scene {quote.scene}): [Not found]"
    
    start = max(0, quote.location - window_size)
    end = min(len(candidate), quote.location + len(quote.text) + window_size)
    context = candidate[start:end]
    
    # Highlight correct characters
    highlighted = []
    for i, char in enumerate(context):
        pos = start + i
        if quote.location <= pos < quote.location + len(quote.text):
            target_char = TARGET[pos] if pos < len(TARGET) else ''
            if char == target_char:
                highlighted.append(f"\033[32m{char}\033[0m")  # Green for correct
            else:
                highlighted.append(char)
        else:
            highlighted.append(char)
    
    return f"{quote.speaker} (Act {quote.act} Scene {quote.scene}): {''.join(highlighted)}"

def main():
    args = parse_args()
    global TARGET, POPULATION_SIZE, MUTATION_RATE, FITNESS_THRESHOLD
    
    TARGET = read_hamlet(args.file)
    POPULATION_SIZE = 100
    MUTATION_RATE = 0.01
    FITNESS_THRESHOLD = 0.95  # Stop when we reach 95% match

    # Validate target string
    is_valid, invalid_chars = validate_string(TARGET)
    if not is_valid:
        print("Error: Target string contains invalid characters:", file=sys.stderr)
        for char in sorted(invalid_chars):
            print(f"Character: '{char}' (Unicode: U+{ord(char):04X})", file=sys.stderr)
        return

    # Initialize population
    population = [generate_random_string(len(TARGET)) for _ in range(POPULATION_SIZE)]
    generation = 0
    best_fitness = 0.0
    
    # Create progress bar that writes to stderr
    pbar = tqdm(file=sys.stderr, desc="Evolving text", position=0)
    
    # Print initial quote headers
    print("\n" * len(QUOTES), file=sys.stderr)  # Make space for quotes
    quote_lines = [""] * len(QUOTES)
    
    while best_fitness < FITNESS_THRESHOLD:
        # Calculate fitness for each candidate
        fitness_scores = [(candidate, calculate_fitness(candidate)) for candidate in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get best candidate
        best_candidate, best_fitness = fitness_scores[0]
        
        # Update quote displays
        found_quotes = find_quote_locations(best_candidate)
        for i, quote in enumerate(QUOTES):
            new_line = format_quote_excerpt(best_candidate, quote)
            if new_line != quote_lines[i]:
                quote_lines[i] = new_line
                # Move cursor up and print new line
                print(f"\033[{len(QUOTES)-i}A\033[K{new_line}", file=sys.stderr)
                print("\033[K", file=sys.stderr)  # Clear to end of line
        
        if best_fitness >= FITNESS_THRESHOLD:
            print(f"\nTarget reached! Fitness: {best_fitness:.2f}", file=sys.stderr)
            break
        
        # Select top performers
        top_performers = [candidate for candidate, _ in fitness_scores[:POPULATION_SIZE//2]]
        
        # Create new generation
        new_population = []
        while len(new_population) < POPULATION_SIZE:
            parent1 = random.choice(top_performers)
            parent2 = random.choice(top_performers)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        
        population = new_population
        generation += 1
        pbar.update(1)
        pbar.set_postfix({'fitness': f'{best_fitness:.2f}'})
    
    pbar.close()

if __name__ == "__main__":
    main()
