import timeit

def fibonacci(n: int) -> int:
    match n:
        case 0: return 1
        case 1: return 1
        case _: return fibonacci(n-1) + fibonacci(n-2)

def main():
    # Time the function with timeit
    number = 1000
    times: list[float] = timeit.repeat(
        stmt='fibonacci(20)', 
        setup='from __main__ import fibonacci',
        number=number,
        repeat=10
    )
    
    # Print statistics
    print(f"\nBenchmark results for fibonacci(20) x {number} iterations:")
    print(f"Mean time: {sum(times)/len(times):.6f} seconds")
    print(f"Best time: {min(times):.6f} seconds")
    print(f"Worst time: {max(times):.6f} seconds")


if __name__ == "__main__":
    main()