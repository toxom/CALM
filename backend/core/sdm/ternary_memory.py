# backend/core/sdm/ternary_memory.py
import numpy as np
from typing import Dict, Tuple

class TernarySparseDistributedMemory:
    """
    Balanced Ternary SDM using {-1, 0, +1} representation
    More expressive than binary, captures negation naturally
    """
    
    def __init__(self, vector_dim=1024, num_locations=1000, access_radius=100):
        self.vector_dim = vector_dim
        self.num_locations = num_locations
        self.access_radius = access_radius
        
        # Ternary addresses: {-1, 0, +1}
        self.addresses = self._generate_ternary_addresses(target_sparsity=0.05)
        
        # Memory stores ternary-weighted sums
        self.memory = np.zeros((num_locations, vector_dim), dtype=int)
        self.access_counts = np.zeros(num_locations, dtype=int)
        
        self.write_stats = []
        self.read_stats = []
    
    def _generate_ternary_addresses(self, target_sparsity=0.05):
        """Generate sparse ternary addresses"""
        addresses = np.zeros((self.num_locations, self.vector_dim), dtype=int)
        
        for i in range(self.num_locations):
            # Number of non-zero elements
            num_nonzero = int(self.vector_dim * target_sparsity)
            
            if num_nonzero > 0:
                indices = np.random.choice(self.vector_dim, num_nonzero, replace=False)
                # Randomly assign -1 or +1
                values = np.random.choice([-1, 1], size=num_nonzero)
                addresses[i, indices] = values
        
        return addresses
    
    def _ternary_distance(self, v1, v2):
        """
        Ternary distance metric
        - Same sign: distance 0
        - Different sign: distance 2
        - One zero: distance 1
        """
        diff = np.abs(v1 - v2)
        return np.sum(diff)
    
    def write(self, input_vector, strength=1):
        """
        Store ternary input_vector
        
        Args:
            input_vector: ternary numpy array {-1, 0, +1}
            strength: reinforcement strength
        """
        activated_locations = []
        
        for i, addr in enumerate(self.addresses):
            dist = self._ternary_distance(input_vector, addr)
            
            if dist <= self.access_radius:
                activated_locations.append(i)
                self.access_counts[i] += 1
                
                # Ternary reinforcement: add the pattern values directly
                self.memory[i] += input_vector * strength
        
        self.write_stats.append({
            'activated_locations': len(activated_locations),
            'activation_rate': len(activated_locations) / self.num_locations,
            'pattern_sparsity': np.mean(np.abs(input_vector) > 0)
        })
        
        return len(activated_locations)
    
    def read(self, query_vector):
        """
        Recall from ternary memory
        
        Args:
            query_vector: ternary numpy array {-1, 0, +1}
        Returns:
            output_vector: ternary numpy array {-1, 0, +1}
            confidence: retrieval confidence
        """
        activated_idxs = []
        distances = []
        
        for i, addr in enumerate(self.addresses):
            dist = self._ternary_distance(query_vector, addr)
            if dist <= self.access_radius:
                activated_idxs.append(i)
                distances.append(dist)
        
        if not activated_idxs:
            return np.zeros(self.vector_dim, dtype=int), 0.0
        
        # Weighted sum
        weights = np.array([1.0 / (1.0 + d) for d in distances])
        weights = weights / np.sum(weights)
        
        total = np.zeros(self.vector_dim)
        for idx, weight in zip(activated_idxs, weights):
            total += weight * self.memory[idx]
        
        # Ternary threshold: -1 if negative, +1 if positive, 0 if near zero
        output_vector = np.zeros(self.vector_dim, dtype=int)
        threshold = np.max(np.abs(total)) * 0.1  # 10% threshold
        output_vector[total > threshold] = 1
        output_vector[total < -threshold] = -1
        
        confidence = np.max(np.abs(total)) if len(total) > 0 else 0.0
        
        self.read_stats.append({
            'activated_locations': len(activated_idxs),
            'activation_rate': len(activated_idxs) / self.num_locations,
            'confidence': confidence,
            'avg_distance': np.mean(distances) if distances else float('inf')
        })
        
        return output_vector, confidence
    
    def get_memory_statistics(self):
        """Get memory statistics"""
        return {
            'memory_utilization': np.mean(self.access_counts > 0),
            'avg_access_count': np.mean(self.access_counts),
            'max_access_count': np.max(self.access_counts),
            'memory_magnitude': np.mean(np.abs(self.memory)),
            'write_stats': self.write_stats,
            'read_stats': self.read_stats
        }

def generate_ternary_vector(dim: int, sparsity: float = 0.05) -> np.ndarray:
    """Generate sparse ternary vector"""
    vector = np.zeros(dim, dtype=int)
    num_nonzero = int(dim * sparsity)
    
    if num_nonzero > 0:
        indices = np.random.choice(dim, num_nonzero, replace=False)
        values = np.random.choice([-1, 1], size=num_nonzero)
        vector[indices] = values
    
    return vector