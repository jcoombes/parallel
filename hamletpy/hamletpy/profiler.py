import cProfile
import pstats
from pathlib import Path
from hamlet_evolver import evolve_text, evolve_text_processes
from benchmark import benchmark_evolution

def profile_evolution():
    # Read the essential hamlet text
    target_text = Path('hamlet_essential.txt').read_text()[:107]  # First 107 characters
    
    # Create benchmark directory if it doesn't exist
    Path('benchmark').mkdir(exist_ok=True)
    
    # Profile sequential version
    print("Profiling sequential evolution...")
    profiler = cProfile.Profile()
    profiler.enable()
    benchmark_evolution(evolve_text, target_text)
    profiler.disable()
    
    # Save sequential stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.dump_stats('benchmark/sequential_profile.prof')
    
    # Profile process-based version
    print("Profiling process-based evolution...")
    profiler = cProfile.Profile()
    profiler.enable()
    benchmark_evolution(evolve_text_processes, target_text)
    profiler.disable()
    
    # Save process-based stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.dump_stats('benchmark/processes_profile.prof')
    
    print("\nProfile data saved to:")
    print("- benchmark/sequential_profile.prof")
    print("- benchmark/processes_profile.prof")
    print("\nTo view the profiles, you can use:")
    print("python -m pstats benchmark/sequential_profile.prof")
    print("python -m pstats benchmark/processes_profile.prof")

if __name__ == "__main__":
    profile_evolution() 