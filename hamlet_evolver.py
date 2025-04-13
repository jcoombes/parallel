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

def is_valid_hamlet_character(char):
    return char in string.ascii_letters + string.punctuation + string.digits + string.whitespace

def validate_hamlet_string(text):
    invalid_chars = set()
    for char in text:
        if not is_valid_hamlet_character(char):
            invalid_chars.add(char)
    return len(invalid_chars) == 0, invalid_chars

def parse_hamlet_args():
    parser = argparse.ArgumentParser(description='Evolve Hamlet text using a genetic algorithm')
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

def get_hamlet_mutation_rate(fitness):
    """Get mutation rate from precomputed lookup table."""
    # Convert fitness to table index (0-1000)
    index = min(1000, max(0, int(fitness * 1000)))
    return MUTATION_RATE_TABLE[index]

# Create a fixed thread pool at module level
THREAD_POOL = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())

def generate_hamlet_string(length):
    """Generate a random string of given length."""
    return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace) for _ in range(length))

def calculate_hamlet_fitness(candidate):
    """Calculate fitness of a candidate against the target text."""
    if len(candidate) != len(TARGET):
        return 0.0
    matches = sum(1 for a, b in zip(candidate, TARGET) if a == b)
    return matches / len(TARGET)

def calculate_hamlet_fitness_parallel(population):
    """Calculate fitness for a population in parallel using threads."""
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(calculate_hamlet_fitness, candidate) for candidate in population]
        return [future.result() for future in futures]

def mutate_hamlet(candidate, current_fitness):
    """Mutate a candidate with dynamic mutation rate based on fitness."""
    mutation_rate = get_hamlet_mutation_rate(current_fitness)
    result = list(candidate)
    for i in range(len(result)):
        if random.random() < mutation_rate:
            result[i] = random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace)
    return ''.join(result)

def crossover_hamlet(parent1, parent2):
    """Perform crossover between two parents."""
    point = random.randint(0, len(parent1))
    return parent1[:point] + parent2[point:]

def format_hamlet_quote_excerpt(candidate: str, quote, window_size: int = 20) -> str:
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

def read_hamlet_target(file_path):
    """Read target text from file."""
    with open(file_path, 'r') as f:
        return f.read()

def evolve_hamlet(target_text, population_size=100, mutation_rate=0.1, selection_pressure=0.1, crossover_rate=0.7, max_generations=None, show_progress=True):
    """
    Evolve text using a genetic algorithm.
    Returns (best_candidate, fitness, generations)
    """
    # Initialize population
    population = [generate_hamlet_string(len(target_text)) for _ in range(population_size)]
    generation = 0
    best_fitness = 0.0
    
    # Create progress bar if requested
    pbar = None
    if show_progress:
        pbar = tqdm(file=sys.stderr, desc="Evolving text", position=0)
    
    while True:
        # Calculate fitness for each candidate
        fitness_scores = [(p, calculate_hamlet_fitness(p)) for p in population]
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
                child = crossover_hamlet(parent1, parent2)
            else:
                child = parent1
            
            # Apply static mutation rate
            child = mutate_hamlet_static(child, mutation_rate)
            new_population.append(child)
        
        population = new_population
        generation += 1

def calculate_hamlet_fitness_for_target(candidate, target):
    """Calculate fitness of a candidate against a specific target text."""
    if len(candidate) != len(target):
        return 0.0
    matches = sum(1 for a, b in zip(candidate, target) if a == b)
    return matches / len(target)

def mutate_hamlet_static(candidate, mutation_rate):
    """Mutate a candidate with a static mutation rate."""
    result = list(candidate)
    for i in range(len(result)):
        if random.random() < mutation_rate:
            result[i] = random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace)
    return ''.join(result)

def main():
    args = parse_hamlet_args()
    target_text = read_hamlet_target(args.file)
    best_candidate, fitness, generations = evolve_hamlet(
        target_text,
        population_size=POPULATION_SIZE,
        mutation_rate=BASE_MUTATION_RATE,
        selection_pressure=0.1,
        crossover_rate=0.7,
        max_generations=None,
        show_progress=True
    )
    print(f"\nTarget reached! Fitness: {fitness:.2f}")
    print(f"Generations: {generations}")
    print(f"Best candidate: {best_candidate}")

if __name__ == "__main__":
    main()
