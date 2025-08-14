# backend/core/sdm/optimization/radius_optimizer.py

import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class OptimizationStrategy(Enum):
    """Different optimization strategies for radius selection"""
    BRUTE_FORCE = "brute_force"
    GENETIC_ALGORITHM = "genetic_algorithm" 
    GRADIENT_DESCENT = "gradient_descent"
    SIMULATED_ANNEALING = "simulated_annealing"
    SWARM_CONSENSUS = "swarm_consensus"
    HIERARCHICAL_SEARCH = "hierarchical_search"

class PerformanceMetric(Enum):
    """Performance metrics for optimization"""
    MATCH_RATIO = "match_ratio"
    ACTIVATION_RATE = "activation_rate"
    INTERFERENCE_LEVEL = "interference_level"
    RETRIEVAL_ACCURACY = "retrieval_accuracy"
    COMPUTATIONAL_EFFICIENCY = "computational_efficiency"

class RadiusOptimizer:
    """Optimize access radius across single or multiple SDM agents"""
    
    def __init__(self, strategy: OptimizationStrategy = OptimizationStrategy.GENETIC_ALGORITHM):
        self.strategy = strategy
        self.optimization_history = []
        self.best_parameters = {}
        
    def optimize_single_agent(self, sdm_agent, patterns: List[np.ndarray], 
                            metric: PerformanceMetric = PerformanceMetric.MATCH_RATIO,
                            radius_range: Tuple[int, int] = None) -> Dict:
        """
        Optimize radius for a single SDM agent
        
        Args:
            sdm_agent: SDM agent to optimize
            patterns: List of test patterns
            metric: Performance metric to optimize
            radius_range: (min_radius, max_radius) search range
            
        Returns:
            Dictionary with optimization results
        """
        if radius_range is None:
            radius_range = (1, sdm_agent.vector_dim // 2)
        
        print(f"Optimizing single agent radius using {self.strategy.value}")
        print(f"Search range: {radius_range[0]} to {radius_range[1]}")
        
        if self.strategy == OptimizationStrategy.BRUTE_FORCE:
            return self._brute_force_optimization(sdm_agent, patterns, metric, radius_range)
        elif self.strategy == OptimizationStrategy.GENETIC_ALGORITHM:
            return self._genetic_algorithm_optimization(sdm_agent, patterns, metric, radius_range)
        elif self.strategy == OptimizationStrategy.GRADIENT_DESCENT:
            return self._gradient_descent_optimization(sdm_agent, patterns, metric, radius_range)
        else:
            # Default to genetic algorithm
            return self._genetic_algorithm_optimization(sdm_agent, patterns, metric, radius_range)
    
    def _brute_force_optimization(self, sdm_agent, patterns: List[np.ndarray], 
                                metric: PerformanceMetric, radius_range: Tuple[int, int]) -> Dict:
        """Brute force search over all possible radius values"""
        
        best_radius = radius_range[0]
        best_score = 0.0
        results = []
        
        for radius in range(radius_range[0], radius_range[1] + 1):
            score = self._evaluate_radius(sdm_agent, patterns, radius, metric)
            results.append((radius, score))
            
            if score > best_score:
                best_score = score
                best_radius = radius
                
            print(f"  Radius {radius}: score = {score:.4f}")
        
        return {
            'optimal_radius': best_radius,
            'best_score': best_score,
            'all_results': results,
            'strategy': self.strategy.value,
            'metric': metric.value
        }
    
    def _genetic_algorithm_optimization(self, sdm_agent, patterns: List[np.ndarray],
                                      metric: PerformanceMetric, radius_range: Tuple[int, int],
                                      population_size: int = 20, generations: int = 10) -> Dict:
        """Genetic algorithm optimization"""
        
        min_radius, max_radius = radius_range
        
        # Initialize population
        population = np.random.randint(min_radius, max_radius + 1, population_size)
        fitness_history = []
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for radius in population:
                score = self._evaluate_radius(sdm_agent, patterns, radius, metric)
                fitness_scores.append(score)
            
            fitness_scores = np.array(fitness_scores)
            fitness_history.append(np.max(fitness_scores))
            
            # Selection (tournament selection)
            new_population = []
            for _ in range(population_size):
                # Tournament selection
                tournament_size = 3
                tournament_indices = np.random.choice(population_size, tournament_size, replace=False)
                tournament_fitness = fitness_scores[tournament_indices]
                winner_idx = tournament_indices[np.argmax(tournament_fitness)]
                new_population.append(population[winner_idx])
            
            population = np.array(new_population)
            
            # Mutation
            mutation_rate = 0.1
            for i in range(population_size):
                if np.random.random() < mutation_rate:
                    # Random mutation within range
                    population[i] = np.random.randint(min_radius, max_radius + 1)
            
            print(f"  Generation {generation + 1}: best fitness = {fitness_history[-1]:.4f}")
        
        # Return best solution
        final_fitness = [self._evaluate_radius(sdm_agent, patterns, r, metric) for r in population]
        best_idx = np.argmax(final_fitness)
        
        return {
            'optimal_radius': population[best_idx],
            'best_score': final_fitness[best_idx],
            'fitness_history': fitness_history,
            'final_population': population.tolist(),
            'strategy': self.strategy.value,
            'metric': metric.value
        }
    
    def _gradient_descent_optimization(self, sdm_agent, patterns: List[np.ndarray],
                                     metric: PerformanceMetric, radius_range: Tuple[int, int],
                                     learning_rate: float = 1.0, max_iterations: int = 50) -> Dict:
        """Gradient descent optimization (adapted for discrete radius values)"""
        
        min_radius, max_radius = radius_range
        current_radius = (min_radius + max_radius) // 2  # Start in middle
        
        score_history = []
        radius_history = []
        
        for iteration in range(max_iterations):
            current_score = self._evaluate_radius(sdm_agent, patterns, current_radius, metric)
            score_history.append(current_score)
            radius_history.append(current_radius)
            
            # Calculate approximate gradient using finite differences
            gradient = 0
            if current_radius > min_radius:
                left_score = self._evaluate_radius(sdm_agent, patterns, current_radius - 1, metric)
                gradient += (current_score - left_score)
            
            if current_radius < max_radius:
                right_score = self._evaluate_radius(sdm_agent, patterns, current_radius + 1, metric)
                gradient += (right_score - current_score)
            
            # Update radius based on gradient
            if gradient > 0.01:  # Threshold to avoid noise
                new_radius = min(max_radius, current_radius + int(learning_rate))
            elif gradient < -0.01:
                new_radius = max(min_radius, current_radius - int(learning_rate))
            else:
                break  # Converged
            
            current_radius = new_radius
            print(f"  Iteration {iteration + 1}: radius = {current_radius}, score = {current_score:.4f}")
        
        final_score = self._evaluate_radius(sdm_agent, patterns, current_radius, metric)
        
        return {
            'optimal_radius': current_radius,
            'best_score': final_score,
            'score_history': score_history,
            'radius_history': radius_history,
            'strategy': self.strategy.value,
            'metric': metric.value
        }
    
    def _evaluate_radius(self, sdm_agent, patterns: List[np.ndarray], 
                        radius: int, metric: PerformanceMetric) -> float:
        """Evaluate performance for a given radius"""
        
        # Temporarily set the radius
        original_radius = sdm_agent.access_radius
        sdm_agent.access_radius = radius
        
        try:
            if metric == PerformanceMetric.MATCH_RATIO:
                return self._calculate_match_ratio(sdm_agent, patterns)
            elif metric == PerformanceMetric.ACTIVATION_RATE:
                return self._calculate_activation_rate(sdm_agent, patterns)
            elif metric == PerformanceMetric.INTERFERENCE_LEVEL:
                return 1.0 - self._calculate_interference_level(sdm_agent, patterns)
            elif metric == PerformanceMetric.RETRIEVAL_ACCURACY:
                return self._calculate_retrieval_accuracy(sdm_agent, patterns)
            else:
                return self._calculate_match_ratio(sdm_agent, patterns)
        finally:
            # Restore original radius
            sdm_agent.access_radius = original_radius
    
    def _calculate_match_ratio(self, sdm_agent, patterns: List[np.ndarray]) -> float:
        """Calculate average match ratio for patterns"""
        match_ratios = []
        
        for pattern in patterns:
            # Write pattern
            sdm_agent.write(pattern, strength=1)
            
            # Read back
            retrieved_pattern, confidence = sdm_agent.read(pattern)
            
            # Calculate match ratio
            match_ratio = np.mean(pattern == retrieved_pattern)
            match_ratios.append(match_ratio)
        
        return np.mean(match_ratios)
    
    def _calculate_activation_rate(self, sdm_agent, patterns: List[np.ndarray]) -> float:
        """Calculate average activation rate"""
        activation_rates = []
        
        for pattern in patterns:
            activated_locations = 0
            for i, addr in enumerate(sdm_agent.addresses):
                dist = np.sum(pattern != addr)
                if dist <= sdm_agent.access_radius:
                    activated_locations += 1
            
            activation_rate = activated_locations / sdm_agent.num_locations
            activation_rates.append(activation_rate)
        
        return np.mean(activation_rates)
    
    def _calculate_interference_level(self, sdm_agent, patterns: List[np.ndarray]) -> float:
        """Calculate interference between patterns"""
        if len(patterns) < 2:
            return 0.0
        
        # Store all patterns
        for pattern in patterns:
            sdm_agent.write(pattern, strength=1)
        
        # Measure retrieval degradation
        total_degradation = 0.0
        for i, pattern in enumerate(patterns):
            retrieved, confidence = sdm_agent.read(pattern)
            match_ratio = np.mean(pattern == retrieved)
            degradation = 1.0 - match_ratio
            total_degradation += degradation
        
        return total_degradation / len(patterns)
    
    def _calculate_retrieval_accuracy(self, sdm_agent, patterns: List[np.ndarray]) -> float:
        """Calculate overall retrieval accuracy including confidence"""
        accuracies = []
        
        for pattern in patterns:
            sdm_agent.write(pattern, strength=1)
            retrieved, confidence = sdm_agent.read(pattern)
            
            match_ratio = np.mean(pattern == retrieved)
            # Weight by confidence
            weighted_accuracy = match_ratio * confidence
            accuracies.append(weighted_accuracy)
        
        return np.mean(accuracies)

class SwarmRadiusOptimizer:
    """Optimize radius across multiple SDM agents in a swarm"""
    
    def __init__(self, optimization_strategy: OptimizationStrategy = OptimizationStrategy.SWARM_CONSENSUS):
        self.strategy = optimization_strategy
        self.consensus_threshold = 0.8
        self.max_iterations = 10
        
    def optimize_radius_across_swarm(self, agents: List, patterns: List[np.ndarray],
                                   metric: PerformanceMetric = PerformanceMetric.MATCH_RATIO) -> Dict:
        """
        Optimize radius across multiple SDM agents
        
        Args:
            agents: List of SDM agents
            patterns: List of test patterns  
            metric: Performance metric to optimize
            
        Returns:
            Dictionary with swarm optimization results
        """
        print(f"Optimizing radius across {len(agents)} agents using {self.strategy.value}")
        
        if self.strategy == OptimizationStrategy.SWARM_CONSENSUS:
            return self._swarm_consensus_optimization(agents, patterns, metric)
        elif self.strategy == OptimizationStrategy.HIERARCHICAL_SEARCH:
            return self._hierarchical_swarm_optimization(agents, patterns, metric)
        else:
            # Fallback to individual optimization + averaging
            return self._individual_then_average_optimization(agents, patterns, metric)
    
    def _swarm_consensus_optimization(self, agents: List, patterns: List[np.ndarray],
                                    metric: PerformanceMetric) -> Dict:
        """Distributed consensus-based optimization"""
        
        # Each agent proposes an optimal radius
        proposed_radii = []
        for agent in agents:
            optimizer = RadiusOptimizer(strategy=OptimizationStrategy.BRUTE_FORCE)
            result = optimizer.optimize_single_agent(
                agent, patterns, metric,
                radius_range=(1, agent.vector_dim // 2)
            )
            proposed_radii.append(result['optimal_radius'])

        # Iteratively move toward consensus
        iteration = 0
        while iteration < self.max_iterations:
            avg_radius = int(np.mean(proposed_radii))
            agreement_ratio = np.mean([
                1 if abs(r - avg_radius) <= 1 else 0
                for r in proposed_radii
            ])

            print(f"  Iteration {iteration + 1}: avg_radius = {avg_radius}, agreement = {agreement_ratio:.2f}")

            if agreement_ratio >= self.consensus_threshold:
                break

            # Agents test new avg_radius and adjust proposal
            new_proposals = []
            for agent in agents:
                best_score = -np.inf
                best_r = avg_radius
                for candidate_r in [avg_radius - 1, avg_radius, avg_radius + 1]:
                    if 1 <= candidate_r <= agent.vector_dim // 2:
                        optimizer = RadiusOptimizer(strategy=OptimizationStrategy.BRUTE_FORCE)
                        score = optimizer._evaluate_radius(agent, patterns, candidate_r, metric)
                        if score > best_score:
                            best_score = score
                            best_r = candidate_r
                new_proposals.append(best_r)
            proposed_radii = new_proposals
            iteration += 1

        final_radius = int(np.mean(proposed_radii))
        return {
            'consensus_radius': final_radius,
            'iterations': iteration + 1,
            'final_proposals': proposed_radii,
            'strategy': self.strategy.value,
            'metric': metric.value
        }

    def _hierarchical_swarm_optimization(self, agents: List, patterns: List[np.ndarray],
                                         metric: PerformanceMetric) -> Dict:
        """Hierarchical optimization: local groups converge, then leaders converge globally"""
        
        # Divide agents into clusters of ~3-5
        group_size = max(3, len(agents) // 3)
        clusters = [agents[i:i + group_size] for i in range(0, len(agents), group_size)]

        cluster_results = []
        for idx, cluster in enumerate(clusters):
            print(f"  Optimizing cluster {idx + 1} with {len(cluster)} agents")
            cluster_optimizer = SwarmRadiusOptimizer(OptimizationStrategy.SWARM_CONSENSUS)
            result = cluster_optimizer._swarm_consensus_optimization(cluster, patterns, metric)
            cluster_results.append(result['consensus_radius'])

        # Leaders are represented by their cluster consensus
        print("  Performing global consensus among cluster leaders...")
        leader_agents = []
        for leader_radius in cluster_results:
            # Create a temporary "leader" agent with fixed vector_dim just for evaluation
            dummy_agent = agents[0].__class__(vector_dim=agents[0].vector_dim,
                                              num_locations=agents[0].num_locations)
            dummy_agent.access_radius = leader_radius
            leader_agents.append(dummy_agent)

        global_optimizer = SwarmRadiusOptimizer(OptimizationStrategy.SWARM_CONSENSUS)
        global_result = global_optimizer._swarm_consensus_optimization(leader_agents, patterns, metric)

        return {
            'hierarchical_radius': global_result['consensus_radius'],
            'cluster_results': cluster_results,
            'strategy': self.strategy.value,
            'metric': metric.value
        }

    def _individual_then_average_optimization(self, agents: List, patterns: List[np.ndarray],
                                              metric: PerformanceMetric) -> Dict:
        """Fallback: optimize individually, then take average radius"""
        individual_radii = []
        for agent in agents:
            optimizer = RadiusOptimizer(strategy=OptimizationStrategy.BRUTE_FORCE)
            result = optimizer.optimize_single_agent(
                agent, patterns, metric,
                radius_range=(1, agent.vector_dim // 2)
            )
            individual_radii.append(result['optimal_radius'])

        avg_radius = int(np.mean(individual_radii))
        return {
            'average_radius': avg_radius,
            'individual_radii': individual_radii,
            'strategy': self.strategy.value,
            'metric': metric.value
        }