# Copyright (c) 2025 Ernesto Sola-Thomas

# Use Ubuntu as the base image
FROM ubuntu:25.04
ARG PYTHON_VERSION=3.10.16
ARG LIBOQS_BUILD_DEFINES="-DOQS_DIST_BUILD=ON -DBUILD_SHARED_LIBS=ON -DOQS_USE_OPENSSL=OFF"

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt update && apt install -y\
    cmake \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    git \
    vim \
    tree \
    ninja-build \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /

# Install pyenv
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv && \
    ~/.pyenv/src/configure && make -C ~/.pyenv/src

# Set up pyenv for bash
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc

# Set up pyenv for zsh
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc && \
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc && \
    echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc

# Ensure pyenv is available in the current shell
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN eval "$(pyenv init --path)"
# Install Python
RUN pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION}

# Upgrade pip
RUN python -m pip install --upgrade pip

# Add a build argument for the PAT
ENV DOCKER_ENV=1
ENV PROJECT_PATH=/ws
ENV OQS_INSTALL_PATH=/opt/liboqs/lib
ENV LD_LIBRARY_PATH=/opt/liboqs/lib

# Clone the private repository using the PAT
WORKDIR /opt
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs && \
    git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs-python.git 

# build liboqs 
WORKDIR /opt/liboqs
RUN mkdir lib && cd lib && cmake -GNinja .. ${LIBOQS_BUILD_DEFINES} && ninja install

WORKDIR /opt
RUN git clone --depth 1 --branch OQS-OpenSSL_1_1_1-stable https://github.com/open-quantum-safe/openssl.git && cd liboqs && mkdir build-openssl && cd build-openssl && cmake -G"Ninja" .. ${LIBOQS_BUILD_DEFINES} -DCMAKE_INSTALL_PREFIX=/opt/openssl/oqs && ninja install
RUN apt update && apt install -y automake autoconf && cd /opt/openssl && LDFLAGS="-Wl,-rpath -Wl,/usr/local/lib64" ./Configure shared linux-x86_64 -lm && make -j 2 && make install_sw
RUN cd liboqs-python && pip install .

WORKDIR /ws

# Test the install of the oqs library
RUN python -c "import oqs; print('oqs installed successfully')"

# Default command to keep the container alive
CMD ["tail", "-f", "/dev/null"]