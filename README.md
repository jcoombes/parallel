# Parallel Text Evolution

A genetic algorithm that evolves text towards Shakespeare's Hamlet, with parallel processing capabilities.

## Getting Started

### Prerequisites

- Python 3.13.2 and 3.13.3t (GIL-free) installed via pyenv
- `uv` package manager

### Environment Setup

This project uses two Python environments to compare performance between GIL and GIL-free versions:

1. Create the environments:
```bash
# Create directory for virtual environments
mkdir -p ~/.venvs

# Create GIL-enabled environment (Python 3.13.2)
cd ~/.venvs
uv venv parallel-313 --python 3.13.2

# Create GIL-free environment (Python 3.13.3t)
uv venv parallel-313t --python 3.13.3t
```

2. Install dependencies in both environments:
```bash
# Install in GIL environment
source ~/.venvs/parallel-313/bin/activate
uv pip install tqdm python-Levenshtein
deactivate

# Install in GIL-free environment
source ~/.venvs/parallel-313t/bin/activate
uv pip install tqdm python-Levenshtein
deactivate
```

3. Switch between environments:
```bash
# Use GIL version
source ~/.venvs/parallel-313/bin/activate

# Use GIL-free version
source ~/.venvs/parallel-313t/bin/activate
```

### Running the Algorithm

// ... existing code ...
