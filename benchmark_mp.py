import time
import json
import random
import sys
import string
import timeit
from pathlib import Path
from hello_mp import evolve_text as evolve_text_processes
from hello import calculate_fitness_for_target
from tqdm import tqdm

def generate_random_string(length):
    """Generate a random string of given length."""
    return ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits + string.whitespace) for _ in range(length))

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

def evolve_text_sequential(target_text, population_size=100, mutation_rate=0.1, selection_pressure=0.1, crossover_rate=0.7, max_generations=None, show_progress=True):
    """
    Sequential version of the genetic algorithm with no concurrency.
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
        # Calculate fitness for each candidate sequentially
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
            
            child = mutate(child, mutation_rate)
            new_population.append(child)
        
        population = new_population
        generation += 1

def benchmark_evolution(evolve_func, target_text, population_size, mutation_rate, selection_pressure, crossover_rate, max_generations=3000):
    """Run a single benchmark of the evolution process."""
    # Create a function to benchmark that includes all setup
    def run_benchmark():
        random.seed(42)  # Reset seed for consistent results
        return evolve_func(
            target_text,
            population_size=population_size,
            mutation_rate=mutation_rate,
            selection_pressure=selection_pressure,
            crossover_rate=crossover_rate,
            max_generations=max_generations,
            show_progress=False
        )
    
    # Run the benchmark multiple times and take the best time
    number = 1  # Number of times to run in a single timing
    repeat = 1  # Number of timings to perform (changed from 3 to 1)
    
    # Time the function
    times = timeit.repeat(
        lambda: run_benchmark(),
        number=number,
        repeat=repeat
    )
    
    # Get the results from one final run to capture fitness and generations
    best_candidate, fitness, generations = run_benchmark()
    
    return {
        'time': min(times),  # Best time from all runs
        'fitness': fitness,
        'generations': generations,
        'best_candidate': best_candidate,
        'all_times': times  # Store all times for analysis
    }

def run_benchmarks():
    """Run benchmarks for sequential and process based implementations."""
    # Set random seed for reproducibility
    random.seed(42)
    
    # Test only text size 128
    text_sizes = [128]
    results = {}
    
    # Use optimized parameters from hyperparameter search (rounded to nice values)
    population_size = 900  # from 895
    mutation_rate = 0.06   # from 0.060
    selection_pressure = 0.15  # from 0.143
    crossover_rate = 0.75  # from 0.756
    
    for size in text_sizes:
        print(f"\nBenchmarking with text size {size}...")
        target_file = f"benchmark/hamlet_{size}.txt"
        
        # Read target text
        with open(target_file, 'r') as f:
            target_text = f.read()
        
        # Run sequential benchmark
        print("Running sequential benchmark...")
        sequential_results = benchmark_evolution(
            evolve_text_sequential,
            target_text,
            population_size,
            mutation_rate,
            selection_pressure,
            crossover_rate
        )
        
        # Run process-based benchmark
        print("Running process-based benchmark...")
        process_results = benchmark_evolution(
            evolve_text_processes,
            target_text,
            population_size,
            mutation_rate,
            selection_pressure,
            crossover_rate
        )
        
        # Store results
        results[size] = {
            'sequential': sequential_results,
            'processes': process_results,
            'parameters': {
                'population_size': population_size,
                'mutation_rate': mutation_rate,
                'selection_pressure': selection_pressure,
                'crossover_rate': crossover_rate
            }
        }
        
        # Print comparison
        print(f"\nResults for text size {size}:")
        print(f"Sequential: {sequential_results['time']:.2f}s, fitness: {sequential_results['fitness']:.3f}, generations: {sequential_results['generations']}")
        print(f"  All times: {[f'{t:.2f}s' for t in sequential_results['all_times']]}")
        print(f"Processes:  {process_results['time']:.2f}s, fitness: {process_results['fitness']:.3f}, generations: {process_results['generations']}")
        print(f"  All times: {[f'{t:.2f}s' for t in process_results['all_times']]}")
        print(f"Speedup:    {sequential_results['time']/process_results['time']:.2f}x")
    
    # Save results to file
    output_file = "benchmark/results_sequential_vs_process.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    run_benchmarks() 