# backend/core/sdm/hierarchy/complexity_analyzer.py

import numpy as np
from typing import Dict, List, Tuple, Any
from enum import Enum

class ComplexityClass(Enum):
    """Polynomial hierarchy complexity classes"""
    P = "P"                    # Polynomial time
    NP = "NP"                  # Nondeterministic polynomial
    SIGMA_2P = "Σ₂P"          # Σ₂ᴾ - ∃∀ quantifier alternation
    PI_2P = "Π₂P"             # Π₂ᴾ - ∀∃ quantifier alternation  
    DELTA_2P = "Δ₂P"          # Δ₂ᴾ - P with NP oracle
    PSPACE = "PSPACE"         # Polynomial space
    UNKNOWN = "UNKNOWN"

class SDMProblemType(Enum):
    """Types of SDM problems"""
    HAMMING_DISTANCE = "hamming_distance"
    PATTERN_RETRIEVAL = "pattern_retrieval"
    OPTIMAL_RADIUS = "optimal_radius"
    CAPACITY_ESTIMATION = "capacity_estimation"
    INTERFERENCE_MINIMIZATION = "interference_minimization"
    SWARM_COORDINATION = "swarm_coordination"
    PATTERN_OPTIMIZATION = "pattern_optimization"
    MEMORY_ALLOCATION = "memory_allocation"

class ComplexityAnalyzer:
    """Analyze computational complexity of SDM problems"""
    
    def __init__(self):
        self.complexity_map = self._initialize_complexity_map()
        self.problem_characteristics = {}
        
    def _initialize_complexity_map(self) -> Dict[SDMProblemType, ComplexityClass]:
        """Initialize known complexity classifications"""
        return {
            SDMProblemType.HAMMING_DISTANCE: ComplexityClass.P,
            SDMProblemType.PATTERN_RETRIEVAL: ComplexityClass.P,
            SDMProblemType.OPTIMAL_RADIUS: ComplexityClass.NP,
            SDMProblemType.CAPACITY_ESTIMATION: ComplexityClass.SIGMA_2P,
            SDMProblemType.INTERFERENCE_MINIMIZATION: ComplexityClass.NP,
            SDMProblemType.SWARM_COORDINATION: ComplexityClass.PI_2P,
            SDMProblemType.PATTERN_OPTIMIZATION: ComplexityClass.DELTA_2P,
            SDMProblemType.MEMORY_ALLOCATION: ComplexityClass.NP
        }
    
    def analyze_problem_complexity(self, problem_type: str, 
                                 problem_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze complexity of a given SDM problem
        
        Args:
            problem_type: Type of SDM problem to analyze
            problem_params: Parameters of the specific problem instance
            
        Returns:
            Dict containing complexity analysis results
        """
        try:
            sdm_problem = SDMProblemType(problem_type)
        except ValueError:
            return self._analyze_unknown_problem(problem_type, problem_params)
        
        base_complexity = self.complexity_map[sdm_problem]
        
        # Problem-specific characteristics
        analysis = {
            'problem_type': problem_type,
            'base_complexity': base_complexity.value,
            'estimated_complexity': base_complexity.value,
            'problem_size': self._calculate_problem_size(problem_params),
            'scalability': self._analyze_scalability(sdm_problem, problem_params),
            'approximation_available': self._check_approximation_algorithms(sdm_problem),
            'recommended_approach': self._recommend_solution_approach(sdm_problem, problem_params)
        }
        
        # Complexity based on specific parameters
        refined_complexity = self._refine_complexity_estimate(sdm_problem, problem_params)
        analysis['estimated_complexity'] = refined_complexity.value
        
        return analysis
    
    def _calculate_problem_size(self, params: Dict[str, Any]) -> int:
        """Calculate the size of the problem instance"""
        size = 1
        
        # Common SDM parameters that affect problem size
        if 'vector_dim' in params:
            size *= params['vector_dim']
        if 'num_locations' in params:
            size *= params['num_locations'] 
        if 'num_patterns' in params:
            size *= params['num_patterns']
        if 'num_agents' in params:
            size *= params['num_agents']
            
        return size
    
    def _analyze_scalability(self, problem_type: SDMProblemType, 
                           params: Dict[str, Any]) -> Dict[str, str]:
        """Analyze how the problem scales with input size"""
        
        scalability = {
            'vector_dimension': 'linear',
            'num_locations': 'linear', 
            'num_patterns': 'linear',
            'overall': 'polynomial'
        }
        
        if problem_type == SDMProblemType.HAMMING_DISTANCE:
            scalability.update({
                'vector_dimension': 'linear',
                'overall': 'linear'
            })
        elif problem_type == SDMProblemType.OPTIMAL_RADIUS:
            scalability.update({
                'vector_dimension': 'exponential',
                'num_patterns': 'exponential',
                'overall': 'exponential'
            })
        elif problem_type == SDMProblemType.SWARM_COORDINATION:
            scalability.update({
                'num_agents': 'polynomial', 
                'coordination_complexity': 'exponential',
                'overall': 'exponential'
            })
        elif problem_type == SDMProblemType.CAPACITY_ESTIMATION:
            scalability.update({
                'vector_dimension': 'exponential',
                'sparsity_level': 'exponential', 
                'overall': 'double_exponential'
            })
            
        return scalability
    
    def _check_approximation_algorithms(self, problem_type: SDMProblemType) -> Dict[str, Any]:
        """Check availability of approximation algorithms"""
        
        approximation_info = {
            'available': False,
            'approximation_ratio': None,
            'algorithm_type': None,
            'time_complexity': None
        }
        
        if problem_type == SDMProblemType.OPTIMAL_RADIUS:
            approximation_info.update({
                'available': True,
                'approximation_ratio': '1.5',
                'algorithm_type': 'greedy_search',
                'time_complexity': 'O(n²)'
            })
        elif problem_type == SDMProblemType.INTERFERENCE_MINIMIZATION:
            approximation_info.update({
                'available': True,
                'approximation_ratio': '2.0',
                'algorithm_type': 'graph_coloring_approximation',
                'time_complexity': 'O(n log n)'
            })
        elif problem_type == SDMProblemType.SWARM_COORDINATION:
            approximation_info.update({
                'available': True,
                'approximation_ratio': 'FPTAS',
                'algorithm_type': 'distributed_consensus',
                'time_complexity': 'O(n³)'
            })
        elif problem_type == SDMProblemType.CAPACITY_ESTIMATION:
            approximation_info.update({
                'available': True,
                'approximation_ratio': '1.1',
                'algorithm_type': 'sampling_based',
                'time_complexity': 'O(n² log n)'
            })
            
        return approximation_info
    
    def _recommend_solution_approach(self, problem_type: SDMProblemType, 
                                   params: Dict[str, Any]) -> Dict[str, str]:
        """Recommend solution approach based on complexity analysis"""
        
        problem_size = self._calculate_problem_size(params)
        base_complexity = self.complexity_map[problem_type]
        
        recommendations = {
            'primary_approach': 'exact_algorithm',
            'fallback_approach': 'approximation',
            'parallelization': 'not_needed',
            'hardware_requirements': 'standard'
        }
        
        # Small problem instances
        if problem_size < 1000:
            if base_complexity in [ComplexityClass.P]:
                recommendations['primary_approach'] = 'exact_algorithm'
            elif base_complexity in [ComplexityClass.NP]:
                recommendations['primary_approach'] = 'exact_algorithm_small'
            else:
                recommendations['primary_approach'] = 'approximation'
                
        # Medium problem instances  
        elif problem_size < 100000:
            if base_complexity == ComplexityClass.P:
                recommendations['primary_approach'] = 'exact_algorithm'
            elif base_complexity == ComplexityClass.NP:
                recommendations['primary_approach'] = 'approximation'
                recommendations['parallelization'] = 'recommended'
            else:
                recommendations['primary_approach'] = 'heuristic'
                recommendations['parallelization'] = 'required'
                
        # Large problem instances
        else:
            if base_complexity == ComplexityClass.P:
                recommendations['primary_approach'] = 'exact_algorithm'
                recommendations['parallelization'] = 'beneficial'
            else:
                recommendations['primary_approach'] = 'heuristic'
                recommendations['parallelization'] = 'required'
                recommendations['hardware_requirements'] = 'high_performance'
        
        # Problem-specific recommendations
        if problem_type == SDMProblemType.SWARM_COORDINATION:
            recommendations['parallelization'] = 'distributed'
            recommendations['primary_approach'] = 'consensus_algorithm'
            
        elif problem_type == SDMProblemType.CAPACITY_ESTIMATION:
            recommendations['primary_approach'] = 'sampling_method'
            recommendations['fallback_approach'] = 'monte_carlo'
            
        return recommendations
    
    def _refine_complexity_estimate(self, problem_type: SDMProblemType, 
                                  params: Dict[str, Any]) -> ComplexityClass:
        """Refine complexity estimate based on specific parameters"""
        
        base_complexity = self.complexity_map[problem_type]
        
        # Special cases that might change complexity
        if 'sparsity' in params:
            sparsity = params['sparsity']
            
            # Very sparse patterns might reduce complexity
            if sparsity < 0.05:
                if base_complexity == ComplexityClass.NP:
                    return ComplexityClass.P  # Some NP problems become P with sparse inputs
                    
            # Very dense patterns might increase complexity  
            elif sparsity > 0.8:
                if base_complexity == ComplexityClass.P:
                    return ComplexityClass.NP  # Some P problems become harder with dense inputs
        
        # Constraints that might simplify the problem
        if 'constraints' in params:
            constraints = params['constraints']
            if 'radius_bounds' in constraints:
                if problem_type == SDMProblemType.OPTIMAL_RADIUS:
                    return ComplexityClass.P  # Bounded search becomes polynomial
        
        # Approximation requirements
        if 'approximation_tolerance' in params:
            tolerance = params['approximation_tolerance']
            if tolerance > 0.1:  # Loose approximation requirements
                if base_complexity in [ComplexityClass.NP, ComplexityClass.SIGMA_2P]:
                    return ComplexityClass.P  # Approximation might be in P
        
        return base_complexity
    
    def _analyze_unknown_problem(self, problem_type: str, 
                                params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze problems not in the standard classification"""
        
        return {
            'problem_type': problem_type,
            'base_complexity': ComplexityClass.UNKNOWN.value,
            'estimated_complexity': ComplexityClass.UNKNOWN.value,
            'problem_size': self._calculate_problem_size(params),
            'scalability': {'overall': 'unknown'},
            'approximation_available': {'available': False},
            'recommended_approach': {
                'primary_approach': 'empirical_analysis',
                'fallback_approach': 'heuristic',
                'parallelization': 'case_by_case'
            },
            'analysis_notes': f'Unknown problem type: {problem_type}. Recommend empirical complexity analysis.'
        }

# Main analysis function for external use
def analyze_problem_complexity(problem_type: str, **kwargs) -> Dict[str, Any]:
    """
    Analyze the computational complexity of an SDM problem
    
    Args:
        problem_type: Type of SDM problem
        **kwargs: Problem parameters
        
    Returns:
        Dictionary containing complexity analysis
        
    Examples:
        >>> analyze_problem_complexity('optimal_radius', vector_dim=512, num_patterns=100)
        >>> analyze_problem_complexity('swarm_coordination', num_agents=10, coordination_depth=3)
    """
    analyzer = ComplexityAnalyzer()
    return analyzer.analyze_problem_complexity(problem_type, kwargs)

def get_complexity_recommendations(problem_type: str, problem_size: int) -> Dict[str, str]:
    """
    Get quick complexity-based recommendations
    
    Args:
        problem_type: Type of SDM problem
        problem_size: Estimated size of problem instance
        
    Returns:
        Dictionary with solution recommendations
    """
    analyzer = ComplexityAnalyzer()
    
    # Basic parameters based on problem size
    if problem_size < 1000:
        params = {'vector_dim': 64, 'num_locations': 100}
    elif problem_size < 10000:
        params = {'vector_dim': 256, 'num_locations': 500}
    else:
        params = {'vector_dim': 1024, 'num_locations': 2000}
    
    analysis = analyzer.analyze_problem_complexity(problem_type, params)
    return analysis['recommended_approach']

# Utility functions for specific SDM operations
def classify_sdm_operation_complexity(operation_name: str, input_size: int) -> str:
    """Quick complexity classification for common SDM operations"""
    
    operation_map = {
        'hamming_distance': 'O(n)',
        'pattern_write': 'O(m·n)', 
        'pattern_read': 'O(m·n)',
        'radius_optimization': 'NP-hard',
        'capacity_analysis': 'Σ₂P-complete',
        'swarm_consensus': 'Π₂P-hard'
    }
    
    return operation_map.get(operation_name, 'Unknown complexity')

def estimate_runtime_complexity(problem_type: str, **params) -> str:
    """Estimate runtime complexity for problem instance"""
    
    analysis = analyze_problem_complexity(problem_type, **params)
    complexity_class = analysis['estimated_complexity']
    problem_size = analysis['problem_size']
    
    if complexity_class == 'P':
        return f"O({problem_size}²) - Polynomial time"
    elif complexity_class == 'NP':
        return f"O(2^{int(np.log2(problem_size))}) - Exponential time"
    elif complexity_class in ['Σ₂P', 'Π₂P']:
        return f"O(2^{problem_size}) - Double exponential time"
    else:
        return f"Unknown - Complexity class: {complexity_class}"

if __name__ == "__main__":
    print("=== SDM Complexity Analysis Examples ===\n")
    
    # Example 1: Optimal radius problem
    result1 = analyze_problem_complexity(
        'optimal_radius', 
        vector_dim=256, 
        num_patterns=100,
        sparsity=0.03
    )
    print("Optimal Radius Analysis:")
    print(f"  Complexity: {result1['estimated_complexity']}")
    print(f"  Recommended approach: {result1['recommended_approach']['primary_approach']}")
    print(f"  Approximation available: {result1['approximation_available']['available']}")
    
    # Example 2: Swarm coordination
    result2 = analyze_problem_complexity(
        'swarm_coordination',
        num_agents=5,
        coordination_depth=2,
        vector_dim=128
    )
    print(f"\nSwarm Coordination Analysis:")
    print(f"  Complexity: {result2['estimated_complexity']}")
    print(f"  Scalability: {result2['scalability']['overall']}")
    print(f"  Parallelization: {result2['recommended_approach']['parallelization']}")
    
    # Example 3: Simple operations
    print(f"\nSimple Operation Complexities:")
    print(f"  Hamming distance: {classify_sdm_operation_complexity('hamming_distance', 256)}")
    print(f"  Pattern retrieval: {classify_sdm_operation_complexity('pattern_read', 1000)}")
    print(f"  Runtime estimate: {estimate_runtime_complexity('pattern_retrieval', vector_dim=256)}")