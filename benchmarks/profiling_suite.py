import os
import time
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
import multiprocessing
from pathlib import Path
from src.api import PQFE
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json

class ProfilingSuite:
    def __init__(self, output_dir="profiling_results", num_cores=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.num_cores = num_cores or multiprocessing.cpu_count()
        print(f"Using {self.num_cores} CPU cores for testing.")

    def generate_test_file(self, size_in_bytes, file_path):
        print(f"Generating test file of size {size_in_bytes} bytes...")
        with open(file_path, "wb") as f:
            f.write(os.urandom(size_in_bytes))
        print(f"Test file {file_path} generated.")

    def cleanup_test_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Test file {file_path} removed.")

    def measure_performance(self, func, *args, **kwargs):
        # Set process affinity to enforce the specified number of cores
        process = psutil.Process(os.getpid())
        process.cpu_affinity(list(range(self.num_cores)))
        
        # Capture baseline CPU times and memory before running function
        start_time = time.time()
        start_memory = process.memory_info().rss
        start_cpu_times = process.cpu_times()
        
        result = func(*args, **kwargs)
        
        # Capture post-run metrics
        end_time = time.time()
        end_memory = process.memory_info().rss
        end_cpu_times = process.cpu_times()
        
        # Calculate CPU time used (user+system)
        cpu_time_used = ((end_cpu_times.user + end_cpu_times.system) -
                         (start_cpu_times.user + start_cpu_times.system))
        elapsed_time = end_time - start_time
        # Normalize CPU usage to the number of allocated cores
        cpu_percent = (cpu_time_used / elapsed_time * 100 / self.num_cores) if elapsed_time > 0 else 0
        
        return {
            "time": elapsed_time,
            "memory": end_memory - start_memory,
            "cpu": cpu_percent,
            "result": result
        }

    def pqfe_encrypt_decrypt(self, file_path, pqfe_instance, public_key, private_key):
        print(f"Running PQFE encryption and decryption for {file_path}...")
        encrypt_result = pqfe_instance.encrypt_file(file_path, public_key=public_key, return_as_data=True)
        decrypt_result = pqfe_instance.decrypt_file(
            encrypted_file=file_path,
            ciphertext=encrypt_result["ciphertext"],
            private_key=private_key,
            return_as_data=True,
            encrypted_data=encrypt_result["encrypted_data"]
        )
        print(f"PQFE encryption and decryption for {file_path} completed.")
        # Return as a tuple (encrypt_result, decrypt_result)
        return (encrypt_result, decrypt_result)

    def aes_encrypt_decrypt(self, file_path, key):
        print(f"Running AES encryption and decryption for {file_path}...")
        aesgcm = AESGCM(key)
        with open(file_path, "rb") as f:
            data = f.read()
        nonce = os.urandom(12)
        encrypted_data = aesgcm.encrypt(nonce, data, None)
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
        print(f"AES encryption and decryption for {file_path} completed.")
        # Return a tuple for consistency; first element is the encrypted data
        return (encrypted_data, decrypted_data)

    def plot_results(self, results):
        sns.set(style="whitegrid")
        sizes = [r["size"] for r in results]
        pqfe_times = [r["pqfe"]["time"] for r in results]
        aes_times = [r["aes"]["time"] for r in results]

        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_times, label="PQFE", marker="o")
        plt.plot(sizes, aes_times, label="AES", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Time (seconds)")
        plt.title("Encryption/Decryption Time vs File Size")
        plt.legend()
        plt.savefig(self.output_dir / "time_vs_size.png")
        plt.close()

    def plot_additional_metrics(self, results):
        sns.set(style="whitegrid")
        sizes = [r["size"] for r in results]
        pqfe_memory = [r["pqfe"]["memory"] for r in results]
        aes_memory = [r["aes"]["memory"] for r in results]
        pqfe_cpu = [r["pqfe"]["cpu"] for r in results]
        aes_cpu = [r["aes"]["cpu"] for r in results]

        # Plot Memory Usage
        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_memory, label="PQFE Memory Usage", marker="o")
        plt.plot(sizes, aes_memory, label="AES Memory Usage", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Memory Usage (bytes)")
        plt.title("Memory Usage vs File Size")
        plt.legend()
        plt.savefig(self.output_dir / "memory_vs_size.png")
        plt.close()

        # Plot CPU Usage
        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_cpu, label="PQFE CPU Usage", marker="o")
        plt.plot(sizes, aes_cpu, label="AES CPU Usage", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("CPU Usage (%)")
        plt.title("CPU Usage vs File Size")
        plt.legend()
        plt.savefig(self.output_dir / "cpu_vs_size.png")
        plt.close()

        # Calculate storage used for encrypted data
        # For PQFE, extract from the encryption result (which is at index 0 of the tuple)
        pqfe_storage = []
        for r in results:
            pqfe_result = r["pqfe"]["result"][0]
            if "encrypted_data" in pqfe_result:
                pqfe_storage.append(len(pqfe_result["encrypted_data"]))
            elif pqfe_result.get("encrypted_file_path"):
                pqfe_storage.append(os.path.getsize(pqfe_result["encrypted_file_path"]))
            else:
                pqfe_storage.append(0)
        aes_storage = [len(r["aes"]["result"][0]) for r in results]

        # Plot Storage Size
        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_storage, label="PQFE Encrypted Size", marker="o")
        plt.plot(sizes, aes_storage, label="AES Encrypted Size", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Encrypted File Size (bytes)")
        plt.title("Encrypted File Size vs Original File Size")
        plt.legend()
        plt.savefig(self.output_dir / "storage_vs_size.png")
        plt.close()

        # Save data used to create graphs
        graph_data = {
            "sizes": sizes,
            "pqfe_memory": pqfe_memory,
            "aes_memory": aes_memory,
            "pqfe_cpu": pqfe_cpu,
            "aes_cpu": aes_cpu,
            "pqfe_storage": pqfe_storage,
            "aes_storage": aes_storage,
        }
        with open(self.output_dir / "graph_data.json", "w") as f:
            json.dump(graph_data, f, indent=4)

    def run_tests(self, file_sizes):
        print("Initializing PQFE and AES keys...")
        pqfe = PQFE()
        public_key, private_key = pqfe.generate_keys()
        aes_key = os.urandom(32)
        print("Keys initialized.")

        print("Waiting 40s for CPU to stabilize...")
        time.sleep(40)

        results = []

        for size in file_sizes:
            print(f"Starting tests for file size: {size} bytes...")
            file_path = self.output_dir / f"test_file_{size}.bin"
            self.generate_test_file(size, file_path)

            # Ensure CPU core constraint is enforced
            process = psutil.Process(os.getpid())
            process.cpu_affinity(list(range(self.num_cores)))

            pqfe_metrics = self.measure_performance(
                self.pqfe_encrypt_decrypt, file_path, pqfe, public_key, private_key
            )
            aes_metrics = self.measure_performance(
                self.aes_encrypt_decrypt, file_path, aes_key
            )

            results.append({
                "size": size,
                "pqfe": pqfe_metrics,
                "aes": aes_metrics
            })
            print(f"Tests for file size {size} bytes completed.")

            # Cleanup test file
            self.cleanup_test_file(file_path)

        print("All tests completed. Generating plots...")
        self.plot_results(results)
        self.plot_additional_metrics(results)
        print("Plots generated and saved.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run profiling tests for PQFE and AES encryption/decryption.")
    parser.add_argument("--cores", type=int, default=None, help="Number of CPU cores to use for testing.")
    args = parser.parse_args()

    suite = ProfilingSuite(num_cores=args.cores)
    
    # More data points: From 1KB to ~100MB with intermediate sizes
    file_sizes = [
        1024,           # 1 KB
        2048,           # 2 KB
        4096,           # 4 KB
        8192,           # 8 KB
        16384,          # 16 KB
        32768,          # 32 KB
        65536,          # 64 KB
        131072,         # 128 KB
        262144,         # 256 KB
        524288,         # 512 KB
        1048576,        # 1 MB
        2097152,        # 2 MB
        4194304,        # 4 MB
        8388608,        # 8 MB
        16777216,       # 16 MB
        33554432,       # 32 MB
        67108864,       # 64 MB
        134217728,      # 128 MB
        268435456,      # 256 MB
        536870912,      # 512 MB
        1073741824      # 1 GB
    ]
    
    suite.run_tests(file_sizes)
