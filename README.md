# PQFE (Post-Quantum File Encryption)

A Python wrapper over liboqs that provides easy-to-use post-quantum file encryption capabilities.

## Overview

PQFE is a tool that allows you to encrypt files using post-quantum cryptographic algorithms implemented in liboqs (Open Quantum Safe). This wrapper makes it simple to protect your files against potential threats from quantum computers.

## Features

- Easy-to-use command line interface
- Support for multiple post-quantum encryption algorithms
- File encryption and decryption
- Built on top of the well-tested liboqs library
- Python-based for cross-platform compatibility
- Multiple symmetric cipher options (AES-256-GCM and ChaCha20-Poly1305)
- In-memory operation support
- Customizable output locations

## Build status
[![Build and Push Docker Image](https://github.com/esola-thomas/pqfe/actions/workflows/push_docker_image.yml/badge.svg)](https://github.com/esola-thomas/pqfe/actions/workflows/push_docker_image.yml)

^ This is a Docker image to be used to create containers for developmenent and testing

## Benchmarks

The PQFE repository includes a comprehensive benchmarking suite to evaluate the performance of post-quantum encryption algorithms compared to traditional methods like AES. The benchmarks measure:

- Encryption and decryption time across different file sizes
- Memory usage during encryption and decryption operations
- CPU utilization for all methods
- Storage overhead for encrypted files

### Benchmark Methods

The benchmarking suite compares three encryption methods:

1. **PQFE (File-Based)**: Post-quantum encryption using file operations
2. **PQFE (In-Memory)**: Post-quantum encryption done entirely in memory
3. **AES**: Traditional AES-GCM encryption for baseline comparison

### Running Benchmarks

To run the benchmarks, you can use the provided Docker container for a controlled environment. Follow these steps:

1. **Build the Docker Image:**
   ```bash
   docker build -t pqfe_profiling .
   ```

2. **Run the Docker Container:**
   Limit the container to a specific number of CPUs and memory for controlled profiling:
   ```bash
   docker run --cpus=1 --memory=2g -v ./profiling_results:/ws/profiling_results pqfe_profiling
   ```

   Adjust the `--cpus` and `--memory` flags as needed to control resource usage.

3. **Run Benchmarks with Custom Parameters:**
   You can also run the profiling suite with custom parameters:
   ```bash
   docker run --cpus=1 --memory=2g -v ./profiling_results:/ws/profiling_results pqfe_profiling \
     --min-size 1024 --max-size 1000000000 --steps 20 --scale logarithmic
   ```

   Available parameters:
   - `--min-size`: Minimum file size in bytes (default: 1024)
   - `--max-size`: Maximum file size in bytes (default: 2000000000)
   - `--steps`: Number of test file sizes between min and max (default: 300)
   - `--scale`: Scale type for file size distribution ("linear" or "logarithmic")
   - `--graphs-only`: Only generate graphs from existing JSON data without running tests
   - `--json-dir`: Path to JSON directory with existing results (used with --graphs-only)
   - `--output-dir`: Directory where results and charts will be saved (default: profiling_results)

4. **View Results:**
   The profiling results, including graphs and raw data, will be saved in the `./profiling_results` directory:
   - `charts/`: Contains visual representations of the benchmark results
   - `json/`: Contains raw data for further analysis

### Example Graphs

The benchmarking suite generates several visualizations:

- **time_vs_size_linear.png**: Encryption/decryption time vs file size (linear scale)
- **time_vs_size_log.png**: Encryption/decryption time vs file size (logarithmic scale)
- **memory_vs_size.png**: Memory usage vs file size
- **cpu_vs_size.png**: CPU utilization vs file size
- **size_comparison.png**: Original vs encrypted file sizes
- **size_comparison_log.png**: Original vs encrypted file sizes (logarithmic scale)

These graphs help visualize the performance trade-offs between post-quantum and traditional encryption methods across different metrics and file sizes.
