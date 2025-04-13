import random
import string
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def generate_random_string(length):
    """Generate a random string of given length."""
    return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace) for _ in range(length))

def calculate_fitness_batch(args):
    """Calculate fitness for a batch of candidates."""
    candidates, target = args
    return [(candidate, sum(1 for a, b in zip(candidate, target) if a == b) / len(target)) for candidate in candidates]

def mutate(candidate, mutation_rate):
    """Mutate a candidate with a given mutation rate."""
    result = list(candidate)
    for i in range(len(result)):
        if random.random() < mutation_rate:
            result[i] = random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace)
    return ''.join(result)

def crossover(parent1, parent2):
    """Perform crossover between two parents."""
    point = random.randint(0, len(parent1))
    return parent1[:point] + parent2[point:]

def read_target_text(file_path):
    """Read target text from file."""
    with open(file_path, 'r') as file:
        return file.read()

def evolve_text(target_text, population_size=100, mutation_rate=0.1, selection_pressure=0.1, crossover_rate=0.7, max_generations=None, show_progress=True):
    """
    Evolve text using a genetic algorithm with process-based parallelization.
    Returns (best_candidate, fitness, generations)
    """
    # Initialize population
    target_len = len(target_text)  # Pre-compute target length
    population = [generate_random_string(target_len) for _ in range(population_size)]
    generation = 0
    best_fitness = 0.0
    
    # Create progress bar if requested
    pbar = None
    if show_progress:
        pbar = tqdm(file=sys.stderr, desc="Evolving text", position=0)
    
    # Get number of CPU cores and adjust batch size
    num_cores = multiprocessing.cpu_count()
    # Use even fewer processes to reduce overhead
    num_processes = max(1, num_cores // 2)
    # Calculate larger batch size to ensure each process gets more work
    batch_size = max(50, population_size // num_processes)
    
    # Create a ProcessPoolExecutor with fixed number of processes
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        while True:
            # Split population into larger batches for parallel processing
            batches = [population[i:i + batch_size] for i in range(0, population_size, batch_size)]
            
            # Calculate fitness for each batch in parallel
            futures = [executor.submit(calculate_fitness_batch, (batch, target_text)) for batch in batches]
            
            # Combine results
            fitness_scores = []
            for future in futures:
                fitness_scores.extend(future.result())
            
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
                
                child = mutate(child, mutation_rate)
                new_population.append(child)
            
            population = new_population
            generation += 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Evolve text using a genetic algorithm with process-based parallelization.')
    parser.add_argument('file', help='Path to the target text file')
    args = parser.parse_args()
    
    target = read_target_text(args.file)
    best, fitness, gens = evolve_text(target) 