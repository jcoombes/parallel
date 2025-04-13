import numpy as np
from scipy.optimize import differential_evolution
from hello import evolve_text, read_target_text
import contextlib
import io
import sys

def objective(params):
    """Objective function to minimize (negative of fitness)."""
    population_size, mutation_rate, selection_pressure, crossover_rate = params
    
    # Convert parameters to appropriate ranges
    population_size = int(population_size * 900) + 100  # 100-1000
    mutation_rate = mutation_rate * 0.15 + 0.05  # 0.05-0.2
    selection_pressure = selection_pressure * 0.1 + 0.1  # 0.1-0.2
    crossover_rate = crossover_rate * 0.2 + 0.6  # 0.6-0.8
    
    # Suppress output during evolution
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        _, fitness, _ = evolve_text(
            read_target_text("benchmark/hamlet_64.txt"),
            population_size=population_size,
            mutation_rate=mutation_rate,
            selection_pressure=selection_pressure,
            crossover_rate=crossover_rate,
            max_generations=2000,
            show_progress=False
        )
    
    # Print current parameters and score
    print(f"Params: pop={population_size}, mut={mutation_rate:.3f}, sel={selection_pressure:.3f}, cross={crossover_rate:.3f}, score={fitness:.3f}")
    
    return -fitness  # Minimize negative fitness

# Define bounds for each parameter
bounds = [
    (0, 1),  # population_size (scaled)
    (0, 1),  # mutation_rate (scaled)
    (0, 1),  # selection_pressure (scaled)
    (0, 1),  # crossover_rate (scaled)
]

# Run optimization
result = differential_evolution(
    objective,
    bounds,
    maxiter=10,  # Fewer iterations
    popsize=5,   # Smaller population
    mutation=(0.5, 1.0),
    recombination=0.7,
    seed=42
)

# Print results
print("\nOptimization Results:")
print(f"Best parameters:")
print(f"Population size: {int(result.x[0] * 900) + 100}")
print(f"Mutation rate: {result.x[1] * 0.15 + 0.05:.3f}")
print(f"Selection pressure: {result.x[2] * 0.1 + 0.1:.3f}")
print(f"Crossover rate: {result.x[3] * 0.2 + 0.6:.3f}")
print(f"Best fitness: {-result.fun:.3f}") 