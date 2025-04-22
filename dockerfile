FROM ubuntu:latest

# Install basic tools
RUN apt-get update && apt-get install -y build-essential curl git software-properties-common ca-certificates

# Add Deadsnakes PPA and install Python 3.13-nogil
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update
RUN apt-get install -y python3.13-nogil

# Install pip for Python 3.13-nogil
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13

# Create symbolic link for python3
RUN ln -sf /usr/bin/python3.13 /usr/local/bin/python3

# Install any Python packages your script might need
RUN pip3 install numpy pandas matplotlib anyio trio pyspy py-spy

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup default stable


# Global rust dependencies.

# Install cargo-edit for dependency management
RUN cargo install cargo-edit

# Set up project and dependencies
WORKDIR /code
RUN cargo init && \
    cargo add criterion tokio rayon --features tokio/full && \
    cargo build --release

WORKDIR /code