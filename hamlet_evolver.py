import random
import string
import sys
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def read_hamlet(file_path='hamlet.txt'):
    with open(file_path, 'r') as file:
        return file.read()

def parse_hamlet_args():
    parser = argparse.ArgumentParser(description='Evolve Hamlet text using a genetic algorithm')
    parser.add_argument('file', nargs='?', default='hamlet.txt', help='Input text file to evolve')
    return parser.parse_args()

TARGET = read_hamlet()
POPULATION_SIZE = 5000  # Increased from 1000
BASE_MUTATION_RATE = 0.02  # Base mutation rate
FITNESS_THRESHOLD = 0.95  # Stop when we reach 95% match

def generate_hamlet_string(length):
    """Generate a random string of given length."""
    return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace) for _ in range(length))

def calculate_hamlet_fitness(candidate):
    """Calculate fitness of a candidate against the target text."""
    if len(candidate) != len(TARGET):
        return 0.0
    matches = sum(1 for a, b in zip(candidate, TARGET) if a == b)
    return matches / len(TARGET)

def mutate_hamlet(candidate, mutation_rate):
    """Mutate a candidate with a given mutation rate."""
    result = list(candidate)
    for i in range(len(result)):
        if random.random() < mutation_rate:
            result[i] = random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace)
    return ''.join(result)

def crossover_hamlet(parent1, parent2):
    """Perform crossover between two parents."""
    point = random.randint(0, len(parent1))
    return parent1[:point] + parent2[point:]

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
            
            child = mutate_hamlet(child, mutation_rate)
            new_population.append(child)
        
        population = new_population
        generation += 1

def calculate_hamlet_fitness_for_target(candidate, target):
    """Calculate fitness of a candidate against a specific target text."""
    if len(candidate) != len(target):
        return 0.0
    matches = sum(1 for a, b in zip(candidate, target) if a == b)
    return matches / len(target)

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
