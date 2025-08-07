import numpy as np

class SparseDistributedMemory:
    def __init__(self, vector_dim=1024, num_locations=1000, access_radius=100):
        """
        Args:
            vector_dim: Dimensionality of binary vectors.
            num_locations: Number of hard memory locations.
            access_radius: Max Hamming distance to activate locations.
        """
        self.vector_dim = vector_dim
        self.num_locations = num_locations
        self.access_radius = access_radius

        # Initialize random fixed hard locations (addresses)
        self.addresses = self._generate_addresses()
        # Memory locations store integer counts per bit (for weighted sums)
        self.memory = np.zeros((num_locations, vector_dim), dtype=int)

    def _generate_addresses(self):
        # Random sparse binary vectors (hard locations)
        # Each bit 0 or 1 with equal probability
        return np.random.randint(2, size=(self.num_locations, self.vector_dim))

    def _hamming_distance(self, v1, v2):
        # Compute Hamming distance between two binary vectors
        return np.sum(v1 != v2)

    def write(self, input_vector):
        """
        Store input_vector into all locations within access_radius
        Args:
            input_vector: binary numpy array (0/1)
        """
        for i, addr in enumerate(self.addresses):
            dist = self._hamming_distance(input_vector, addr)
            if dist <= self.access_radius:
                # Add 2 where input_vector has 1, subtract 1 where 0 (optional)
                self.memory[i] += np.where(input_vector == 1, 2, -1)

    def read(self, query_vector):
        """
        Recall from memory by weighted sum of nearby locations.
        Args:
            query_vector: binary numpy array (0/1)
        Returns:
            output_vector: binary numpy array (0/1)
        """
        activated_idxs = []
        for i, addr in enumerate(self.addresses):
            dist = self._hamming_distance(query_vector, addr)
            if dist <= self.access_radius:
                activated_idxs.append(i)

        if not activated_idxs:
            # No nearby locations found; fallback or empty output
            return np.zeros(self.vector_dim, dtype=int)

        # Sum the memory vectors from activated locations
        total = np.sum(self.memory[activated_idxs], axis=0)
        # Threshold at zero to get binary output
        output_vector = (total > 0).astype(int)
        return output_vector
    
def run_sdm_memory_test(vector_dim=32, num_locations=3000, access_radius=18, reinforce=30):
    sdm = SparseDistributedMemory(vector_dim=vector_dim, num_locations=num_locations, access_radius=access_radius)
    input_vec = np.random.randint(2, size=vector_dim)
    for _ in range(reinforce):
        sdm.write(input_vec)
    output_vec = sdm.read(input_vec)
    match_ratio = float(np.mean(input_vec == output_vec))

    summary = {
        "vector_dim": vector_dim,
        "num_locations": num_locations,
        "access_radius": access_radius,
        "reinforce": reinforce,
        "match_ratio": match_ratio,
        "input_ones_count": int(np.sum(input_vec)),
        "recalled_ones_count": int(np.sum(output_vec)),
        "first_16_bits_input": ''.join(map(str, input_vec[:16])),
        "first_16_bits_recalled": ''.join(map(str, output_vec[:16]))
    }

    return {
        "summary": summary,
        "input_vector": input_vec.tolist(),
        "recalled_vector": output_vec.tolist(),
    }

if __name__ == "__main__":
    sdm = SparseDistributedMemory(vector_dim=32, num_locations=3000, access_radius=18)
    # Create a random input vector
    input_vec = np.random.randint(2, size=32)

    print("Input vector:", input_vec)

    # Write the same vector multiple times to reinforce memory
    for _ in range(30):
        sdm.write(input_vec)

    # Query with same vector (should recall closely)
    output_vec = sdm.read(input_vec)
    print("Recalled vector:", output_vec)

    # Compare input vs output
    print("Match ratio:", np.mean(input_vec == output_vec))

