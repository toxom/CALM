import sys
from pathlib import Path
import csv
import time
from itertools import product
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from core.sdm.memory import run_sdm_memory_test

# Parameter ranges
vector_dims = [32, 64, 128, 256, 512, 1024]
num_locations_list = [500, 1000, 3000, 5000, 8000]
access_radius_factors = [0.05, 0.1, 0.2, 0.4, 0.6, 0.78, 0.9]
reinforce_cycles = [1, 5, 10, 15, 30, 50, 100]

# Base output directory structure
BASE_OUTPUT_DIR = Path(__file__).parent.parent / "api" / "tests" / "SDMPreMark"

def get_csv_output_path(test_type: str, description: str = ""):
    """
    Generate organized CSV output path with incremental naming
    
    Args:
        test_type: Type of test (comprehensive, focused, critical, etc.)
        description: Optional description for the test
    
    Returns:
        Path: Full path to CSV file with incremental naming
    """
    # Create test-specific directory
    test_dir = BASE_OUTPUT_DIR / test_type
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp and find next available number
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Find highest existing test number
    existing_files = list(test_dir.glob(f"{test_type}_*.csv"))
    max_num = 0
    for file in existing_files:
        try:
            # Extract number from filename like "focused_001_20241225_123456.csv"
            parts = file.stem.split('_')
            if len(parts) >= 2 and parts[1].isdigit():
                max_num = max(max_num, int(parts[1]))
        except (ValueError, IndexError):
            continue
    
    next_num = max_num + 1
    
    # Create filename with incremental number and timestamp
    if description:
        filename = f"{test_type}_{next_num:03d}_{description}_{timestamp}.csv"
    else:
        filename = f"{test_type}_{next_num:03d}_{timestamp}.csv"
    
    csv_path = test_dir / filename
    
    print(f"Output will be saved to: {csv_path}")
    return csv_path

def estimate_runtime():
    """Estimate total benchmark runtime"""
    total_configs = len(vector_dims) * len(num_locations_list) * len(access_radius_factors) * len(reinforce_cycles)
    avg_time_per_test = 0.5  # seconds (conservative estimate)
    total_time = total_configs * avg_time_per_test
    
    print(f"Total configurations: {total_configs}")
    print(f"Estimated runtime: {total_time/3600:.1f} hours")
    print(f"Consider running subsets for initial analysis\n")
    
    return total_configs

def run_comprehensive_benchmark():
    """Run full parameter sweep"""
    total_configs = estimate_runtime()
    
    csv_output_path = get_csv_output_path("comprehensive", "full_sweep")
    
    with open(csv_output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "vector_dim", "num_locations", "access_radius", 
            "reinforce", "match_ratio", "input_ones_count",
            "recalled_ones_count", "duration_seconds", 
            "radius_factor", "sparsity_ratio"
        ])

        config_count = 0
        for vector_dim, num_locations, factor, reinforce in product(
            vector_dims, num_locations_list, access_radius_factors, reinforce_cycles
        ):
            config_count += 1
            access_radius = max(1, int(vector_dim * factor))
            
            print(f"Config {config_count}/{total_configs}: dim={vector_dim}, "
                  f"locs={num_locations}, r={access_radius}, reinforce={reinforce}")
            
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
            
            sparsity_ratio = summary["input_ones_count"] / vector_dim if vector_dim > 0 else 0

            writer.writerow([
                vector_dim, num_locations, access_radius, reinforce,
                summary["match_ratio"],
                summary["input_ones_count"],
                summary["recalled_ones_count"],
                round(duration, 4),
                round(factor, 3),
                round(sparsity_ratio, 4)
            ])

            if config_count % 50 == 0:
                print(f"Progress: {config_count}/{total_configs} ({100*config_count/total_configs:.1f}%)")

def run_focused_benchmark():
    """Run targeted subsets for specific research questions"""
    
    focus_dims = [128, 512]
    focus_locations = [1000, 5000]
    focus_factors = [0.1, 0.4, 0.6]
    
    total_configs = len(focus_dims) * len(focus_locations) * len(focus_factors) * len(reinforce_cycles)
    print("Running focused reinforcement analysis...")
    print(f"Configurations: {total_configs}")
    
    csv_output_path = get_csv_output_path("focused", "reinforcement_analysis")
    
    with open(csv_output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "vector_dim", "num_locations", "access_radius", 
            "reinforce", "match_ratio", "input_ones_count",
            "recalled_ones_count", "duration_seconds", 
            "radius_factor", "sparsity_ratio", "performance_regime"
        ])

        config_count = 0
        for vector_dim, num_locations, factor, reinforce in product(
            focus_dims, focus_locations, focus_factors, reinforce_cycles
        ):
            config_count += 1
            access_radius = max(1, int(vector_dim * factor))
            
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
            
            sparsity_ratio = summary["input_ones_count"] / vector_dim if vector_dim > 0 else 0
            
            if factor < 0.3:
                regime = "under_activation"
            elif factor < 0.5:
                regime = "transition"
            else:
                regime = "over_activation"

            writer.writerow([
                vector_dim, num_locations, access_radius, reinforce,
                summary["match_ratio"],
                summary["input_ones_count"], 
                summary["recalled_ones_count"],
                round(duration, 4),
                round(factor, 3),
                round(sparsity_ratio, 4),
                regime
            ])

            if config_count % 25 == 0:
                print(f"Progress: {config_count}/{total_configs} ({100*config_count/total_configs:.1f}%)")
                
            print(f"Done: dim={vector_dim}, r={access_radius}, reinforce={reinforce}, "
                  f"match={summary['match_ratio']:.3f}")

def run_critical_radius_mapping():
    """Map critical radius more precisely across reinforcement levels"""
    
    print("Running critical radius mapping...")
    
    fine_factors = [0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65]
    test_dims = [64, 256, 1024]
    test_locations = [1000]
    
    total_configs = len(test_dims) * len(fine_factors) * 4
    print(f"Total configurations: {total_configs}")
    
    csv_output_path = get_csv_output_path("critical", "radius_mapping")
    
    with open(csv_output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "vector_dim", "access_radius", "radius_factor", "reinforce", 
            "match_ratio", "success_binary", "input_sparsity"
        ])

        config_count = 0
        for vector_dim in test_dims:
            for factor in fine_factors:
                for reinforce in [1, 10, 30, 100]:
                    config_count += 1
                    access_radius = max(1, int(vector_dim * factor))
                    
                    result = run_sdm_memory_test(
                        vector_dim=vector_dim,
                        num_locations=1000,
                        access_radius=access_radius,
                        reinforce=reinforce
                    )

                    summary = result.get("summary", {
                        "match_ratio": result.get("match_ratio", None),
                        "input_ones_count": sum(result.get("input_vector", []))
                    })
                    
                    success_binary = 1 if summary["match_ratio"] > 0.8 else 0
                    input_sparsity = summary["input_ones_count"] / vector_dim if vector_dim > 0 else 0

                    writer.writerow([
                        vector_dim, access_radius, round(factor, 3), reinforce,
                        summary["match_ratio"], success_binary, round(input_sparsity, 4)
                    ])
                    
                    print(f"Critical mapping {config_count}/{total_configs}: dim={vector_dim}, "
                          f"factor={factor:.3f}, reinforce={reinforce}, success={success_binary}")

def test_dense_vs_sparse():
    """Quick test to compare dense vs sparse encoding"""
    
    print("\n=== DENSE VS SPARSE ENCODING COMPARISON ===")
    
    test_configs = [
        {"vector_dim": 128, "radius_factor": 0.1},
        {"vector_dim": 128, "radius_factor": 0.4},
        {"vector_dim": 128, "radius_factor": 0.6},
        {"vector_dim": 256, "radius_factor": 0.4},
    ]
    
    csv_output_path = get_csv_output_path("comparison", "dense_vs_sparse")
    
    results = []
    
    with open(csv_output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "vector_dim", "radius_factor", "access_radius", "encoding_type",
            "match_ratio", "input_ones_count", "sparsity_ratio", "regime"
        ])
        
        for config in test_configs:
            vector_dim = config["vector_dim"]
            radius_factor = config["radius_factor"] 
            access_radius = max(1, int(vector_dim * radius_factor))
            
            print(f"\nTesting: dim={vector_dim}, radius_factor={radius_factor}")
            
            # Test current implementation (assuming it's using sparse encoding)
            try:
                current_result = run_sdm_memory_test(
                    vector_dim=vector_dim,
                    num_locations=1000,
                    access_radius=access_radius,
                    reinforce=30
                )
                current_match = current_result['summary']['match_ratio']
                current_ones = current_result['summary']['input_ones_count']
                current_sparsity = current_ones / vector_dim
                
                # Determine if this is sparse or dense based on sparsity
                encoding_type = "sparse" if current_sparsity < 0.1 else "dense"
                
                # Determine regime
                if radius_factor < 0.3:
                    regime = "under_activation"
                elif radius_factor < 0.5:
                    regime = "transition"
                else:
                    regime = "over_activation"
                
                writer.writerow([
                    vector_dim, radius_factor, access_radius, encoding_type,
                    current_match, current_ones, round(current_sparsity, 4), regime
                ])
                
                results.append({
                    'vector_dim': vector_dim,
                    'radius_factor': radius_factor,
                    'encoding_type': encoding_type,
                    'match_ratio': current_match,
                    'sparsity': current_sparsity
                })
                
                print(f"  {encoding_type.title()} ({current_sparsity*100:.1f}%): {current_match:.3f}")
                
            except Exception as e:
                print(f"Test failed: {e}")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    for r in results:
        regime = "under" if r['radius_factor'] < 0.3 else "transition" if r['radius_factor'] < 0.5 else "over"
        print(f"Dim {r['vector_dim']}, {regime}-activation: {r['encoding_type']} "
              f"({r['sparsity']*100:.1f}%) = {r['match_ratio']:.3f}")
    
    return results

def test_sparse_only():
    """Test to confirm we're using sparse encoding"""
    
    print("\n=== SPARSE ENCODING CONFIRMATION TEST ===")
    
    csv_output_path = get_csv_output_path("validation", "sparse_confirmation")
    
    test_cases = [
        {"vector_dim": 64, "radius_factor": 0.2},
        {"vector_dim": 128, "radius_factor": 0.3},
        {"vector_dim": 256, "radius_factor": 0.4},
        {"vector_dim": 512, "radius_factor": 0.5},
    ]
    
    with open(csv_output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "vector_dim", "radius_factor", "access_radius", "match_ratio", 
            "input_ones_count", "actual_sparsity", "expected_performance"
        ])
        
        for case in test_cases:
            vector_dim = case["vector_dim"]
            radius_factor = case["radius_factor"]
            access_radius = max(1, int(vector_dim * radius_factor))
            
            result = run_sdm_memory_test(
                vector_dim=vector_dim,
                num_locations=1000,
                access_radius=access_radius,
                reinforce=30
            )
            
            summary = result['summary']
            actual_sparsity = summary['input_ones_count'] / vector_dim
            
            # If we're truly using sparse encoding, sparsity should be < 10%
            if actual_sparsity < 0.1:
                expected = "perfect_sparse"
                status = "✅ SPARSE"
            else:
                expected = "dense_with_threshold"
                status = "❌ DENSE"
            
            writer.writerow([
                vector_dim, radius_factor, access_radius, summary['match_ratio'],
                summary['input_ones_count'], round(actual_sparsity, 4), expected
            ])
            
            print(f"Dim {vector_dim}: {actual_sparsity*100:.1f}% sparsity, "
                  f"match={summary['match_ratio']:.3f} {status}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("Choose benchmark mode:")
        print("1. comprehensive - Full parameter sweep (long runtime)")
        print("2. focused - Reinforcement effect analysis (recommended)")
        print("3. critical - Critical radius mapping (precise)")
        print("4. compare - Dense vs Sparse comparison (quick)")
        print("5. validate - Confirm sparse encoding is working")
        choice = input("Enter choice (1/2/3/4/5): ").strip()
        mode = {"1": "comprehensive", "2": "focused", "3": "critical", 
               "4": "compare", "5": "validate"}.get(choice, "focused")
    
    # DEBUG: Show what mode was selected
    print(f"DEBUG: choice='{choice}' → mode='{mode}'")
    print(f"Running {mode} benchmark...")
    print(f"Results will be organized in: {BASE_OUTPUT_DIR}")
    
    if mode == "comprehensive":
        print("DEBUG: Calling run_comprehensive_benchmark()")
        run_comprehensive_benchmark()
    elif mode == "focused":
        print("DEBUG: Calling run_focused_benchmark()")
        run_focused_benchmark()
    elif mode == "critical":
        print("DEBUG: Calling run_critical_radius_mapping()")
        run_critical_radius_mapping()
    elif mode == "compare":
        print("DEBUG: Calling test_dense_vs_sparse()")
        test_dense_vs_sparse()
    elif mode == "validate":
        print("DEBUG: Calling test_sparse_only()")
        test_sparse_only()
    else:
        print(f"DEBUG: Invalid mode '{mode}'. Running focused benchmark.")
        run_focused_benchmark()
    
    print("Benchmark complete!")