import random
import string
import sys
import argparse
from tqdm import tqdm
from hamlet_quotes import QUOTES, find_quote_locations
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import threading

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
POPULATION_SIZE = 5000  # Increased from 1000
BASE_MUTATION_RATE = 0.02  # Base mutation rate
FITNESS_THRESHOLD = 0.95  # Stop when we reach 95% match

# Precompute mutation rate lookup table
MUTATION_RATE_TABLE = {}
for fitness in range(0, 1001):  # 0.000 to 1.000 in steps of 0.001
    f = fitness / 1000
    if f < 0.3:
        rate = BASE_MUTATION_RATE * 2
    elif f < 0.7:
        rate = BASE_MUTATION_RATE * (2 - (f - 0.3) / 0.4)
    else:
        rate = BASE_MUTATION_RATE * (1 - (f - 0.7) / 0.4)
    MUTATION_RATE_TABLE[fitness] = rate

def get_dynamic_mutation_rate(fitness):
    """Get mutation rate from precomputed lookup table."""
    # Convert fitness to table index (0-1000)
    index = min(1000, max(0, int(fitness * 1000)))
    return MUTATION_RATE_TABLE[index]

# Create a fixed thread pool at module level
THREAD_POOL = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace) for _ in range(length))

def calculate_fitness(candidate):
    """Calculate fitness by comparing characters at each position.
    Returns a score between 0 and 1."""
    matches = sum(1 for a, b in zip(candidate, TARGET) if a == b)
    return matches / len(TARGET)

def calculate_fitness_parallel(population):
    """Calculate fitness for all candidates in parallel using chunks."""
    # Use one chunk per CPU core
    chunk_size = len(population) // multiprocessing.cpu_count()
    chunks = [population[i:i + chunk_size] for i in range(0, len(population), chunk_size)]
    
    # Track thread usage
    active_threads = set()
    thread_count = [0]  # Use list to allow modification in nested scope
    
    def process_chunk(chunk):
        thread_id = threading.get_ident()
        active_threads.add(thread_id)
        thread_count[0] = len(active_threads)
        try:
            return [calculate_fitness(c) for c in chunk]
        finally:
            active_threads.remove(thread_id)
    
    # Use the fixed thread pool
    chunk_results = list(THREAD_POOL.map(process_chunk, chunks))
    print(f"\nThread usage:", file=sys.stderr)
    print(f"Maximum concurrent threads: {thread_count[0]}", file=sys.stderr)
    print(f"Number of chunks processed: {len(chunks)}", file=sys.stderr)
    
    # Flatten results
    return [score for chunk in chunk_results for score in chunk]

def mutate(candidate, current_fitness):
    """Mutate a candidate with dynamic mutation rate based on fitness."""
    mutation_rate = get_dynamic_mutation_rate(current_fitness)
    result = list(candidate)
    for i in range(len(result)):
        if random.random() < mutation_rate:
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

def read_target_text(file_path):
    """Read target text from file."""
    with open(file_path, 'r') as file:
        return file.read()

def evolve_text(target_text, population_size=100, mutation_rate=0.1, selection_pressure=0.1, crossover_rate=0.7, max_generations=None, show_progress=True):
    """
    Evolve text using a genetic algorithm.
    Returns (best_candidate, fitness, generations)
    """
    # Initialize population
    population = [generate_random_string(len(target_text)) for _ in range(population_size)]
    generation = 0
    best_fitness = 0.0
    
    # Create progress bar if requested
    pbar = None
    if show_progress:
        pbar = tqdm(file=sys.stderr, desc="Evolving text", position=0)
    
    while True:
        # Calculate fitness for each candidate
        fitness_scores = [(p, calculate_fitness_for_target(p, target_text)) for p in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get best candidate
        best_candidate, current_fitness = fitness_scores[0]
        best_fitness = max(best_fitness, current_fitness)
        
        # Update progress
        if pbar:
            pbar.update(1)
            pbar.set_postfix({'fitness': f'{best_fitness:.2f}', 'generation': generation})
        
        # Check termination conditions
        if best_fitness >= 0.95 or (max_generations and generation >= max_generations):
            if pbar:
                pbar.close()
            if show_progress:
                print(f"\nTarget reached! Fitness: {best_fitness:.2f}")
            return best_candidate, best_fitness, generation
        
        # Select top performers
        num_parents = int(population_size * selection_pressure)
        top_performers = [candidate for candidate, _ in fitness_scores[:num_parents]]
        
        # Create new generation
        new_population = []
        while len(new_population) < population_size:
            parent1 = random.choice(top_performers)
            if random.random() < crossover_rate:
                parent2 = random.choice(top_performers)
                child = crossover(parent1, parent2)
            else:
                child = parent1
            
            # Apply static mutation rate
            child = mutate_static(child, mutation_rate)
            new_population.append(child)
        
        population = new_population
        generation += 1

def calculate_fitness_for_target(candidate, target):
    """Calculate fitness by comparing characters at each position."""
    matches = sum(1 for a, b in zip(candidate, target) if a == b)
    return matches / len(target)

def mutate_static(candidate, mutation_rate):
    """Mutate a candidate with a static mutation rate."""
    result = list(candidate)
    for i in range(len(result)):
        if random.random() < mutation_rate:
            result[i] = random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace)
    return ''.join(result)

def main():
    args = parse_args()
    global TARGET, POPULATION_SIZE, BASE_MUTATION_RATE, FITNESS_THRESHOLD
    
    TARGET = read_target_text(args.file)
    POPULATION_SIZE = 5000
    BASE_MUTATION_RATE = 0.02
    FITNESS_THRESHOLD = 0.95  # Stop when we reach 95% match

    # Print system information
    cpu_count = multiprocessing.cpu_count()
    chunk_size = POPULATION_SIZE // cpu_count
    num_chunks = (POPULATION_SIZE + chunk_size - 1) // chunk_size  # Ceiling division
    
    print(f"\nSystem Information:", file=sys.stderr)
    print(f"CPU cores: {cpu_count}", file=sys.stderr)
    print(f"Population size: {POPULATION_SIZE}", file=sys.stderr)
    print(f"Chunk size: {chunk_size}", file=sys.stderr)
    print(f"Number of chunks: {num_chunks}", file=sys.stderr)
    print(f"Individuals per chunk: {POPULATION_SIZE/num_chunks:.1f}", file=sys.stderr)

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
        # Calculate fitness for each candidate in parallel
        fitness_scores = list(zip(population, calculate_fitness_parallel(population)))
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
            child = mutate(child, best_fitness)  # Pass current best fitness for dynamic mutation
            new_population.append(child)
        
        population = new_population
        generation += 1
        pbar.update(1)
        pbar.set_postfix({'fitness': f'{best_fitness:.2f}'})
    
    pbar.close()

if __name__ == "__main__":
    main()
