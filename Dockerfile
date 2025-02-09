# Copyright (c) 2025 Ernesto Sola-Thomas

FROM python:3.10.16

WORKDIR /liboqs_gits

RUN apt-get update && \
    apt-get install -y git cmake build-essential && \
    pip install --upgrade pip && \
    git clone --depth=1 https://github.com/open-quantum-safe/liboqs && \
    git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python

RUN cmake -S liboqs -B liboqs/build -DBUILD_SHARED_LIBS=ON && \
    cmake --build liboqs/build --parallel 8 && \
    cmake --build liboqs/build --target install && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/liboqs.conf && \
    ldconfig && \
    cd liboqs-python && \
    pip install . && \
    python -c "import oqs; print('oqs installed successfully')" && \
    apt-get remove -y git cmake build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* liboqs

WORKDIR /app

COPY . .

CMD ["python", "-m", "unittest", "discover", "-s", "tests"]
