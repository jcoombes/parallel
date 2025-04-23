#!/bin/bash
# profile_in_docker.sh

# Define colors
RUST_COLOR='\033[38;5;208m'  # Orange
PYTHON_COLOR='\033[38;5;40m'  # Green
RESET='\033[0m'              # Reset color

echo "python --version"
python3.13t --version
echo "python3.13t -c \"import sys; print(sys._is_gil_enabled())\""
python3.13t -c "import sys; print(sys._is_gil_enabled())"

echo "Starting profiling..."

# Profile Rust code
echo -e "${RUST_COLOR}Profiling Rust code...${RESET}"
cd /code/hamletrs
. $HOME/.cargo/env
cargo criterion 2>&1 || echo -e "${RUST_COLOR}Rust benchmarking failed with error: $?${RESET}"
cp -r target/criterion/* /code/flamegraphs/ 2>&1 || echo -e "${RUST_COLOR}No criterion results to copy. Error: $?${RESET}"

# Profile Python code
echo -e "${PYTHON_COLOR}Profiling Python code...${RESET}"
cd /code/hamletpy

# Run timing benchmark
echo -e "${PYTHON_COLOR}Running Python timing benchmark...${RESET}"
python3.13t timeit_benchmark.py | tee /code/flamegraphs/python_timing.txt 2>&1 || echo -e "${PYTHON_COLOR}Python benchmark failed with error: $?${RESET}"

# Generate flamegraph
echo -e "${PYTHON_COLOR}Generating Python flamegraph...${RESET}"
py-spy record --subprocesses --idle --rate 100 -o /code/flamegraphs/python_profile.svg python3.13t profile_task.py 2>&1 || echo -e "${PYTHON_COLOR}Python profiling failed with error: $?${RESET}"

# Ensure correct permissions for output files
chmod -R 777 /code/flamegraphs 2>&1 || echo "Failed to set permissions with error: $?"

echo "Profiling complete. Check /code/flamegraphs for results."