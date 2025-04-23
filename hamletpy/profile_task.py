def fibonacci(n: int) -> int:
    match n:
        case 0: return 1
        case 1: return 1
        case _: return fibonacci(n-1) + fibonacci(n-2)

def main():
    # Run continuously for profiling
    for _ in range(1000):
        result = fibonacci(20)

if __name__ == "__main__":
    main()