from .hamlet_evolver import (
    evolve_hamlet_sequential,
    evolve_hamlet_processes,
    POPULATION_SIZE,
    MUTATION_RATE,
    SELECTION_PRESSURE,
    CROSSOVER_RATE,
    FITNESS_THRESHOLD,
)
from .hamlet_quotes import get_quotes, get_essential_quotes

__all__ = [
    'evolve_hamlet_sequential',
    'evolve_hamlet_processes',
    'get_quotes',
    'get_essential_quotes',
    'POPULATION_SIZE',
    'MUTATION_RATE',
    'SELECTION_PRESSURE',
    'CROSSOVER_RATE',
    'FITNESS_THRESHOLD',
]

__version__ = '0.1.0' 