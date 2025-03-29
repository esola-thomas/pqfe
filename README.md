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

- Encryption and decryption time
- CPU and memory usage
- Storage overhead

### Running Benchmarks

To run the benchmarks, you can use the provided Docker container for a controlled environment. Follow these steps:

1. **Build the Docker Image:**
   ```bash
   docker build -t pqfe_profiling /home/esola-thomas/Electrical_and_Computer_Master_Thesis/external/pqfe
   ```

2. **Run the Docker Container:**
   Limit the container to 1 CPU and 2GB of RAM for controlled profiling:
   ```bash
   docker run --cpus=1 --memory=2g -v /home/esola-thomas/Electrical_and_Computer_Master_Thesis/profiling_results:/ws/profiling_results pqfe_profiling
   ```

3. **View Results:**
   The profiling results, including graphs and raw data, will be saved in the `/home/esola-thomas/Electrical_and_Computer_Master_Thesis/profiling_results` directory.

### Example Graphs

The benchmarking suite generates graphs for:

- Encryption/Decryption Time vs File Size
- CPU and Memory Usage vs File Size
- Storage Overhead vs File Size

These graphs help visualize the performance trade-offs between post-quantum and traditional encryption methods.
