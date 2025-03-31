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

class ProfilingSuite:
    def __init__(self, output_dir="profiling_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
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
            os.remove(enc_file_path)
            print(f"Test file {file_path} and {enc_file_path} removed.")

    def measure_performance(self, func, *args, **kwargs):
        process = psutil.Process(os.getpid())
        start_time = time.time()
        start_memory = process.memory_info().rss
        start_cpu_times = process.cpu_times()

        result = func(*args, **kwargs)

        end_time = time.time()
        end_memory = process.memory_info().rss
        end_cpu_times = process.cpu_times()

        cpu_time_used = ((end_cpu_times.user + end_cpu_times.system) -
                         (start_cpu_times.user + start_cpu_times.system))
        elapsed_time = end_time - start_time
        cpu_percent = (cpu_time_used / elapsed_time * 100) if elapsed_time > 0 else 0

        return {
            "time": elapsed_time,
            "memory": end_memory - start_memory,
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
        pqfe_memory = [r["pqfe"]["average"]["memory"] for r in results]
        aes_memory = [r["aes"]["average"]["memory"] for r in results]
        pqfe_cpu = [r["pqfe"]["average"]["cpu"] for r in results]
        aes_cpu = [r["aes"]["average"]["cpu"] for r in results]

        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_memory, label="PQFE Memory Usage", marker="o")
        plt.plot(sizes, aes_memory, label="AES Memory Usage", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Memory Usage (bytes)")
        plt.title("Memory Usage vs File Size")
        plt.legend()
        plt.savefig(self.output_dir / "memory_vs_size.png")
        plt.close()

        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_cpu, label="PQFE CPU Usage", marker="o")
        plt.plot(sizes, aes_cpu, label="AES CPU Usage", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("CPU Usage (%)")
        plt.title("CPU Usage vs File Size")
        plt.legend()
        plt.savefig(self.output_dir / "cpu_vs_size.png")
        plt.close()

        pqfe_storage = []
        for r in results:
            pqfe_result = r["pqfe"]["average"]
            if "encrypted_data" in pqfe_result:
                pqfe_storage.append(len(pqfe_result["encrypted_data"]))
            elif pqfe_result.get("encrypted_file_path"):
                pqfe_storage.append(os.path.getsize(pqfe_result["encrypted_file_path"]))
            else:
                pqfe_storage.append(0)
        aes_storage = [
            len(r["aes"]["average"].get("result", [b""])[0]) if "result" in r["aes"]["average"] else 0
            for r in results
        ]

        plt.figure(figsize=(10, 6))
        plt.plot(sizes, pqfe_storage, label="PQFE Encrypted Size", marker="o")
        plt.plot(sizes, aes_storage, label="AES Encrypted Size", marker="o")
        plt.xlabel("File Size (bytes)")
        plt.ylabel("Encrypted File Size (bytes)")
        plt.title("Encrypted File Size vs Original File Size")
        plt.legend()
        plt.savefig(self.output_dir / "storage_vs_size.png")
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

                for _ in range(10):  # Run each test 10 times
                    for attempt in range(5):
                        pqfe_metrics = self.measure_performance(
                            self.pqfe_encrypt_decrypt, file_path, pqfe, public_key, private_key
                        )
                        if pqfe_metrics["cpu"] <= 100 or attempt == 4:
                            break
                        print(f"Retrying PQFE test for file size {size} due to high CPU utilization ({pqfe_metrics['cpu']}%).")

                    for attempt in range(5):
                        aes_metrics = self.measure_performance(
                            self.aes_encrypt_decrypt, file_path, aes_key
                        )
                        if aes_metrics["cpu"] <= 100 or attempt == 4:
                            break
                        print(f"Retrying AES test for file size {size} due to high CPU utilization ({aes_metrics['cpu']}%).")

                    pqfe_metrics_list.append(pqfe_metrics)
                    aes_metrics_list.append(aes_metrics)

                # Remove the 'result' field from individual runs and averages
                for metric in pqfe_metrics_list:
                    if "result" in metric:
                        del metric["result"]
                for metric in aes_metrics_list:
                    if "result" in metric:
                        del metric["result"]

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

                results.append({
                    "size": size,
                    "pqfe": {
                        "individual_runs": pqfe_metrics_list,
                        "average": avg_pqfe_metrics
                    },
                    "aes": {
                        "individual_runs": aes_metrics_list,
                        "average": avg_aes_metrics
                    }
                })
                print(f"Tests for file size {size} bytes completed.")
            finally:
                self.cleanup_test_file(file_path)
                del pqfe, pqfe_metrics_list, aes_metrics_list, pqfe_metrics, aes_metrics, avg_pqfe_metrics, avg_aes_metrics
                import gc
                gc.collect()

        # Save detailed results to JSON
        with open(self.output_dir / "graph_data.json", "w") as f:
            json.dump(results, f, indent=4)

        print("All tests completed. Generating plots...")
        self.plot_results(results)
        self.plot_additional_metrics(results)
        print("Plots generated and saved.")

if __name__ == "__main__":
    suite = ProfilingSuite()

    # More evenly spaced file sizes (logarithmic scale)
    file_sizes = [
        1024           # 1 KB
        # 2048,           # 2 KB
        # 4096,           # 4 KB
        # 8192,           # 8 KB
        # 16384,          # 16 KB
        # 32768,          # 32 KB
        # 65536,          # 64 KB
        # 131072,         # 128 KB
        # 262144,         # 256 KB
        # 524288,         # 512 KB
        # 1048576,        # 1 MB
        # 2097152,        # 2 MB
        # 4194304,        # 4 MB
        # 8388608,        # 8 MB
        # 16777216,       # 16 MB
        # 33554432,       # 32 MB
        # 67108864,       # 64 MB
        # 134217728,      # 128 MB
        # 268435456,      # 256 MB
        # 536870912,      # 512 MB
        # 1073741824      # 1 GB
    ]

    suite.run_tests(file_sizes)
