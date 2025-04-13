import subprocess
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def generate_test_files():
    """Generate test files of different lengths from hamlet.txt."""
    with open('hamlet.txt', 'r') as f:
        text = f.read()
    
    # Create benchmark directory if it doesn't exist
    Path('benchmark').mkdir(exist_ok=True)
    
    # Generate files of increasing lengths (powers of 2)
    lengths = [2**i for i in range(4, 11)]  # From 16 bytes to 1024 bytes
    for length in lengths:
        test_text = text[:length]
        with open(f'benchmark/hamlet_{length}.txt', 'w') as f:
            f.write(test_text)
    
    return lengths

def run_benchmarks(lengths):
    """Run hyperfine benchmarks for each file length."""
    results = []
    
    for length in lengths:
        cmd = [
            'hyperfine',
            '--warmup', '1',
            '--runs', '3',
            f'python hello.py benchmark/hamlet_{length}.txt',
            '--export-json', f'benchmark/results_{length}.json'
        ]
        
        print(f"Running benchmark for length {length}...")
        subprocess.run(cmd)
        
        # Read results
        with open(f'benchmark/results_{length}.json') as f:
            result = json.load(f)
            results.append({
                'length': length,
                'mean_time': result['results'][0]['mean'],
                'stddev': result['results'][0]['stddev']
            })
    
    return results

def plot_results(results):
    """Plot the benchmark results."""
    lengths = [r['length'] for r in results]
    times = [r['mean_time'] for r in results]
    stddevs = [r['stddev'] for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(lengths, times, yerr=stddevs, fmt='o-', capsize=5)
    plt.xscale('log', base=2)
    plt.yscale('log')
    plt.xlabel('Input Length (bytes)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Algorithm Performance Scaling')
    plt.grid(True, which="both", ls="-")
    
    # Add complexity annotations
    x = np.array(lengths)
    y_linear = times[0] * x / x[0]
    y_quadratic = times[0] * (x / x[0])**2
    plt.plot(x, y_linear, 'r--', label='O(n)')
    plt.plot(x, y_quadratic, 'g--', label='O(n²)')
    plt.legend()
    
    plt.savefig('benchmark/scaling.png')
    plt.close()

def main():
    print("Generating test files...")
    lengths = generate_test_files()
    
    print("Running benchmarks...")
    results = run_benchmarks(lengths)
    
    print("Plotting results...")
    plot_results(results)
    
    print("\nResults summary:")
    for r in results:
        print(f"Length: {r['length']:8d} bytes | Time: {r['mean_time']:.3f} ± {r['stddev']:.3f} seconds")

if __name__ == "__main__":
    main() 