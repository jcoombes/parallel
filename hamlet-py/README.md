# Hamlet Text Evolution

A genetic algorithm implementation for evolving text, with a focus on Shakespeare's Hamlet. The project includes both sequential and process-based parallel implementations, with benchmarking capabilities.

## Features

- **Text Evolution**: Evolve text using a genetic algorithm with configurable parameters
- **Parallel Processing**: Support for both sequential and process-based parallelization
- **Flexible Input**: Work with any text file or use the included Hamlet essential quotes
- **Configurable Length**: Target specific lengths of text (e.g., first k characters)
- **Benchmarking**: Compare performance between sequential and parallel implementations

## Files

- `hamlet_evolver.py`: Main genetic algorithm implementation
- `hamlet_quotes.py`: Contains Hamlet quotes and essential/non-essential flags
- `hamlet_essential.txt`: 128-character version of key Hamlet quotes
- `benchmark.py`: Benchmarking tool for comparing implementations
- `hamlet.txt`: Full text of Hamlet (for reference)

## Usage

### Text Evolution

Basic usage with hamlet_essential.txt (first 107 characters):
```bash
python hamlet_evolver.py --essential
```

Use full hamlet_essential.txt (128 characters):
```bash
python hamlet_evolver.py --essential --full
```

Use custom length from hamlet_essential.txt:
```bash
python hamlet_evolver.py --essential --length 100
```

Use any text file:
```bash
python hamlet_evolver.py --file hamlet.txt --length 128
```

Use process-based parallelization:
```bash
python hamlet_evolver.py --essential --processes
```

### Benchmarking

Benchmark first 107 characters of hamlet_essential.txt:
```bash
python benchmark.py --essential
```

Benchmark full hamlet_essential.txt:
```bash
python benchmark.py --essential --full
```

Benchmark custom length from hamlet_essential.txt:
```bash
python benchmark.py --essential --length 100
```

Benchmark any text file:
```bash
python benchmark.py --file hamlet.txt --length 128
```

## Parameters

The genetic algorithm uses the following parameters:
- Population Size: 900
- Mutation Rate: 0.06
- Selection Pressure: 0.15
- Crossover Rate: 0.75
- Fitness Threshold: 0.95

## Results

Benchmark results are saved in JSON format in the `benchmark` directory, named according to the text size used (e.g., `results_107.json`).

Each result file contains:
- Sequential implementation timing and results
- Process-based implementation timing and results
- Algorithm parameters used
- Fitness scores and generation counts
- Speedup comparison

## Implementation Details

The genetic algorithm:
1. Generates an initial population of random strings
2. Calculates fitness by comparing characters with the target
3. Selects top performers based on fitness
4. Creates new generation through crossover and mutation
5. Repeats until fitness threshold is reached

The process-based implementation:
- Uses Python's multiprocessing
- Splits population into chunks for parallel fitness calculation
- Maintains same genetic algorithm logic as sequential version
