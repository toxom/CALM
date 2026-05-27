# backend/api/config/routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from backend.api.config.models import SystemConfig
from backend.api.config.validation import validate_embedding_contract

import numpy as np

from .models import (
    SystemMode, MemoryParameters, SystemConfig,
    ConfigResponse, PerformanceMetrics, QuickConfig
)

router = APIRouter()

# Global configuration state
_current_config = SystemConfig()

# Preset configurations
PRESETS = {
    "small": MemoryParameters(
        num_locations=500,
        access_radius=15,
        target_sparsity=0.03
    ),
    "medium": MemoryParameters(
        num_locations=1000,
        access_radius=25,
        target_sparsity=0.03
    ),
    "large": MemoryParameters(
        num_locations=5000,
        access_radius=100,
        target_sparsity=0.03
    ),
    "swarm": MemoryParameters(
        num_locations=500,
        access_radius=50,
        target_sparsity=0.05
    ),
    "llm": MemoryParameters(
        num_locations=10000,
        access_radius=200,
        target_sparsity=0.02
    )
}

@router.get("/current", response_model=SystemConfig)
async def get_current_config():
    """Get current system configuration"""
    return _current_config

@router.post("/mode", response_model=ConfigResponse)
async def set_memory_mode(mode: SystemMode):
    """Switch between binary and ternary memory modes"""
    global _current_config
    
    old_mode = _current_config.mode
    _current_config.mode = mode.mode
    
    return ConfigResponse(
        success=True,
        message=f"Memory mode switched from {old_mode} to {mode.mode}",
        config=_current_config
    )

@router.post("/parameters", response_model=ConfigResponse)
async def update_memory_parameters(params: MemoryParameters):
    """Update memory hyperparameters"""
    global _current_config
    
    # Validate access_radius < vector_dim
    if params.access_radius >= params.vector_dim:
        raise HTTPException(
            status_code=400,
            detail=f"access_radius ({params.access_radius}) must be less than vector_dim ({params.vector_dim})"
        )
    
    _current_config.memory_params = params
    
    return ConfigResponse(
        success=True,
        message="Memory parameters updated successfully",
        config=_current_config
    )

@router.post("/full", response_model=ConfigResponse)
async def update_full_config(config: SystemConfig):
    """Update complete system configuration"""
    global _current_config
    
    validate_embedding_contract(config)  
    
    _current_config = config
    
    return ConfigResponse(
        success=True,
        message="System configuration updated successfully",
        config=_current_config
    )

@router.post("/preset", response_model=ConfigResponse)
async def apply_preset(quick_config: QuickConfig):
    """Apply a preset configuration"""
    global _current_config
    
    if quick_config.preset not in PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown preset: {quick_config.preset}. Available: {list(PRESETS.keys())}"
        )
    
    preset_params = PRESETS[quick_config.preset]
    _current_config.memory_params = preset_params
    
    if quick_config.mode:
        _current_config.mode = quick_config.mode
    
    return ConfigResponse(
        success=True,
        message=f"Applied '{quick_config.preset}' preset configuration",
        config=_current_config
    )

@router.get("/presets")
async def list_presets():
    """List all available preset configurations"""
    return {
        "presets": {
            name: {
                "vector_dim": params.vector_dim,
                "num_locations": params.num_locations,
                "access_radius": params.access_radius,
                "target_sparsity": params.target_sparsity,
                "description": _get_preset_description(name)
            }
            for name, params in PRESETS.items()
        }
    }

@router.get("/compare", response_model=PerformanceMetrics)
async def compare_modes():
    """Compare binary vs ternary performance characteristics"""
    
    binary_perf = {
        "storage_bits_per_value": 1.0,
        "expressiveness": 2.0,  # 2 states: 0, 1
        "negation_support": 0.0,  # No native negation
        "sparsity_efficiency": 1.0,  # Baseline
        "recommended_sparsity": 0.03
    }
    
    ternary_perf = {
        "storage_bits_per_value": 2.0,  # Need 2 bits to encode 3 states
        "expressiveness": 3.0,  # 3 states: -1, 0, +1
        "negation_support": 1.0,  # Native negation via sign
        "sparsity_efficiency": 1.5,  # More efficient for sparse patterns
        "recommended_sparsity": 0.05
    }
    
    recommendation = """
    Binary Mode:
    - Use for: Simple pattern matching, boolean logic
    - Pros: Memory efficient, faster computation
    - Cons: Cannot represent negation or neutral states
    
    Ternary Mode:
    - Use for: Semantic relationships, LLM integration, opposites
    - Pros: More expressive, native negation, better for language
    - Cons: 2x memory usage, slightly slower
    
    Recommendation for LLM + SDM:
    - Use TERNARY mode for richer semantic representation
    - Binary mode sufficient for simple pattern recognition tasks
    """
    
    return PerformanceMetrics(
        binary_performance=binary_perf,
        ternary_performance=ternary_perf,
        recommendation=recommendation.strip()
    )

@router.post("/optimize")
async def auto_optimize_config():
    """Auto-optimize configuration based on current system state"""
    global _current_config
    
    # Simple heuristic: adjust access_radius based on vector_dim
    optimal_radius = int(_current_config.memory_params.vector_dim * 0.2)
    
    old_radius = _current_config.memory_params.access_radius
    _current_config.memory_params.access_radius = optimal_radius
    
    return ConfigResponse(
        success=True,
        message=f"Auto-optimized: access_radius {old_radius} → {optimal_radius}",
        config=_current_config
    )

@router.post("/reset")
async def reset_to_defaults():
    """Reset configuration to default values"""
    global _current_config
    _current_config = SystemConfig()
    
    return ConfigResponse(
        success=True,
        message="Configuration reset to defaults",
        config=_current_config
    )

def _get_preset_description(preset_name: str) -> str:
    """Get description for preset"""
    descriptions = {
        "small": "Fast testing and prototyping (64-dim)",
        "medium": "Balanced performance (128-dim, default)",
        "large": "High capacity system (512-dim)",
        "swarm": "Multi-agent coordination (256-dim)",
        "llm": "LLM integration optimized (1024-dim)"
    }
    return descriptions.get(preset_name, "")
