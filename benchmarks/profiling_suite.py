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

    def cleanup_test_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            enc_file_path = f"{file_path}.enc"
            if os.path.exists(enc_file_path):
                os.remove(enc_file_path)
            print(f"Test file {file_path} and related files removed.")
    
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
        print(f"Running PQFE encryption and decryption for {file_path}...")
        encrypt_result = pqfe_instance.encrypt_file(
            file_path=file_path,
            public_key=public_key,
            return_as_data=False
        )
        encrypted_file_path = encrypt_result["encrypted_file_path"]
        ciphertext = encrypt_result["ciphertext"]

        decrypt_result = pqfe_instance.decrypt_file(
            encrypted_file=encrypted_file_path,
            ciphertext=ciphertext,
            private_key=private_key,
            return_as_data=False
        )
        decrypted_file_path = decrypt_result["decrypted_file_path"]

        print(f"PQFE encryption and decryption for {file_path} completed.")
        return (encrypted_file_path, decrypted_file_path)

    def pqfe_encrypt_decrypt_in_memory(self, data: bytes, pqfe_instance, public_key, private_key):
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
        sns.set(style="whitegrid")
        sizes = [r["size"] for r in results]
        pqfe_times = [r["pqfe"]["average"]["time"] for r in results]
        aes_times = [r["aes"]["average"]["time"] for r in results]
        pqfe_in_memory_times = [r["pqfe_in_memory"]["average"]["time"] for r in results]

        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_times, label="PQFE (File-Based)", marker="o")
        plt.plot(sizes, pqfe_in_memory_times, label="PQFE (In-Memory)", marker="o")
        plt.plot(sizes, aes_times, label="AES", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Time (seconds)")
        plt.title("Encryption/Decryption Time vs File Size")
        plt.legend()
        plt.savefig(self.charts_dir / "time_vs_size.png")
        plt.close()

    def plot_additional_metrics(self, results):
        sns.set(style="whitegrid")
        sizes = [r["size"] for r in results]
        pqfe_memory = [r["pqfe"]["average"]["memory"] for r in results]
        aes_memory = [r["aes"]["average"]["memory"] for r in results]
        pqfe_in_memory_memory = [r["pqfe_in_memory"]["average"]["memory"] for r in results]
        
        pqfe_cpu = [r["pqfe"]["average"]["cpu"] for r in results]
        aes_cpu = [r["aes"]["average"]["cpu"] for r in results]
        pqfe_in_memory_cpu = [r["pqfe_in_memory"]["average"]["cpu"] for r in results]

        # Memory usage plot
        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_memory, label="PQFE (File-Based) Memory", marker="o")
        plt.plot(sizes, pqfe_in_memory_memory, label="PQFE (In-Memory) Memory", marker="o")
        plt.plot(sizes, aes_memory, label="AES Memory", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Memory Usage (bytes)")
        plt.title("Memory Usage vs File Size")
        plt.legend()
        plt.savefig(self.charts_dir / "memory_vs_size.png")
        plt.close()

        # CPU usage plot
        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_cpu, label="PQFE (File-Based) CPU", marker="o")
        plt.plot(sizes, pqfe_in_memory_cpu, label="PQFE (In-Memory) CPU", marker="o")
        plt.plot(sizes, aes_cpu, label="AES CPU", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("CPU Usage (%)")
        plt.title("CPU Usage vs File Size")
        plt.legend()
        plt.savefig(self.charts_dir / "cpu_vs_size.png")
        plt.close()

        # Storage plot - attempt to get metrics for all three types
        pqfe_storage = []
        pqfe_in_memory_storage = []
        aes_storage = []
        
        for r in results:
            # File-based PQFE
            pqfe_result = r["pqfe"]["average"]
            if "encrypted_data" in pqfe_result:
                pqfe_storage.append(len(pqfe_result["encrypted_data"]))
            elif pqfe_result.get("encrypted_file_path"):
                pqfe_storage.append(os.path.getsize(pqfe_result["encrypted_file_path"]))
            else:
                pqfe_storage.append(0)
            
            # In-memory PQFE
            pqfe_in_mem_result = r["pqfe_in_memory"]["average"]
            pqfe_in_memory_storage.append(0)  # Default value
            # Try to extract size from individual runs if available
            for run in r["pqfe_in_memory"]["individual_runs"]:
                if "result" in run and isinstance(run["result"], (list, tuple)) and len(run["result"]) > 0:
                    if hasattr(run["result"][0], "__len__"):
                        pqfe_in_memory_storage[-1] = len(run["result"][0])
                        break
            
            # AES
            aes_result = r["aes"]["average"]
            if "result" in aes_result and isinstance(aes_result["result"], (list, tuple)) and len(aes_result["result"]) > 0:
                if hasattr(aes_result["result"][0], "__len__"):
                    aes_storage.append(len(aes_result["result"][0]))
                else:
                    aes_storage.append(0)
            else:
                aes_storage.append(0)

        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_storage, label="PQFE (File-Based) Size", marker="o")
        plt.plot(sizes, pqfe_in_memory_storage, label="PQFE (In-Memory) Size", marker="o")
        plt.plot(sizes, aes_storage, label="AES Size", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Encrypted Size (bytes)")
        plt.title("Encrypted Size vs Original File Size")
        plt.legend()
        plt.savefig(self.charts_dir / "storage_vs_size.png")
        plt.close()


    def run_tests(self, file_sizes):
        print("Initializing PQFE and AES keys...")
        public_key, private_key = PQFE().generate_keys()
        aes_key = os.urandom(32)
        print("Keys initialized.")

        results = []

        for size in file_sizes:
            print(f"Starting tests for file size: {size} bytes...")
            pqfe = PQFE()  # Initialize PQFE instance for each test
            file_path = self.output_dir / f"test_file_{size}.bin"
            self.generate_test_file(size, file_path)

            try:
                pqfe_metrics_list = []
                aes_metrics_list = []
                pqfe_in_memory_metrics_list = []

                for _ in range(10):  # Run each test 10 times
                    for attempt in range(5):
                        pqfe_metrics = self.measure_performance(
                            self.pqfe_encrypt_decrypt, file_path, pqfe, public_key, private_key
                        )
                        if pqfe_metrics["cpu"] <= 110 or attempt == 4:
                            break
                        print(f"Retrying PQFE test for file size {size} due to high CPU utilization ({pqfe_metrics['cpu']}%).")

                    for attempt in range(5):
                        aes_metrics = self.measure_performance(
                            self.aes_encrypt_decrypt, file_path, aes_key
                        )
                        if aes_metrics["cpu"] <= 100 or attempt == 4:
                            break
                        print(f"Retrying AES test for file size {size} due to high CPU utilization ({aes_metrics['cpu']}%).")

                    with open(file_path, "rb") as f:
                        data = f.read()

                    for attempt in range(5):
                        pqfe_in_memory_metrics = self.measure_performance(
                            self.pqfe_encrypt_decrypt_in_memory, data, pqfe, public_key, private_key
                        )
                        if pqfe_in_memory_metrics["cpu"] <= 100 or attempt == 4:
                            break
                        print(f"Retrying PQFE in-memory test for file size {size} due to high CPU utilization ({pqfe_in_memory_metrics['cpu']}%).")

                    # Replace binary data with metadata before adding to metrics lists
                    if "result" in pqfe_metrics and isinstance(pqfe_metrics["result"], tuple):
                        # Keep file paths for PQFE
                        pqfe_metrics["result"] = [str(path) for path in pqfe_metrics["result"]]
                    
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
                avg_pqfe_metrics = {
                    "time": sum(m["time"] for m in pqfe_metrics_list) / 10,
                    "memory": sum(m["memory"] for m in pqfe_metrics_list) / 10,
                    "cpu": sum(m["cpu"] for m in pqfe_metrics_list) / 10,
                }

                avg_aes_metrics = {
                    "time": sum(m["time"] for m in aes_metrics_list) / 10,
                    "memory": sum(m["memory"] for m in aes_metrics_list) / 10,
                    "cpu": sum(m["cpu"] for m in aes_metrics_list) / 10,
                }

                avg_pqfe_in_memory_metrics = {
                    "time": sum(m["time"] for m in pqfe_in_memory_metrics_list) / 10,
                    "memory": sum(m["memory"] for m in pqfe_in_memory_metrics_list) / 10,
                    "cpu": sum(m["cpu"] for m in pqfe_in_memory_metrics_list) / 10,
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
                self.cleanup_test_file(file_path)
                del pqfe, pqfe_metrics_list, aes_metrics_list, pqfe_in_memory_metrics_list, pqfe_metrics, aes_metrics, pqfe_in_memory_metrics, avg_pqfe_metrics, avg_aes_metrics, avg_pqfe_in_memory_metrics
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
    suite = ProfilingSuite()

    # More evenly spaced file sizes (logarithmic scale)
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
