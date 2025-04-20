import time
import json
import random
import sys
import timeit
from pathlib import Path
from hamlet_evolver import (
    evolve_text,
    evolve_text_processes,
    POPULATION_SIZE,
    MUTATION_RATE,
    SELECTION_PRESSURE,
    CROSSOVER_RATE
)

def benchmark_evolution(evolve_func, target_text, max_generations=3000):
    """Run a single benchmark of the evolution process."""
    # Create a function to benchmark that includes all setup
    def run_benchmark():
        random.seed(42)  # Reset seed for consistent results
        return evolve_func(
            target_text,
            population_size=POPULATION_SIZE,
            mutation_rate=MUTATION_RATE,
            selection_pressure=SELECTION_PRESSURE,
            crossover_rate=CROSSOVER_RATE,
            max_generations=max_generations,
            show_progress=False
        )
    
    # Run the benchmark multiple times and take the best time
    number = 1  # Number of times to run in a single timing
    repeat = 1  # Number of timings to perform
    
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

def run_benchmarks(use_full_text=False, input_file=None, text_length=None):
    """Run benchmarks for sequential and process based implementations."""
    # Set random seed for reproducibility
    random.seed(42)
    
    # Read target text
    if input_file:
        with open(input_file, 'r') as f:
            target_text = f.read()
    else:
        with open('hamlet_essential.txt', 'r') as f:
            target_text = f.read()
            if not use_full_text and not text_length:
                # Default to first 107 characters for essential
                target_text = target_text[:107]
    
    # Apply length if specified
    if text_length:
        target_text = target_text[:text_length]
    
    text_size = len(target_text)
    print(f"\nBenchmarking with text size {text_size}...")
    
    # Run sequential benchmark
    print("Running sequential benchmark...")
    sequential_results = benchmark_evolution(
        evolve_text,
        target_text
    )
    
    # Run process-based benchmark
    print("Running process-based benchmark...")
    process_results = benchmark_evolution(
        evolve_text_processes,
        target_text
    )
    
    # Store results
    results = {
        'sequential': sequential_results,
        'processes': process_results,
        'parameters': {
            'population_size': POPULATION_SIZE,
            'mutation_rate': MUTATION_RATE,
            'selection_pressure': SELECTION_PRESSURE,
            'crossover_rate': CROSSOVER_RATE
        }
    }
    
    # Print comparison
    print(f"\nResults for text size {text_size}:")
    print(f"Sequential: {sequential_results['time']:.2f}s, fitness: {sequential_results['fitness']:.3f}, generations: {sequential_results['generations']}")
    print(f"  All times: {[f'{t:.2f}s' for t in sequential_results['all_times']]}")
    print(f"Processes:  {process_results['time']:.2f}s, fitness: {process_results['fitness']:.3f}, generations: {process_results['generations']}")
    print(f"  All times: {[f'{t:.2f}s' for t in process_results['all_times']]}")
    print(f"Speedup:    {sequential_results['time']/process_results['time']:.2f}x")
    
    # Save results to file
    output_file = f"benchmark/results_{text_size}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Benchmark genetic algorithm implementations.')
    parser.add_argument('--file', help='Path to the target text file')
    parser.add_argument('--essential', action='store_true', help='Use hamlet_essential.txt')
    parser.add_argument('--length', type=int, help='Number of characters to use from the start of the file')
    parser.add_argument('--full', action='store_true', help='Use full hamlet_essential.txt (ignored if --file is specified)')
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.essential:
        parser.error("Either --file or --essential must be specified")
    if args.file and args.full:
        parser.error("--full can only be used with --essential")
    
    run_benchmarks(
        use_full_text=args.full,
        input_file=args.file,
        text_length=args.length
    ) 