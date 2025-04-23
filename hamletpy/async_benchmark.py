def fibonacci(n: int) -> int:
    match n:
        case 0: return 1
        case 1: return 1
        case _: return fibonacci(n-1) + fibonacci(n-2)

def main():
    # Match the Rust benchmark by calculating fib(20) repeatedly
    for _ in range(10_000):  # Add some iterations to make it measurable
        result = fibonacci(25)
    


if __name__ == "__main__":
    main()