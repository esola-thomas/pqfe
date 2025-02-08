# Copyright (c) 2025 Ernesto Sola-Thomas

"""
Performance benchmarking module for Post-Quantum File Encryption system.
"""

import time
import statistics
from pathlib import Path
import tempfile
import os
from typing import List, Dict, Any

from src.kyber_encryption import KyberEncryption
from src import file_ops

def benchmark_key_generation(
    variant: str = "Kyber512",
    iterations: int = 100
) -> Dict[str, float]:
    """
    Benchmark key generation performance.
    
    Args:
        variant (str): Kyber variant to test
        iterations (int): Number of iterations
        
    Returns:
        Dict[str, float]: Benchmark results
    """
    encryptor = KyberEncryption(variant=variant)
    times: List[float] = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        encryptor.generate_keypair()
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "std_dev": statistics.stdev(times),
        "min": min(times),
        "max": max(times)
    }

def benchmark_file_encryption(
    file_size: int,
    variant: str = "Kyber512",
    iterations: int = 10
) -> Dict[str, float]:
    """
    Benchmark file encryption performance.
    
    Args:
        file_size (int): Size of test file in bytes
        variant (str): Kyber variant to test
        iterations (int): Number of iterations
        
    Returns:
        Dict[str, float]: Benchmark results
    """
    # Create test environment
    test_dir = tempfile.mkdtemp()
    test_file = Path(test_dir) / "test.bin"
    test_file.write_bytes(os.urandom(file_size))
    
    encryptor = KyberEncryption(variant=variant)
    public_key, _ = encryptor.generate_keypair()
    times: List[float] = []
    
    try:
        for _ in range(iterations):
            start = time.perf_counter()
            encryptor.encrypt_file(str(test_file), public_key)
            end = time.perf_counter()
            times.append(end - start)
    finally:
        # Clean up
        for root, dirs, files in os.walk(test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(test_dir)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "std_dev": statistics.stdev(times),
        "min": min(times),
        "max": max(times),
        "file_size": file_size
    }

if __name__ == '__main__':
    # Run benchmarks
    print("Key Generation Benchmarks:")
    for variant in ["Kyber512", "Kyber768", "Kyber1024"]:
        results = benchmark_key_generation(variant=variant)
        print(f"\n{variant}:")
        for key, value in results.items():
            print(f"  {key}: {value:.6f} seconds") 