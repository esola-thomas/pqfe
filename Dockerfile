# Copyright (c) 2025 Ernesto Sola-Thomas
# Stage 1: Builder
FROM ubuntu:25.04 AS builder
ARG PYTHON_VERSION=3.10.16

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt update && apt install -y \
    cmake make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils \
    tk-dev libffi-dev liblzma-dev git ninja-build automake autoconf

# Install pyenv and Python
RUN git clone https://github.com/pyenv/pyenv.git /root/.pyenv && \
    cd /root/.pyenv && src/configure && make -C src
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN pyenv install ${PYTHON_VERSION} && pyenv global ${PYTHON_VERSION}
RUN python -m pip install --upgrade pip

# Clone and build liboqs following the recommended approach
WORKDIR /opt
RUN git clone --depth=1 https://github.com/open-quantum-safe/liboqs && \
    cmake -S liboqs -B liboqs/build -DBUILD_SHARED_LIBS=ON && \
    cmake --build liboqs/build --parallel 8 && \
    cmake --build liboqs/build --target install

# Set liboqs library path for subsequent steps
ENV LD_LIBRARY_PATH=/usr/local/lib

# Clone and install liboqs-python
WORKDIR /opt
RUN git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python.git && \
    cd liboqs-python && \
    pip install . && \
    pip install pytest cryptography nose2

# Stage 2: Final Runtime Image
FROM ubuntu:25.04
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt update && apt install -y libssl3 git cmake && rm -rf /var/lib/apt/lists/*

# Copy Python and built libraries from builder stage
COPY --from=builder /root/.pyenv /root/.pyenv
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
ENV LD_LIBRARY_PATH=/usr/local/lib

# Copy shared libraries and installed files
COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/include /usr/local/include
COPY --from=builder /opt/liboqs-python /opt/liboqs-python

# Install your pqfe package
WORKDIR /ws
COPY . /ws
RUN pip install -e .
RUN pip install -r requirements.txt

# Install liboqs-python in final stage
WORKDIR /opt/liboqs-python
RUN pip install .
# # Install psutil Python module
# RUN pip install psutil

# # Install matplotlib Python module
# RUN pip install matplotlib

# # Install seaborn Python module
# RUN pip install seaborn

# Test installation of the oqs library
RUN python -c "import oqs; print('oqs installed successfully')"

# Add a script to limit CPU cores and run the profiling script
RUN chmod +x /ws/benchmarks/run_with_cores.sh

WORKDIR /ws
# Default command to run the profiling script with 1 cores
CMD ["/ws/benchmarks/run_with_cores.sh", "1", "/ws/benchmarks/profiling_suite.py"]
