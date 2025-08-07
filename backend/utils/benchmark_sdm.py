from pathlib import Path
import csv
import time
from backend.core.sdm.memory import run_sdm_memory_test

# Define parameter ranges
vector_dims = [32, 64, 128, 256, 512, 1024]
num_locations_list = [500, 1000, 3000, 5000, 8000]
access_radius_factors = [0.05, 0.1, 0.2, 0.4, 0.6, 0.78, 0.9]
reinforce = 30

csv_output_path = Path(__file__).parent.parent / "api" / "tests" / "sdm_benchmark_results.csv"
csv_output_path.parent.mkdir(parents=True, exist_ok=True)

with open(csv_output_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "vector_dim", "num_locations", "access_radius",
        "reinforce", "match_ratio", "input_ones_count",
        "recalled_ones_count", "duration_seconds"
    ])

    for vector_dim in vector_dims:
        for num_locations in num_locations_list:
            for factor in access_radius_factors:
                access_radius = max(1, int(vector_dim * factor))  # always at least 1

                start_time = time.perf_counter()
                result = run_sdm_memory_test(
                    vector_dim=vector_dim,
                    num_locations=num_locations,
                    access_radius=access_radius,
                    reinforce=reinforce
                )
                duration = time.perf_counter() - start_time

                summary = result.get("summary", {
                    "match_ratio": result.get("match_ratio", None),
                    "input_ones_count": sum(result.get("input_vector", [])),
                    "recalled_ones_count": sum(result.get("recalled_vector", []))
                })

                writer.writerow([
                    vector_dim, num_locations, access_radius,
                    reinforce,
                    summary["match_ratio"],
                    summary["input_ones_count"],
                    summary["recalled_ones_count"],
                    round(duration, 4)
                ])

                print(f"Done: vec_dim={vector_dim}, locs={num_locations}, r={access_radius}, time={duration:.4f}s")

print(f"Benchmark complete! Results in {csv_output_path}")