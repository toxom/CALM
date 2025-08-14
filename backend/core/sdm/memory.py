import numpy as np
import matplotlib.pyplot as plt
import sys
from typing import Dict, List, Tuple, Optional
class SparseDistributedMemory:
    def __init__(self, vector_dim=1024, num_locations=1000, access_radius=100):
        """
        Enhanced SDM with better sparsity control and analysis capabilities.
        
        Args:
            vector_dim: Dimensionality of binary vectors.
            num_locations: Number of hard memory locations.
            access_radius: Max Hamming distance to activate locations.
        """
        self.vector_dim = vector_dim
        self.num_locations = num_locations
        self.access_radius = access_radius

        # Initialize random fixed hard locations (addresses)
        self.addresses = self._generate_addresses(target_sparsity=0.03)
        # Memory locations store integer counts per bit (for weighted sums)
        self.memory = np.zeros((num_locations, vector_dim), dtype=int)
        # Track access counts for each location
        self.access_counts = np.zeros(num_locations, dtype=int)
        
        # Statistics tracking
        self.write_stats = []
        self.read_stats = []

    def _generate_addresses(self, target_sparsity=0.03):
        """
        Generate random binary addresses with specified sparsity.
        
        Args:
            target_sparsity: Fraction of bits that should be 1 (0.02-0.05 optimal)
        """
        # Dense implementation for high sparsity (backward compatibility)
        if target_sparsity >= 0.1:
            return np.random.randint(2, size=(self.num_locations, self.vector_dim))
        
        #Ssparse implementation for low sparsity (optimal)
        addresses = np.zeros((self.num_locations, self.vector_dim), dtype=int)
        for i in range(self.num_locations):
            num_ones = int(self.vector_dim * target_sparsity)
            if num_ones > 0:  # Avoiding empty vectors
                indices = np.random.choice(self.vector_dim, num_ones, replace=False)
                addresses[i, indices] = 1
        return addresses

    def _hamming_distance(self, v1, v2):
        """Compute Hamming distance between two binary vectors"""
        return np.sum(v1 != v2)

    def write(self, input_vector, strength=1):
        """
        Store input_vector into all locations within access_radius
        
        Args:
            input_vector: binary numpy array (0/1)
            strength: how much to reinforce this pattern (default=1)
        """
        activated_locations = []
        
        # DEBUG: Add this to diagnose the issue
        min_distance = float('inf')
        max_distance = 0
        
        for i, addr in enumerate(self.addresses):
            dist = self._hamming_distance(input_vector, addr)
            min_distance = min(min_distance, dist)
            max_distance = max(max_distance, dist)
            
            if dist <= self.access_radius:
                activated_locations.append(i)
                self.access_counts[i] += 1
                
                # FIXED: Your current write operation has issues
                # Original: self.memory[i] += np.where(input_vector == 1, 2, -1)
                # Problem: This can make memory go negative and creates bias
                
                # Better approach: Store the actual pattern with reinforcement
                self.memory[i] += np.where(input_vector == 1, strength, -strength)
        
        # DEBUG: Print diagnostic info
        print(f"DEBUG: access_radius={self.access_radius}, min_dist={min_distance}, max_dist={max_distance}, activated={len(activated_locations)}")
        
        # Track statistics
        self.write_stats.append({
            'activated_locations': len(activated_locations),
            'activation_rate': len(activated_locations) / self.num_locations,
            'pattern_sparsity': np.mean(input_vector)
        })
        
        return len(activated_locations)
    def read(self, query_vector):
        """
        Recall from memory by weighted sum of nearby locations.
        
        Args:
            query_vector: binary numpy array (0/1)
        Returns:
            output_vector: binary numpy array (0/1)
            confidence: measure of retrieval confidence
        """
        activated_idxs = []
        distances = []
        
        for i, addr in enumerate(self.addresses):
            dist = self._hamming_distance(query_vector, addr)
            if dist <= self.access_radius:
                activated_idxs.append(i)
                distances.append(dist)

        if not activated_idxs:
            # No nearby locations found; return empty
            return np.zeros(self.vector_dim, dtype=int), 0.0

        # Weight by inverse distance (closer = higher weight)
        weights = np.array([1.0 / (1.0 + d) for d in distances])
        weights = weights / np.sum(weights)  # Normalize
        
        # Weighted sum of activated memory locations
        total = np.zeros(self.vector_dim)
        for idx, weight in zip(activated_idxs, weights):
            total += weight * self.memory[idx]
        
        # Threshold to get binary output
        output_vector = (total > 0).astype(int)
        
        # Calculate confidence based on activation strength
        confidence = np.max(np.abs(total)) if len(total) > 0 else 0.0
        
        # Track statistics
        self.read_stats.append({
            'activated_locations': len(activated_idxs),
            'activation_rate': len(activated_idxs) / self.num_locations,
            'confidence': confidence,
            'avg_distance': np.mean(distances) if distances else float('inf')
        })
        
        return output_vector, confidence
    
    def get_memory_statistics(self):
        """Get comprehensive statistics about memory state"""
        return {
            'memory_utilization': np.mean(self.access_counts > 0),
            'avg_access_count': np.mean(self.access_counts),
            'max_access_count': np.max(self.access_counts),
            'memory_magnitude': np.mean(np.abs(self.memory)),
            'write_stats': self.write_stats,
            'read_stats': self.read_stats
        }

def generate_sparse_vector(dim: int, sparsity: float = 0.05) -> np.ndarray:
    """
    Generate properly sparse binary vector (unlike your current dense ones)
    
    Args:
        dim: vector dimension
        sparsity: fraction of bits that should be 1 (0.02-0.05 is optimal)
    """
    vector = np.zeros(dim, dtype=int)
    num_ones = int(dim * sparsity)
    indices = np.random.choice(dim, num_ones, replace=False)
    vector[indices] = 1
    return vector

def run_reinforcement_analysis(vector_dim=128, num_locations=1000, access_radius=20):
    """
    Analyze how reinforcement cycles affect performance
    """
    sdm = SparseDistributedMemory(vector_dim=vector_dim, 
    num_locations=num_locations, 
    access_radius=access_radius)
    
    # Test with both dense (your current) and sparse vectors
    dense_vector = np.random.randint(2, size=vector_dim)  # ~50% sparsity
    sparse_vector = generate_sparse_vector(vector_dim, sparsity=0.03)  # 3% sparsity
    
    results = {
        'dense': {'reinforcement': [], 'match_ratio': [], 'confidence': []},
        'sparse': {'reinforcement': [], 'match_ratio': [], 'confidence': []}
    }
    
    reinforcement_levels = [1, 2, 5, 10, 15, 20, 30, 50, 100]
    
    for reinforce in reinforcement_levels:
        print(f"Testing reinforcement level: {reinforce}")
        
        # Test dense vector (your current approach)
        sdm_dense = SparseDistributedMemory(vector_dim, num_locations, access_radius)
        for _ in range(reinforce):
            sdm_dense.write(dense_vector)
        
        output_dense, conf_dense = sdm_dense.read(dense_vector)
        match_ratio_dense = np.mean(dense_vector == output_dense)
        
        # Test sparse vector (better approach)
        sdm_sparse = SparseDistributedMemory(vector_dim, num_locations, access_radius)
        for _ in range(reinforce):
            sdm_sparse.write(sparse_vector)
        
        output_sparse, conf_sparse = sdm_sparse.read(sparse_vector)
        match_ratio_sparse = np.mean(sparse_vector == output_sparse)
        
        # Store results
        results['dense']['reinforcement'].append(reinforce)
        results['dense']['match_ratio'].append(match_ratio_dense)
        results['dense']['confidence'].append(conf_dense)
        
        results['sparse']['reinforcement'].append(reinforce)
        results['sparse']['match_ratio'].append(match_ratio_sparse)
        results['sparse']['confidence'].append(conf_sparse)
        
        print(f"  Dense vector (50% sparsity): match={match_ratio_dense:.3f}, conf={conf_dense:.2f}")
        print(f"  Sparse vector (3% sparsity): match={match_ratio_sparse:.3f}, conf={conf_sparse:.2f}")
    
    return results

def plot_reinforcement_effects(results):
    """Plot the effects of reinforcement on performance"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot match ratios
    ax1.plot(results['dense']['reinforcement'], results['dense']['match_ratio'], 
    'ro-', label='Dense Vector (50% sparsity)', linewidth=2, markersize=8)
    ax1.plot(results['sparse']['reinforcement'], results['sparse']['match_ratio'], 
    'bo-', label='Sparse Vector (3% sparsity)', linewidth=2, markersize=8)
    
    ax1.set_xlabel('Reinforcement Cycles')
    ax1.set_ylabel('Match Ratio')
    ax1.set_title('Match Ratio vs Reinforcement Cycles')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.1)
    
    # Plot confidence levels
    ax2.plot(results['dense']['reinforcement'], results['dense']['confidence'], 
             'rs-', label='Dense Vector', linewidth=2, markersize=8)
    ax2.plot(results['sparse']['reinforcement'], results['sparse']['confidence'], 
             'bs-', label='Sparse Vector', linewidth=2, markersize=8)
    
    ax2.set_xlabel('Reinforcement Cycles')
    ax2.set_ylabel('Confidence Score')
    ax2.set_title('Confidence vs Reinforcement Cycles')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def run_enhanced_sdm_test(vector_dim=32, num_locations=3000, access_radius=18, 
                       reinforce=30, use_sparse_encoding=True, target_sparsity=0.03):
    """
    Enhanced version of your test function with better analysis
    """
    sdm = SparseDistributedMemory(vector_dim=vector_dim, 
    num_locations=num_locations, 
    access_radius=access_radius)
    
    # Generate input vector
    if use_sparse_encoding:
        # Use the target sparsity for sparse vectors
        actual_sparsity = target_sparsity if target_sparsity < 0.1 else 0.03
        input_vec = generate_sparse_vector(vector_dim, sparsity=actual_sparsity)
        print(f"Using sparse encoding ({actual_sparsity*100:.1f}%): {np.sum(input_vec)}/{vector_dim} bits active")
    else:
        input_vec = np.random.randint(2, size=vector_dim)
        print(f"Using dense encoding: {np.sum(input_vec)}/{vector_dim} bits active ({100*np.mean(input_vec):.1f}%)")

    # Write with reinforcement
    print(f"Writing pattern {reinforce} times...")
    for i in range(reinforce):
        activated = sdm.write(input_vec)
        if i == 0:
            print(f"First write activated {activated}/{num_locations} locations ({100*activated/num_locations:.1f}%)")
    
    # Read back
    output_vec, confidence = sdm.read(input_vec)
    match_ratio = float(np.mean(input_vec == output_vec))
    
    # Get detailed statistics
    stats = sdm.get_memory_statistics()
    
    summary = {
        "vector_dim": vector_dim,
        "num_locations": num_locations,
        "access_radius": access_radius,
        "reinforce": reinforce,
        "match_ratio": match_ratio,
        "confidence": confidence,
        "input_ones_count": int(np.sum(input_vec)),
        "recalled_ones_count": int(np.sum(output_vec)),
        "input_sparsity": float(np.mean(input_vec)),
        "first_16_bits_input": ''.join(map(str, input_vec[:16])),
        "first_16_bits_recalled": ''.join(map(str, output_vec[:16])),
        "activation_rate": stats['write_stats'][-1]['activation_rate'] if stats['write_stats'] else 0,
        "memory_utilization": stats['memory_utilization']
    }

    return {
        "summary": summary,
        "input_vector": input_vec.tolist(),
        "recalled_vector": output_vec.tolist(),
        "statistics": stats
    }

def run_sdm_memory_test(vector_dim=32, num_locations=3000, access_radius=18, 
                       reinforce=30, use_sparse_encoding=True, target_sparsity=0.03):

    result = run_enhanced_sdm_test(
        vector_dim, num_locations, access_radius, reinforce, 
        use_sparse_encoding=use_sparse_encoding,
        target_sparsity=target_sparsity 
    )
    return result


def run_swarm_sdm_test(num_agents=2, scenario="camera_ugv"):
    """
    Test SDM with swarm capabilities (minimal version — no optimizer)
    """
    if scenario == "camera_ugv":
        from .swarm.swarm_agent import create_camera_ugv_swarm_demo
        return create_camera_ugv_swarm_demo()
    raise ValueError(f"Unknown scenario: {scenario}")

if __name__ == "__main__":
    # Defaults
    scenario = "camera_ugv"
    num_agents = 2

    if len(sys.argv) > 1:
        scenario = sys.argv[1]
    if len(sys.argv) > 2:
        num_agents = int(sys.argv[2])

    result = run_swarm_sdm_test(num_agents=num_agents, scenario=scenario)
    print(result)

if __name__ == "__main__":
    # Default values
    scenario = "camera_ugv"
    num_agents = 2

    if len(sys.argv) > 1:
        scenario = sys.argv[1]
    if len(sys.argv) > 2:
        num_agents = int(sys.argv[2])

    result = run_swarm_sdm_test(num_agents=num_agents, scenario=scenario)
    print(result)

if __name__ == "__main__":
    print("=== SDM Reinforcement Analysis ===")
    print("\n1. Running reinforcement analysis...")
    
    # Run the reinforcement analysis
    results = run_reinforcement_analysis(vector_dim=128, num_locations=1000, access_radius=20)
    
    print("\n2. Plotting results...")
    plot_reinforcement_effects(results)
    
    print("\n3. Testing your original configuration...")
    
    # Test with your original parameters
    original_result = run_enhanced_sdm_test(vector_dim=32, num_locations=3000, 
    access_radius=18, reinforce=30)
    print("Original (dense) result:", original_result['summary']['match_ratio'])
    
    # Test with sparse encoding
    sparse_result = run_enhanced_sdm_test(vector_dim=32, num_locations=3000, 
    access_radius=18, reinforce=30, 
    use_sparse_encoding=True)
    print("Sparse encoding result:", sparse_result['summary']['match_ratio'])
    
