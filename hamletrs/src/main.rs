use hamletrs::GeneticAlgorithm;
use hamletrs::Quote;

#[tokio::main]
async fn main() {
    // Parse command line arguments
    let args: Vec<String> = std::env::args().collect();
    let benchmark_mode = args.len() > 1 && args[1] == "--benchmark";

    // Example target text
    let target = "To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles, And by opposing end them.";

    let quotes = vec![
        Quote {
            text: "To be, or not to be".to_string(),
            speaker: "Hamlet".to_string(),
            act: 3,
            scene: 1,
            location: Some(0),
        },
        Quote {
            text: "that is the question".to_string(),
            speaker: "Hamlet".to_string(),
            act: 3,
            scene: 1,
            location: Some(21),
        },
    ];

    // Create and run the genetic algorithm
    let mut ga = GeneticAlgorithm::new(target, quotes);
    ga.evolve(benchmark_mode).await;
}
