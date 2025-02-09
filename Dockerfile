# Copyright (c) 2025 Ernesto Sola-Thomas

FROM python:3.10.16

WORKDIR /liboqs-python

RUN apt-get update && \
    apt-get install -y git && \
    git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python && \
    cd liboqs-python && \
    pip install . && \
    apt-get remove -y git && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

CMD ["python", "-m", "unittest", "discover", "-s", "tests"]
