import random
import string
import sys
import multiprocessing
from tqdm import tqdm
from hamlet_evolver import (
    generate_hamlet_string,
    calculate_hamlet_fitness_for_target,
    mutate_hamlet_static,
    crossover_hamlet
)

def evolve_text(target_text, population_size=100, mutation_rate=0.1, selection_pressure=0.1, crossover_rate=0.7, max_generations=None, show_progress=True):
    """
    Process-based parallel version of the genetic algorithm.
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
        # Calculate fitness for each candidate in parallel using processes
        with multiprocessing.Pool() as pool:
            fitness_scores = list(zip(
                population,
                pool.starmap(
                    calculate_hamlet_fitness_for_target,
                    [(p, target_text) for p in population]
                )
            ))
        
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
            
            child = mutate_hamlet_static(child, mutation_rate)
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