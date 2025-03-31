# Copyright (c) 2025 Ernesto Sola-Thomas
import os
import time
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.api import PQFE
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json
import glob
import argparse  # Add this import for command line arguments

class ProfilingSuite:
    def __init__(self, output_dir="profiling_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create subdirectories for different file types
        self.json_dir = self.output_dir / "json"
        self.charts_dir = self.output_dir / "charts"
        self.json_dir.mkdir(exist_ok=True, parents=True)
        self.charts_dir.mkdir(exist_ok=True, parents=True)
        
        print("Using all available CPU cores for testing.")

    def generate_test_file(self, size_in_bytes, file_path):
        print(f"Generating test file of size {size_in_bytes} bytes...")
        with open(file_path, "wb") as f:
            f.write(os.urandom(size_in_bytes))
        print(f"Test file {file_path} generated.")

    def cleanup_test_file(self, file_path, encrypted_path=None, decrypted_path=None):
        """
        Clean up all files related to a test.
        
        Args:
            file_path: Original test file path
            encrypted_path: Path to the encrypted file (optional)
            decrypted_path: Path to the decrypted file (optional)
        """
        # Clean up original test file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed original test file: {file_path}")
        
        # Clean up encrypted file
        if encrypted_path and os.path.exists(encrypted_path):
            os.remove(encrypted_path)
            print(f"Removed encrypted file: {encrypted_path}")
        else:
            # Try common patterns for encrypted files
            enc_patterns = [f"{file_path}.enc", f"{file_path}_enc"]
            for pattern in enc_patterns:
                if os.path.exists(pattern):
                    os.remove(pattern)
                    print(f"Removed encrypted file: {pattern}")
        
        # Clean up decrypted file
        if decrypted_path and os.path.exists(decrypted_path):
            os.remove(decrypted_path)
            print(f"Removed decrypted file: {decrypted_path}")
        else:
            # Try common patterns for decrypted files
            dec_patterns = [f"{file_path}.dec", f"{file_path}_dec", 
                            str(file_path).replace(".bin", "_decrypted.bin")]
            for pattern in dec_patterns:
                if os.path.exists(pattern):
                    os.remove(pattern)
                    print(f"Removed decrypted file: {pattern}")

        print(f"All files related to {file_path} have been removed.")

    def cleanup_all_bin_files(self):
        # Remove all temporary bin files
        bin_files = glob.glob(str(self.output_dir / "*.bin"))
        enc_files = glob.glob(str(self.output_dir / "*.bin.enc"))
        for file in bin_files + enc_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed temporary file: {file}")

    def measure_performance(self, func, *args, **kwargs):
        process = psutil.Process(os.getpid())
        # Start CPU percentage measurement
        process.cpu_percent(interval=None)  # First call to initialize measurement
        
        # Capture start time and memory
        start_time = time.time()
        start_memory = process.memory_info().rss
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Capture end time and memory
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        # Get CPU percentage - this captures CPU usage since the last call
        cpu_percent = process.cpu_percent(interval=None)
        
        # Calculate elapsed time and memory used
        elapsed_time = end_time - start_time
        memory_used = max(0, end_memory - start_memory)  # Avoid negative values
        
        # Add debug logs to verify values
        print(f"Start memory: {start_memory} bytes")
        print(f"End memory: {end_memory} bytes")
        print(f"CPU usage: {cpu_percent}%")
        print(f"Elapsed time: {elapsed_time} seconds")
        
        return {
            "time": elapsed_time,
            "memory": memory_used,
            "cpu": cpu_percent,
            "result": result
        }

    def pqfe_encrypt_decrypt(self, file_path, pqfe_instance, public_key, private_key):
        # Check file size - AES-GCM has a limit of 2^31-1 bytes (approximately 2GB)
        file_size = os.path.getsize(file_path)
        max_size = 2**31 - 1  # ~2GB limit
        
        if file_size > max_size:
            print(f"Warning: File {file_path} exceeds the 2GB encryption limit ({file_size} bytes)")
            print("Skipping PQFE encryption test for this file size")
            return ("skipped - file too large", "skipped - file too large", 0)
            
        print(f"Running PQFE encryption and decryption for {file_path}...")
        encrypt_result = pqfe_instance.encrypt_file(
            file_path=file_path,
            public_key=public_key,
            return_as_data=False
        )
        encrypted_file_path = encrypt_result["encrypted_file_path"]
        ciphertext = encrypt_result["ciphertext"]
        
        # Get and store encrypted file size
        encrypted_file_size = os.path.getsize(encrypted_file_path) if os.path.exists(encrypted_file_path) else 0

        decrypt_result = pqfe_instance.decrypt_file(
            encrypted_file=encrypted_file_path,
            ciphertext=ciphertext,
            private_key=private_key,
            return_as_data=False
        )
        decrypted_file_path = decrypt_result["decrypted_file_path"]

        print(f"PQFE encryption and decryption for {file_path} completed.")
        return (encrypted_file_path, decrypted_file_path, encrypted_file_size)

    def pqfe_encrypt_decrypt_in_memory(self, data: bytes, pqfe_instance, public_key, private_key):
        # Check data size - AES-GCM has a limit of 2^31-1 bytes (approximately 2GB)
        data_size = len(data)
        max_size = 2**31 - 1  # ~2GB limit
        
        if data_size > max_size:
            print(f"Warning: Data exceeds the 2GB encryption limit ({data_size} bytes)")
            print("Skipping PQFE in-memory encryption test for this data size")
            return b"skipped - data too large"
            
        print("Running PQFE in-memory encryption and decryption...")
        encrypt_result = pqfe_instance.encrypt_data(data, public_key)
        encrypted_data = encrypt_result["encrypted_data"]
        ciphertext = encrypt_result["ciphertext"]

        decrypt_result = pqfe_instance.decrypt_data(encrypted_data, ciphertext, private_key)
        decrypted_data = decrypt_result["decrypted_data"]

        print("PQFE in-memory encryption and decryption completed.")
        return decrypted_data

    def aes_encrypt_decrypt(self, file_path, key):
        print(f"Running AES encryption and decryption for {file_path}...")
        aesgcm = AESGCM(key)
        with open(file_path, "rb") as f:
            data = f.read()
        nonce = os.urandom(12)
        encrypted_data = aesgcm.encrypt(nonce, data, None)
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
        print(f"AES encryption and decryption for {file_path} completed.")
        return (encrypted_data, decrypted_data)

    def plot_results(self, results):
        """
        Create a time vs file size plot with linear scale.
        """
        sns.set(style="whitegrid")
        sizes = [r["size"] for r in results]
        pqfe_times = [r["pqfe"]["average"]["time"] for r in results]
        aes_times = [r["aes"]["average"]["time"] for r in results]
        pqfe_in_memory_times = [r["pqfe_in_memory"]["average"]["time"] for r in results]
        
        # Calculate error ranges (min and max values)
        pqfe_times_min = [min(run["time"] for run in r["pqfe"]["individual_runs"]) for r in results]
        pqfe_times_max = [max(run["time"] for run in r["pqfe"]["individual_runs"]) for r in results]
        
        aes_times_min = [min(run["time"] for run in r["aes"]["individual_runs"]) for r in results]
        aes_times_max = [max(run["time"] for run in r["aes"]["individual_runs"]) for r in results]
        
        pqfe_in_memory_times_min = [min(run["time"] for run in r["pqfe_in_memory"]["individual_runs"]) for r in results]
        pqfe_in_memory_times_max = [max(run["time"] for run in r["pqfe_in_memory"]["individual_runs"]) for r in results]
        
        # Convert to error bar format (lower and upper deviation from mean)
        pqfe_times_err = [(pqfe_times[i] - pqfe_times_min[i], pqfe_times_max[i] - pqfe_times[i]) for i in range(len(sizes))]
        aes_times_err = [(aes_times[i] - aes_times_min[i], aes_times_max[i] - aes_times[i]) for i in range(len(sizes))]
        pqfe_in_memory_times_err = [(pqfe_in_memory_times[i] - pqfe_in_memory_times_min[i], pqfe_in_memory_times_max[i] - pqfe_in_memory_times[i]) for i in range(len(sizes))]
        
        # Create consistent colors
        colors = {
            'pqfe': 'blue',
            'pqfe_in_memory': 'orange',
            'aes': 'green'
        }

        # Linear scale plot
        plt.figure(figsize=(12, 7))
        plt.errorbar(sizes, pqfe_times, yerr=list(zip(*pqfe_times_err)), 
                     label="PQFE (File-Based)", marker="o", capsize=5, fmt='-', color=colors['pqfe'])
        plt.errorbar(sizes, pqfe_in_memory_times, yerr=list(zip(*pqfe_in_memory_times_err)), 
                     label="PQFE (In-Memory)", marker="s", capsize=5, fmt='-', color=colors['pqfe_in_memory'])
        plt.errorbar(sizes, aes_times, yerr=list(zip(*aes_times_err)), 
                     label="AES", marker="^", capsize=5, fmt='-', color=colors['aes'])
        
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Time (seconds)")
        plt.title("Encryption/Decryption Time vs File Size - Linear Scale")
        plt.legend()
        
        # Add text annotation explaining the data points
        plt.figtext(0.5, 0.01, "Note: Each data point represents the average of 10 runs.\nError bars show min/max values across all runs.", 
                   ha="center", fontsize=9, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 1])  # Adjust layout to make room for the note
        plt.savefig(self.charts_dir / "time_vs_size_linear.png")
        plt.close()
        
        # Logarithmic scale plot
        plt.figure(figsize=(12, 7))
        plt.semilogx(sizes, pqfe_times, 'o-', color=colors['pqfe'], linewidth=2, label="PQFE (File-Based)")
        plt.semilogx(sizes, pqfe_in_memory_times, 's-', color=colors['pqfe_in_memory'], linewidth=2, label="PQFE (In-Memory)")
        plt.semilogx(sizes, aes_times, '^-', color=colors['aes'], linewidth=2, label="AES")
        
        plt.xlabel("File Size (bytes) - Log Scale")
        plt.ylabel("Time (seconds)")
        plt.title("Encryption/Decryption Time vs File Size - Logarithmic Scale")
        plt.legend()
        
        # Add human-readable file size labels at major tick positions
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: 
            f"{x:g} B" if x < 1024 else
            f"{x/1024:g} KB" if x < 1024**2 else
            f"{x/1024**2:g} MB" if x < 1024**3 else
            f"{x/1024**3:g} GB"
        ))
        
        # Add text annotation explaining the data points
        plt.figtext(0.5, 0.01, "Note: Each data point represents the average of 10 runs.", 
                   ha="center", fontsize=9, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 1])
        plt.savefig(self.charts_dir / "time_vs_size_log.png")
        plt.close()

    def plot_size_comparison(self, results):
        """
        Create a plot comparing original file size vs encrypted file size for all three methods.
        """
        # Extract file sizes and encrypted sizes
        original_sizes = []
        pqfe_encrypted_sizes = []
        pqfe_in_memory_encrypted_sizes = []
        aes_encrypted_sizes = []
        
        for result in results:
            # Original file size
            original_size = result["size"]
            
            # Get PQFE file-based encrypted file size if available
            pqfe_size = None
            for run in result["pqfe"]["individual_runs"]:
                if "result" in run and isinstance(run["result"], list) and len(run["result"]) >= 3:
                    # Use the third element which now contains the encrypted file size
                    if isinstance(run["result"][2], (int, float)) and run["result"][2] > 0:
                        pqfe_size = run["result"][2]
                        break
            
            # Get average PQFE in-memory encrypted data size if available
            pqfe_in_memory_size = None
            for run in result["pqfe_in_memory"]["individual_runs"]:
                if "result" in run and isinstance(run["result"], str) and run["result"].startswith("b'") and run["result"].endswith(" bytes'"):
                    try:
                        # Extract size from the format: "b'XXXXX bytes'"
                        size_str = run["result"].split("'")[1].split(" ")[0]
                        pqfe_in_memory_size = int(size_str)
                        break
                    except:
                        pass
            
            # Get average AES encrypted data size if available
            aes_size = None
            for run in result["aes"]["individual_runs"]:
                if "result" in run and isinstance(run["result"], list) and len(run["result"]) >= 1:
                    size_info = run["result"][0]
                    if isinstance(size_info, str) and size_info.startswith("b'") and size_info.endswith(" bytes'"):
                        try:
                            # Extract size from the format: "b'XXXXX bytes'"
                            size_str = size_info.split("'")[1].split(" ")[0]
                            aes_size = int(size_str)
                            break
                        except:
                            pass
            
            # Only add data if we have the original size and at least one encrypted size
            if original_size is not None and (pqfe_size is not None or pqfe_in_memory_size is not None or aes_size is not None):
                original_sizes.append(original_size)
                pqfe_encrypted_sizes.append(pqfe_size if pqfe_size is not None else 0)
                pqfe_in_memory_encrypted_sizes.append(pqfe_in_memory_size if pqfe_in_memory_size is not None else 0)
                aes_encrypted_sizes.append(aes_size if aes_size is not None else 0)
        
        # Add debugging output to check sizes
        print(f"Debug - Original sizes: {len(original_sizes)} items")
        print(f"Debug - PQFE file sizes: {len(pqfe_encrypted_sizes)} items, {sum(1 for s in pqfe_encrypted_sizes if s > 0)} non-zero")
        print(f"Debug - PQFE in-memory sizes: {len(pqfe_in_memory_encrypted_sizes)} items, {sum(1 for s in pqfe_in_memory_encrypted_sizes if s > 0)} non-zero")
        print(f"Debug - AES sizes: {len(aes_encrypted_sizes)} items, {sum(1 for s in aes_encrypted_sizes if s > 0)} non-zero")
        
        # Create consistent colors
        colors = {
            'pqfe': 'blue',
            'pqfe_in_memory': 'orange',
            'aes': 'green'
        }
        
        # Create plot
        plt.figure(figsize=(12, 7))
        
        # Plot original sizes for reference
        plt.plot(original_sizes, original_sizes, '--', color='gray', label="Original = Encrypted", alpha=0.7)
        
        # Plot all three encryption methods
        if any(size > 0 for size in pqfe_encrypted_sizes):
            plt.scatter(original_sizes, pqfe_encrypted_sizes, color=colors['pqfe'], marker='o', label="PQFE (File-Based)")
        if any(size > 0 for size in pqfe_in_memory_encrypted_sizes):
            plt.scatter(original_sizes, pqfe_in_memory_encrypted_sizes, color=colors['pqfe_in_memory'], marker='s', label="PQFE (In-Memory)")
        if any(size > 0 for size in aes_encrypted_sizes):
            plt.scatter(original_sizes, aes_encrypted_sizes, color=colors['aes'], marker='^', label="AES")
        
        plt.xlabel("Original File Size (bytes)")
        plt.ylabel("Encrypted File/Data Size (bytes)")
        plt.title("Original vs Encrypted Size Comparison")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Make the axes equal to show the 1:1 ratio clearly
        plt.axis('equal')
        
        # Ensure both axes use the same scale and limits
        max_val = max(max(original_sizes), 
                     max(pqfe_encrypted_sizes) if pqfe_encrypted_sizes else 0,
                     max(pqfe_in_memory_encrypted_sizes) if pqfe_in_memory_encrypted_sizes else 0,
                     max(aes_encrypted_sizes) if aes_encrypted_sizes else 0)
        plt.xlim(0, max_val * 1.1)
        plt.ylim(0, max_val * 1.1)
        
        # Add annotations to highlight encryption overhead
        plt.figtext(0.5, 0.01, 
                  "Note: Points above the gray line indicate encryption overhead.\nCloser to the line means more efficient storage.",
                  ha="center", fontsize=9, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 1])
        plt.savefig(self.charts_dir / "size_comparison.png")
        plt.close()
        
        # Also create log-scale version
        plt.figure(figsize=(12, 7))
        plt.loglog(original_sizes, original_sizes, '--', color='gray', label="Original = Encrypted", alpha=0.7)
        
        # Plot all three encryption methods with log scale
        if any(size > 0 for size in pqfe_encrypted_sizes):
            plt.loglog(original_sizes, pqfe_encrypted_sizes, 'o', color=colors['pqfe'], label="PQFE (File-Based)")
        if any(size > 0 for size in pqfe_in_memory_encrypted_sizes):
            plt.loglog(original_sizes, pqfe_in_memory_encrypted_sizes, 's', color=colors['pqfe_in_memory'], label="PQFE (In-Memory)")
        if any(size > 0 for size in aes_encrypted_sizes):
            plt.loglog(original_sizes, aes_encrypted_sizes, '^', color=colors['aes'], label="AES")
        
        plt.xlabel("Original File Size (bytes) - Log Scale")
        plt.ylabel("Encrypted File/Data Size (bytes) - Log Scale")
        plt.title("Original vs Encrypted Size Comparison - Log Scale")
        plt.legend()
        plt.grid(True, alpha=0.3, which="both")
        
        # Add formatter for human-readable labels
        formatter = plt.FuncFormatter(lambda x, _: 
            f"{x:g} B" if x < 1024 else
            f"{x/1024:g} KB" if x < 1024**2 else
            f"{x/1024**2:g} MB" if x < 1024**3 else
            f"{x/1024**3:g} GB"
        )
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.gca().yaxis.set_major_formatter(formatter)
        
        plt.figtext(0.5, 0.01, 
                   "Note: Points above the gray line indicate encryption overhead.\nParallel lines indicate constant overhead ratio.",
                   ha="center", fontsize=9, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 1])
        plt.savefig(self.charts_dir / "size_comparison_log.png")
        plt.close()

    def plot_additional_metrics(self, results):
        sns.set(style="whitegrid")
        sizes = [r["size"] for r in results]
        
        # Memory metrics
        pqfe_memory = [r["pqfe"]["average"]["memory"] for r in results]
        aes_memory = [r["aes"]["average"]["memory"] for r in results]
        pqfe_in_memory_memory = [r["pqfe_in_memory"]["average"]["memory"] for r in results]
        
        # Calculate memory error ranges
        pqfe_memory_min = [min(run["memory"] for run in r["pqfe"]["individual_runs"]) for r in results]
        pqfe_memory_max = [max(run["memory"] for run in r["pqfe"]["individual_runs"]) for r in results]
        
        aes_memory_min = [min(run["memory"] for run in r["aes"]["individual_runs"]) for r in results]
        aes_memory_max = [max(run["memory"] for run in r["aes"]["individual_runs"]) for r in results]
        
        pqfe_in_memory_memory_min = [min(run["memory"] for run in r["pqfe_in_memory"]["individual_runs"]) for r in results]
        pqfe_in_memory_memory_max = [max(run["memory"] for run in r["pqfe_in_memory"]["individual_runs"]) for r in results]
        
        # Convert to error bar format
        pqfe_memory_err = [(pqfe_memory[i] - pqfe_memory_min[i], pqfe_memory_max[i] - pqfe_memory[i]) for i in range(len(sizes))]
        aes_memory_err = [(aes_memory[i] - aes_memory_min[i], aes_memory_max[i] - aes_memory[i]) for i in range(len(sizes))]
        pqfe_in_memory_memory_err = [(pqfe_in_memory_memory[i] - pqfe_in_memory_memory_min[i], pqfe_in_memory_memory_max[i] - pqfe_in_memory_memory[i]) for i in range(len(sizes))]
        
        # CPU metrics
        pqfe_cpu = [r["pqfe"]["average"]["cpu"] for r in results]
        aes_cpu = [r["aes"]["average"]["cpu"] for r in results]
        pqfe_in_memory_cpu = [r["pqfe_in_memory"]["average"]["cpu"] for r in results]
        
        # Calculate CPU error ranges
        pqfe_cpu_min = [min(run["cpu"] for run in r["pqfe"]["individual_runs"]) for r in results]
        pqfe_cpu_max = [max(run["cpu"] for run in r["pqfe"]["individual_runs"]) for r in results]
        
        aes_cpu_min = [min(run["cpu"] for run in r["aes"]["individual_runs"]) for r in results]
        aes_cpu_max = [max(run["cpu"] for run in r["aes"]["individual_runs"]) for r in results]
        
        pqfe_in_memory_cpu_min = [min(run["cpu"] for run in r["pqfe_in_memory"]["individual_runs"]) for r in results]
        pqfe_in_memory_cpu_max = [max(run["cpu"] for run in r["pqfe_in_memory"]["individual_runs"]) for r in results]
        
        # Convert to error bar format
        pqfe_cpu_err = [(pqfe_cpu[i] - pqfe_cpu_min[i], pqfe_cpu_max[i] - pqfe_cpu[i]) for i in range(len(sizes))]
        aes_cpu_err = [(aes_cpu[i] - aes_cpu_min[i], aes_cpu_max[i] - aes_cpu[i]) for i in range(len(sizes))]
        pqfe_in_memory_cpu_err = [(pqfe_in_memory_cpu[i] - pqfe_in_memory_cpu_min[i], pqfe_in_memory_cpu_max[i] - pqfe_in_memory_cpu[i]) for i in range(len(sizes))]
        
        # Memory usage plot
        plt.figure(figsize=(12, 7))
        plt.errorbar(sizes, pqfe_memory, yerr=list(zip(*pqfe_memory_err)), label="PQFE (File-Based)", marker="o", capsize=5, fmt='-')
        plt.errorbar(sizes, pqfe_in_memory_memory, yerr=list(zip(*pqfe_in_memory_memory_err)), label="PQFE (In-Memory)", marker="s", capsize=5, fmt='-')
        plt.errorbar(sizes, aes_memory, yerr=list(zip(*aes_memory_err)), label="AES", marker="^", capsize=5, fmt='-')
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Memory Usage (bytes)")
        plt.title("Memory Usage vs File Size")
        plt.legend()
        
        # Add text annotation
        plt.figtext(0.5, 0.01, "Note: Each data point represents the average of 10 runs.\nError bars show min/max values across all runs.", 
                   ha="center", fontsize=9, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 1])
        plt.savefig(self.charts_dir / "memory_vs_size.png")
        plt.close()
        
        # CPU usage plot
        plt.figure(figsize=(12, 7))
        plt.errorbar(sizes, pqfe_cpu, yerr=list(zip(*pqfe_cpu_err)), label="PQFE (File-Based)", marker="o", capsize=5, fmt='-')
        plt.errorbar(sizes, pqfe_in_memory_cpu, yerr=list(zip(*pqfe_in_memory_cpu_err)), label="PQFE (In-Memory)", marker="s", capsize=5, fmt='-')
        plt.errorbar(sizes, aes_cpu, yerr=list(zip(*aes_cpu_err)), label="AES", marker="^", capsize=5, fmt='-')
        plt.xlabel("File Size (bytes)")
        plt.ylabel("CPU Usage (%)")
        plt.title("CPU Usage vs File Size")
        plt.legend()
        
        # Add text annotation
        plt.figtext(0.5, 0.01, "Note: Each data point represents the average of 10 runs.\nError bars show min/max values across all runs.", 
                   ha="center", fontsize=9, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.05, 1, 1])
        plt.savefig(self.charts_dir / "cpu_vs_size.png")
        plt.close()
        
        # Create the size comparison plot
        self.plot_size_comparison(results)

    def generate_file_sizes(self, scale_type="logarithmic", min_size=1024, max_size=1073741824, steps=20):
        """
        Generate a list of file sizes either logarithmically or linearly.

        Args:
            scale_type (str): Either "logarithmic" or "linear"
            min_size (int): Minimum file size in bytes
            max_size (int): Maximum file size in bytes
            steps (int): Number of steps between min and max size

        Returns:
            list: List of file sizes in bytes
        """
        import numpy as np
        
        if scale_type.lower() == "logarithmic":
            # Generate logarithmically spaced values
            sizes = np.logspace(np.log10(min_size), np.log10(max_size), steps)
        elif scale_type.lower() == "linear":
            # Generate linearly spaced values
            sizes = np.linspace(min_size, max_size, steps)
        else:
            raise ValueError("scale_type must be either 'logarithmic' or 'linear'")
        
        # Convert to integers
        sizes = [int(size) for size in sizes]
        
        # Add human-readable comments
        size_with_comments = []
        for size in sizes:
            if size < 1024:
                comment = f"{size} B"
            elif size < 1024**2:
                comment = f"{size/1024:.0f} KB"
            elif size < 1024**3:
                comment = f"{size/1024**2:.0f} MB"
            else:
                comment = f"{size/1024**3:.0f} GB"
            size_with_comments.append((size, comment))
        return size_with_comments

    def load_results_from_json(self, json_dir):
        """
        Load test results from a previously generated JSON directory.
        
        Args:
            json_dir (str): Path to directory containing JSON results
            
        Returns:
            list: List of test results for each file size
        """
        json_dir = Path(json_dir)
        graph_data_path = json_dir / "graph_data.json"
        
        if graph_data_path.exists():
            print(f"Loading combined results from {graph_data_path}")
            with open(graph_data_path, "r") as f:
                return json.load(f)
        
        # If no graph_data.json exists, try to combine individual result files
        print(f"No graph_data.json found in {json_dir}. Attempting to combine individual result files...")
        
        results = []
        result_files = sorted(glob.glob(str(json_dir / "results_*.json")))
        
        if not result_files:
            raise FileNotFoundError(f"No result files found in {json_dir}")
            
        print(f"Found {len(result_files)} result files.")
        
        for result_file in result_files:
            with open(result_file, "r") as f:
                data = json.load(f)
                results.append(data)
        
        print(f"Successfully loaded {len(results)} result sets.")
        return results

    def generate_graphs_from_json(self, json_dir, output_dir=None):
        """
        Generate all graphs from previously saved JSON results.
        
        Args:
            json_dir (str): Path to directory containing JSON results
            output_dir (str, optional): Directory to save charts. If None, uses the chart_dir from initialization.
        """
        # If output_dir is specified, update the charts_dir
        if output_dir:
            self.charts_dir = Path(output_dir)
            self.charts_dir.mkdir(exist_ok=True, parents=True)
            
        print(f"Loading results from {json_dir}...")
        results = self.load_results_from_json(json_dir)
        
        print(f"Generating plots from {len(results)} data points...")
        self.plot_results(results)
        self.plot_additional_metrics(results)  # This will now also create the file size distribution plot
        
        print(f"Plots generated and saved in {self.charts_dir}")

    def run_tests(self, file_sizes):
        print("Initializing PQFE and AES keys...")
        public_key, private_key = PQFE().generate_keys()
        aes_key = os.urandom(32)
        print("Keys initialized.")
        
        results = []
        
        for size in file_sizes:
            print(f"Starting tests for file size: {size} bytes...")
            # Initialize variables to avoid UnboundLocalError in the finally block
            pqfe = None
            pqfe_metrics_list = []
            aes_metrics_list = []
            pqfe_in_memory_metrics_list = []
            pqfe_metrics = None
            aes_metrics = None
            pqfe_in_memory_metrics = None
            avg_pqfe_metrics = None
            avg_aes_metrics = None 
            avg_pqfe_in_memory_metrics = None
            
            file_path = self.output_dir / f"test_file_{size}.bin"
            self.generate_test_file(size, file_path)

            try:
                pqfe = PQFE()  # Initialize PQFE instance for each test
                pqfe_metrics_list = []
                aes_metrics_list = []
                pqfe_in_memory_metrics_list = []

                for _ in range(10):  # Run each test 10 times
                    try:
                        # Check file size limit for PQFE
                        max_size = 2**31 - 1  # ~2GB limit
                        if size > max_size:
                            print(f"File size {size} exceeds encryption limit. Skipping PQFE test.")
                            pqfe_metrics = {
                                "time": 0,
                                "memory": 0,
                                "cpu": 0,
                                "result": ("skipped - file too large", "skipped - file too large", 0),
                                "skipped": True
                            }
                        else:
                            for attempt in range(5):
                                pqfe_metrics = self.measure_performance(
                                    self.pqfe_encrypt_decrypt, file_path, pqfe, public_key, private_key
                                )
                                if pqfe_metrics["cpu"] <= 110 or attempt == 4:
                                    break
                                print(f"Retrying PQFE test for file size {size} due to high CPU utilization ({pqfe_metrics['cpu']}%).")
                    except Exception as e:
                        print(f"PQFE encryption failed: {str(e)}")
                        pqfe_metrics = {
                            "time": 0,
                            "memory": 0,
                            "cpu": 0,
                            "result": (f"error: {str(e)}", f"error: {str(e)}", 0),
                            "error": str(e)
                        }

                    try:
                        for attempt in range(5):
                            aes_metrics = self.measure_performance(
                                self.aes_encrypt_decrypt, file_path, aes_key
                            )
                            if aes_metrics["cpu"] <= 110 or attempt == 4:
                                break
                            print(f"Retrying AES test for file size {size} due to high CPU utilization ({aes_metrics['cpu']}%).")
                    except Exception as e:
                        print(f"AES encryption failed: {str(e)}")
                        aes_metrics = {
                            "time": 0,
                            "memory": 0,
                            "cpu": 0,
                            "result": (f"error: {str(e)}", f"error: {str(e)}"),
                            "error": str(e)
                        }

                    try:
                        with open(file_path, "rb") as f:
                            data = f.read()

                        # Check data size limit for in-memory PQFE
                        if len(data) > max_size:
                            print(f"Data size {len(data)} exceeds encryption limit. Skipping PQFE in-memory test.")
                            pqfe_in_memory_metrics = {
                                "time": 0,
                                "memory": 0,
                                "cpu": 0,
                                "result": b"skipped - data too large",
                                "skipped": True
                            }
                        else:
                            for attempt in range(5):
                                pqfe_in_memory_metrics = self.measure_performance(
                                    self.pqfe_encrypt_decrypt_in_memory, data, pqfe, public_key, private_key
                                )
                                if pqfe_in_memory_metrics["cpu"] <= 110 or attempt == 4:
                                    break
                                print(f"Retrying PQFE in-memory test for file size {size} due to high CPU utilization ({pqfe_in_memory_metrics['cpu']}%).")
                    except Exception as e:
                        print(f"PQFE in-memory encryption failed: {str(e)}")
                        pqfe_in_memory_metrics = {
                            "time": 0,
                            "memory": 0,
                            "cpu": 0,
                            "result": f"error: {str(e)}".encode(),
                            "error": str(e)
                        }

                    # Replace binary data with metadata before adding to metrics lists
                    if "result" in pqfe_metrics and isinstance(pqfe_metrics["result"], tuple):
                        # Keep file paths and file size for PQFE
                        if len(pqfe_metrics["result"]) >= 3:
                            pqfe_metrics["result"] = [str(pqfe_metrics["result"][0]), 
                                                     str(pqfe_metrics["result"][1]), 
                                                     pqfe_metrics["result"][2]]
                        else:
                            pqfe_metrics["result"] = [str(path) for path in pqfe_metrics["result"]] + [0]
                    
                    if "result" in aes_metrics and isinstance(aes_metrics["result"], tuple):
                        # Replace binary data with size information for AES
                        aes_metrics["result"] = [
                            f"b'{len(item)} bytes'" if isinstance(item, bytes) else str(item)
                            for item in aes_metrics["result"]
                        ]
                    
                    if "result" in pqfe_in_memory_metrics:
                        # Replace binary data with size information for in-memory PQFE
                        if isinstance(pqfe_in_memory_metrics["result"], bytes):
                            pqfe_in_memory_metrics["result"] = f"b'{len(pqfe_in_memory_metrics['result'])} bytes'"

                    pqfe_metrics_list.append(pqfe_metrics)
                    aes_metrics_list.append(aes_metrics)
                    pqfe_in_memory_metrics_list.append(pqfe_in_memory_metrics)

                # Calculate average metrics
                # Only calculate averages for non-skipped/non-error runs
                valid_pqfe_metrics = [m for m in pqfe_metrics_list if "skipped" not in m and "error" not in m]
                valid_aes_metrics = [m for m in aes_metrics_list if "skipped" not in m and "error" not in m]
                valid_pqfe_in_memory_metrics = [m for m in pqfe_in_memory_metrics_list if "skipped" not in m and "error" not in m]
                
                avg_pqfe_metrics = {
                    "time": sum(m["time"] for m in valid_pqfe_metrics) / max(len(valid_pqfe_metrics), 1),
                    "memory": sum(m["memory"] for m in valid_pqfe_metrics) / max(len(valid_pqfe_metrics), 1),
                    "cpu": sum(m["cpu"] for m in valid_pqfe_metrics) / max(len(valid_pqfe_metrics), 1),
                }

                avg_aes_metrics = {
                    "time": sum(m["time"] for m in valid_aes_metrics) / max(len(valid_aes_metrics), 1),
                    "memory": sum(m["memory"] for m in valid_aes_metrics) / max(len(valid_aes_metrics), 1),
                    "cpu": sum(m["cpu"] for m in valid_aes_metrics) / max(len(valid_aes_metrics), 1),
                }

                avg_pqfe_in_memory_metrics = {
                    "time": sum(m["time"] for m in valid_pqfe_in_memory_metrics) / max(len(valid_pqfe_in_memory_metrics), 1),
                    "memory": sum(m["memory"] for m in valid_pqfe_in_memory_metrics) / max(len(valid_pqfe_in_memory_metrics), 1),
                    "cpu": sum(m["cpu"] for m in valid_pqfe_in_memory_metrics) / max(len(valid_pqfe_in_memory_metrics), 1),
                }

                results.append({
                    "size": size,
                    "pqfe": {
                        "individual_runs": pqfe_metrics_list,
                        "average": avg_pqfe_metrics
                    },
                    "aes": {
                        "individual_runs": aes_metrics_list,
                        "average": avg_aes_metrics
                    },
                    "pqfe_in_memory": {
                        "individual_runs": pqfe_in_memory_metrics_list,
                        "average": avg_pqfe_in_memory_metrics
                    }
                })

                # Save individual results to separate JSON files in the json directory
                size_results = {
                    "size": size,
                    "pqfe": {
                        "individual_runs": pqfe_metrics_list,
                        "average": avg_pqfe_metrics
                    },
                    "aes": {
                        "individual_runs": aes_metrics_list,
                        "average": avg_aes_metrics
                    },
                    "pqfe_in_memory": {
                        "individual_runs": pqfe_in_memory_metrics_list,
                        "average": avg_pqfe_in_memory_metrics
                    }
                }
                with open(self.json_dir / f"results_{size}.json", "w") as f:
                    json.dump(size_results, f, indent=4)

                print(f"Tests for file size {size} bytes completed.")
            finally:
                # Extract file paths from the metrics if available
                encrypted_path = None
                decrypted_path = None
                # Try to get paths from the last PQFE run
                if pqfe_metrics_list and "result" in pqfe_metrics_list[-1]:
                    result = pqfe_metrics_list[-1]["result"]
                    if isinstance(result, (list, tuple)) and len(result) >= 2:
                        encrypted_path = result[0]
                        decrypted_path = result[1]
                
                # Clean up all test files
                self.cleanup_test_file(file_path, encrypted_path, decrypted_path)
                
                # Clean up variables with safe deletion
                local_vars = locals()
                for var_name in ['pqfe', 'pqfe_metrics_list', 'aes_metrics_list', 'pqfe_in_memory_metrics_list', 
                                'pqfe_metrics', 'aes_metrics', 'pqfe_in_memory_metrics', 
                                'avg_pqfe_metrics', 'avg_aes_metrics', 'avg_pqfe_in_memory_metrics']:
                    if var_name in local_vars and local_vars[var_name] is not None:
                        del local_vars[var_name]
                
                import gc
                gc.collect()
        
        # Save detailed results to JSON in the json directory
        with open(self.json_dir / "graph_data.json", "w") as f:
            json.dump(results, f, indent=4)

        print("All tests completed. Generating plots...")
        self.plot_results(results)
        self.plot_additional_metrics(results)
        
        # Clean up any remaining temporary files
        self.cleanup_all_bin_files()
        print("Plots generated and saved in the charts directory.")
        print(f"Results saved in the json directory.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="PQFE Profiling Suite")
    parser.add_argument(
        "--graphs-only", 
        action="store_true",
        help="Only generate graphs from existing JSON data without running tests"
    )
    parser.add_argument(
        "--json-dir", 
        type=str,
        help="Path to JSON directory with existing results (used with --graphs-only)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="profiling_results",
        help="Directory where results and charts will be saved"
    )
    parser.add_argument(
        "--min-size", 
        type=int, 
        default=1024,
        help="Minimum file size in bytes"
    )
    parser.add_argument(
        "--max-size", 
        type=int, 
        default=2000000000,  # ~1.86 GB (below the 2GB limit)
        help="Maximum file size in bytes"
    )
    parser.add_argument(
        "--steps", 
        type=int, 
        default=100,
        help="Number of test file sizes between min and max"
    )
    parser.add_argument(
        "--scale", 
        type=str, 
        choices=["linear", "logarithmic"],
        default="linear",
        help="Scale type for file size distribution"
    )
    
    args = parser.parse_args()
    
    # Initialize the profiling suite
    suite = ProfilingSuite(output_dir=args.output_dir)
    
    if args.graphs_only:
        if not args.json_dir:
            parser.error("--json-dir must be specified when using --graphs-only")
        
        # Only generate graphs from existing JSON data
        suite.generate_graphs_from_json(args.json_dir)
    else:
        # Run the full test suite
        file_sizes = [size for size, _ in suite.generate_file_sizes(
            scale_type=args.scale,
            min_size=args.min_size,
            max_size=args.max_size,
            steps=args.steps
        )]
        
        suite.run_tests(file_sizes)
