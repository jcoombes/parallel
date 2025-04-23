use criterion::{black_box, criterion_group, criterion_main, Criterion};
use hamletrs::GeneticAlgorithm;
use std::time::Duration;

fn benchmark_ga(c: &mut Criterion) {
    c.bench_function("genetic_algorithm", |b| {
        b.to_async(tokio::runtime::Runtime::new().unwrap())
            .iter(|| async {
                let target = "to be or not to be";
                let quotes = vec![];
                let mut ga = GeneticAlgorithm::new(target, quotes);
                black_box(ga.evolve(true).await);
            });
    });
}

criterion_group! {
    name = tokio_benches;
    config = Criterion::default()
        .measurement_time(Duration::from_secs(5))
        .warm_up_time(Duration::from_secs(1));
    targets = benchmark_ga
}

criterion_main!(tokio_benches);