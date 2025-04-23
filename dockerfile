# Stage 1: Set up environment and dependencies
FROM ubuntu:24.04 AS base

# Install basic tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    software-properties-common \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python Setup - Add Deadsnakes PPA and install Python 3.13-nogil
RUN add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y python3.13-nogil \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13t \
    && ln -sf /usr/bin/python3.13t /usr/local/bin/python3 \
    && python3.13t -m pip install numpy pandas matplotlib \
    anyio[trio,asyncio] trio tqdm py-spy

# Install Rust and cargo tools
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . $HOME/.cargo/env \
    && rustup default stable \
    && cargo install cargo-criterion cargo-edit

ENV PATH="/root/.cargo/bin:${PATH}"
ENV RUST_BACKTRACE=1
ENV PYTHONUNBUFFERED=1

# Stage 2: Build and compile code
FROM base AS builder

# Create directory structure
RUN mkdir -p /code/hamletpy /code/hamletrs /code/flamegraphs

# Copy your code maintaining structure
COPY ./hamletpy /code/hamletpy/
COPY ./hamletrs /code/hamletrs/

# Set up Rust project
WORKDIR /code/hamletrs
RUN . $HOME/.cargo/env && cargo build --release

# Compile Python
WORKDIR /code/hamletpy
RUN python3.13t -m compileall .

# Set permissions for output
WORKDIR /code
RUN chmod -R 777 flamegraphs

# Add the profiling script
COPY profile_in_docker.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Final stage
FROM builder AS final
ENTRYPOINT ["/usr/local/bin/start.sh"]