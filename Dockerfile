# Copyright (c) 2025 Ernesto Sola-Thomas
# Inspired by https://github.com/open-quantum-safe/liboqs-python/blob/main/docker/Dockerfile
# Multi-stage build: First the full builder image:
ARG LIBOQS_BUILD_DEFINES="-DOQS_DIST_BUILD=ON -DBUILD_SHARED_LIBS=ON -DOQS_USE_OPENSSL=OFF"
ARG MAKE_DEFINES="-j 2"

FROM python:3.10-slim-bullseye as intermediate
ARG LIBOQS_BUILD_DEFINES
ARG MAKE_DEFINES

LABEL version="2"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get upgrade -y

# Get all software packages required for building
RUN apt-get install -y build-essential cmake ninja-build git wget

# get all sources
WORKDIR /opt
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs && \
    git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs-python.git 

# build liboqs 
WORKDIR /opt/liboqs
RUN mkdir build && cd build && cmake -GNinja .. ${LIBOQS_BUILD_DEFINES} && ninja install

WORKDIR /opt
RUN git clone --depth 1 --branch OQS-OpenSSL_1_1_1-stable https://github.com/open-quantum-safe/openssl.git && \
    cd liboqs && mkdir build-openssl && cd build-openssl && \
    cmake -G"Ninja" .. ${LIBOQS_BUILD_DEFINES} -DCMAKE_INSTALL_PREFIX=/opt/openssl/oqs && ninja install

RUN apt-get install -y automake autoconf && cd /opt/openssl && \
    LDFLAGS="-Wl,-rpath -Wl,/usr/local/lib64" ./Configure shared linux-x86_64 -lm && \
    make ${MAKE_DEFINES} && make install_sw

# Get LetsEncrypt root
RUN wget https://letsencrypt.org/certs/isrgrootx1.pem

## second stage: minimal image
FROM python:3.10-slim-bullseye

# Get required packages
RUN apt-get update && apt-get upgrade -y

# Copy built artifacts
COPY --from=intermediate /usr/local /usr/local
COPY --from=intermediate /opt/liboqs-python /opt/liboqs-python

ENV PYTHONPATH=/opt/liboqs-python

# Install liboqs-python
RUN cd /opt/liboqs-python && python setup.py install

# Enable a normal user 
RUN useradd -m -u 1000 -s /bin/bash oqs

USER oqs
WORKDIR /home/oqs
COPY --from=intermediate /opt/isrgrootx1.pem /home/oqs/isrgrootx1.pem

# ensure oqs libs are found
ENV LD_LIBRARY_PATH=/usr/local/lib64
CMD ["python"]
