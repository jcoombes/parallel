use rand::{Rng, SeedableRng};
use rand::rngs::SmallRng;
use std::sync::Arc;
use std::time::Instant;
use tokio::sync::{Mutex, mpsc};
use tokio::task::JoinSet;
use num_cpus;

// Characters allowed in the genetic string
const CHARSET: &[u8] =
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.!?;:'\"()-";

// Genetic algorithm parameters
const POPULATION_SIZE: usize = 1000;
const BASE_MUTATION_RATE: f64 = 0.02;
const FITNESS_THRESHOLD: f64 = 0.95;
const TOURNAMENT_SIZE: usize = 5;

// Using a static mutation rate instead of dynamic rate based on fitness
#[derive(Clone)]
pub struct Individual {
    genes: Vec<u8>,
    fitness: f64,
}

impl Individual {
    pub fn new_random(length: usize) -> Self {
        let mut rng = SmallRng::seed_from_u64(rand::random::<u64>());
        let genes = (0..length)
            .map(|_| CHARSET[rng.random_range(0..CHARSET.len())])
            .collect();
        Self {
            genes,
            fitness: 0.0,
        }
    }

    pub fn calculate_fitness(&mut self, target: &[u8]) -> f64 {
        let matches = self
            .genes
            .iter()
            .zip(target)
            .filter(|&(a, b)| a == b)
            .count();
        self.fitness = matches as f64 / target.len() as f64;
        self.fitness
    }

    pub fn crossover(&self, other: &Self) -> Self {
        let mut rng = SmallRng::seed_from_u64(rand::random::<u64>());
        let split_point = rng.random_range(0..self.genes.len());

        let mut child_genes = Vec::with_capacity(self.genes.len());
        child_genes.extend_from_slice(&self.genes[0..split_point]);
        child_genes.extend_from_slice(&other.genes[split_point..]);

        Self {
            genes: child_genes,
            fitness: 0.0,
        }
    }

    pub fn mutate(&mut self, mutation_rate: f64) {
        let mut rng = SmallRng::seed_from_u64(rand::random::<u64>());
        for gene in &mut self.genes {
            if rng.random_range(0.0..1.0) < mutation_rate {
                *gene = CHARSET[rng.random_range(0..CHARSET.len())];
            }
        }
    }
}

// A structure to help visualize quotes in the evolving text
pub struct Quote {
    pub text: String,
    pub speaker: String,
    pub act: u8,
    pub scene: u8,
    pub location: Option<usize>,
}

impl Quote {
    pub fn format_excerpt(&self, candidate: &[u8], window_size: usize) -> String {
        if self.location.is_none() {
            return format!(
                "{} (Act {} Scene {}): [Not found]",
                self.speaker, self.act, self.scene
            );
        }

        let location = self.location.unwrap();
        let start = location.saturating_sub(window_size);
        let end = (location + self.text.len() + window_size).min(candidate.len());

        // Build the context string with highlighting
        let mut result = format!("{} (Act {} Scene {}): ", self.speaker, self.act, self.scene);

        for i in start..end {
            let c = candidate[i] as char;
            if i >= location && i < location + self.text.len() {
                // Check if character matches the target
                let target_idx = i - location;
                if target_idx < self.text.len() && c == self.text.chars().nth(target_idx).unwrap() {
                    result.push_str(&format!("\x1B[32m{}\x1B[0m", c)); // Green for correct
                } else {
                    result.push(c);
                }
            } else {
                result.push(c);
            }
        }

        result
    }
}

// Main genetic algorithm
pub struct GeneticAlgorithm {
    target: Vec<u8>,
    population: Vec<Individual>,
    best_fitness: f64,
    generation: usize,
    quotes: Vec<Quote>,
}

impl GeneticAlgorithm {
    pub fn new(target_text: &str, quotes: Vec<Quote>) -> Self {
        let target = target_text.as_bytes().to_vec();
        let population = (0..POPULATION_SIZE)
            .map(|_| Individual::new_random(target.len()))
            .collect();

        Self {
            target,
            population,
            best_fitness: 0.0,
            generation: 0,
            quotes,
        }
    }

    // Parallel fitness calculation using Tokio tasks
    pub async fn calculate_fitness_parallel(&mut self) -> Vec<Individual> {
        let target = Arc::new(self.target.clone());
        let mut join_set = JoinSet::new();

        // Split population into chunks for each worker
        let chunks: Vec<Vec<Individual>> = self
            .population
            .chunks(self.population.len() / num_cpus::get().max(1))
            .map(|chunk| chunk.to_vec())
            .collect();

        // Process each chunk in parallel
        for chunk in chunks {
            let target_clone = Arc::clone(&target);
            join_set.spawn(async move {
                let mut results = Vec::with_capacity(chunk.len());
                for mut individual in chunk {
                    individual.calculate_fitness(&target_clone);
                    results.push(individual);
                }
                results
            });
        }

        // Collect results
        let mut all_results = Vec::with_capacity(self.population.len());
        while let Some(result) = join_set.join_next().await {
            if let Ok(chunk_results) = result {
                all_results.extend(chunk_results);
            }
        }

        all_results
    }

    // Tournament selection - more amenable to parallel processing
    pub async fn tournament_selection(&self, tournament_size: usize) -> Individual {
        let mut rng = SmallRng::seed_from_u64(rand::random::<u64>());
        let mut best = None;
        let mut best_fitness = -1.0;

        for _ in 0..tournament_size {
            let idx = rng.random_range(0..self.population.len());
            let candidate = &self.population[idx];
            if candidate.fitness > best_fitness {
                best_fitness = candidate.fitness;
                best = Some(candidate.clone());
            }
        }

        best.unwrap_or_else(|| self.population[0].clone())
    }

    // Main evolution loop using Tokio for parallelism
    pub async fn evolve(&mut self, benchmark_mode: bool) {
        if !benchmark_mode {
            println!("Starting evolution with {} CPUs", num_cpus::get());
            println!("Target length: {} characters", self.target.len());
        }

        let start_time = Instant::now();

        // Only setup progress reporting if not in benchmark mode
        let progress = if !benchmark_mode {
            Arc::new(Mutex::new(Vec::new()))
        } else {
            Arc::new(Mutex::new(Vec::new())) // Still create it but won't use it
        };

        // Channel for reporting updates (only used in visual mode)
        let (tx, mut rx) = mpsc::channel(100);

        // Spawn a task to handle progress updates (only in visual mode)
        if !benchmark_mode {
            let progress_clone = Arc::clone(&progress);
            tokio::spawn(async move {
                while let Some((generation, fitness)) = rx.recv().await {
                    let mut progress = progress_clone.lock().await;
                    progress.push((generation, fitness));

                    // Print current status
                    println!("Generation {}: Best fitness {:.4}", generation, fitness);

                    // Update quotes display if needed
                    // (left as an exercise - would need to implement find_quote_locations)
                }
            });
        }

        while self.best_fitness < FITNESS_THRESHOLD {
            // Calculate fitness for all individuals in parallel
            let mut population = self.calculate_fitness_parallel().await;

            // Sort by fitness
            population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());
            self.population = population;

            // Update best fitness
            self.best_fitness = self.population[0].fitness;

            // Report progress (only in visual mode)
            if !benchmark_mode {
                let _ = tx.send((self.generation, self.best_fitness)).await;
            }

            // Exit if we've reached the threshold
            if self.best_fitness >= FITNESS_THRESHOLD {
                break;
            }

            // Create next generation
            self.create_next_generation().await;
            self.generation += 1;
        }

        let duration = start_time.elapsed();

        // Only output the results if not in benchmark mode
        if !benchmark_mode {
            println!("\nEvolution completed in {:?}", duration);
            println!("Generations: {}", self.generation);
            println!("Final fitness: {:.4}", self.best_fitness);

            // Display the best individual
            let best = &self.population[0];
            println!("Best solution:");
            println!("{}", String::from_utf8_lossy(&best.genes));
        }
    }

    async fn create_next_generation(&mut self) {
        let mut new_population = Vec::with_capacity(POPULATION_SIZE);
        let mut rng = SmallRng::seed_from_u64(rand::random::<u64>());
        
        // Keep the best individual (elitism)
        new_population.push(self.population[0].clone());
        
        // Create the rest of the new population
        while new_population.len() < POPULATION_SIZE {
            let parent1 = self.select_parent(&mut rng);
            let parent2 = self.select_parent(&mut rng);
            let mut child = parent1.crossover(&parent2);
            child.mutate(BASE_MUTATION_RATE);
            new_population.push(child);
        }
        
        self.population = new_population;
    }

    pub async fn evolve_single_generation(&mut self) {
        // Calculate fitness for all individuals in parallel
        let mut population = self.calculate_fitness_parallel().await;

        // Sort by fitness
        population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());
        self.population = population;

        // Update best fitness
        self.best_fitness = self.population[0].fitness;

        // Create next generation
        self.create_next_generation().await;
        self.generation += 1;
    }

    fn select_parent(&self, rng: &mut SmallRng) -> Individual {
        let mut best = None;
        let mut best_fitness = -1.0;
        
        for _ in 0..TOURNAMENT_SIZE {
            let idx = rng.random_range(0..self.population.len());
            let candidate = &self.population[idx];
            if candidate.fitness > best_fitness {
                best_fitness = candidate.fitness;
                best = Some(candidate.clone());
            }
        }
        
        best.unwrap_or_else(|| self.population[0].clone())
    }
} 