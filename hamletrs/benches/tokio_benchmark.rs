use criterion::{criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 1,
        1 => 1,
        n => fibonacci(n-1) + fibonacci(n-2),
    }
}

fn criterion_benchmark(c: &mut Criterion) {
    let mut group = c.benchmark_group("fibonacci");
    group.significance_level(0.1).sample_size(10);
    group.bench_function("fib 20", |b| b.iter(|| fibonacci(20)));
    group.finish();
}

criterion_group! {
    name = benches;
    config = Criterion::default().with_profiler(criterion::profiler::FlamegraphProfiler::new(100));
    targets = criterion_benchmark
}
criterion_main!(benches);