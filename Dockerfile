# Copyright (c) 2025 Ernesto Sola-Thomas
# Stage 1: Build dependencies
FROM ubuntu:25.04 AS builder
ARG PYTHON_VERSION=3.10.16
ARG LIBOQS_BUILD_DEFINES="-DOQS_DIST_BUILD=ON -DBUILD_SHARED_LIBS=ON -DOQS_USE_OPENSSL=OFF"

ENV DEBIAN_FRONTEND=noninteractive
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

# Clone and build liboqs and liboqs-python
WORKDIR /opt
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs-python.git

# Build liboqs
WORKDIR /opt/liboqs
RUN mkdir lib && cd lib && cmake -GNinja .. ${LIBOQS_BUILD_DEFINES} && ninja install

# Optionally build OpenSSL with OQS (if required)
WORKDIR /opt
RUN git clone --depth 1 --branch OQS-OpenSSL_1_1_1-stable https://github.com/open-quantum-safe/openssl.git && \
    cd liboqs && mkdir build-openssl && cd build-openssl && \
    cmake -GNinja .. ${LIBOQS_BUILD_DEFINES} -DCMAKE_INSTALL_PREFIX=/opt/openssl/oqs && ninja install && \
    cd /opt/openssl && LDFLAGS="-Wl,-rpath -Wl,/usr/local/lib64" ./Configure shared linux-x86_64 -lm && make -j2 && make install_sw

# Build and install liboqs-python
WORKDIR /opt/liboqs-python
RUN pip install . && pip install pytest cryptography

# Stage 2: Create final image
FROM ubuntu:25.04
ENV DEBIAN_FRONTEND=noninteractive
# Install runtime dependencies (if any)
RUN apt update && apt install -y libssl1.1 && rm -rf /var/lib/apt/lists/*

# Copy Python from builder
COPY --from=builder /root/.pyenv /root/.pyenv
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN eval "$(pyenv init --path)" && pyenv global ${PYTHON_VERSION}

# Copy built libraries and installed Python packages (if needed)
COPY --from=builder /opt/liboqs-python /opt/liboqs-python

# Install your pqfe package (assuming it's in the repository)
WORKDIR /ws
COPY . /ws
RUN pip install -e .

# Set environment variables for OQS
ENV OQS_INSTALL_PATH=/opt/liboqs/lib
ENV LD_LIBRARY_PATH=/opt/liboqs/lib

# Test the install of the oqs library
RUN python -c "import oqs; print('oqs installed successfully')"

CMD ["tail", "-f", "/dev/null"]
