# backend/api/memory/routes.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

from .models import (
    PatternInput, PatternQuery, PatternResponse,
    MemoryConfig, MemoryStats, MemoryResponse
)
from backend.core.sdm.memory import SparseDistributedMemory, generate_sparse_vector
from backend.core.sdm.ternary_memory import TernarySparseDistributedMemory, generate_ternary_vector

router = APIRouter()

# Global memory instances (in production, use dependency injection or state management)
_memory_instances: Dict[str, object] = {}

def get_or_create_memory(config: MemoryConfig):
    """Get existing memory or create new one"""
    key = f"{config.mode}_{config.vector_dim}_{config.num_locations}_{config.access_radius}"
    
    if key not in _memory_instances:
        if config.mode == "binary":
            _memory_instances[key] = SparseDistributedMemory(
                vector_dim=config.vector_dim,
                num_locations=config.num_locations,
                access_radius=config.access_radius
            )
        else:  # ternary
            _memory_instances[key] = TernarySparseDistributedMemory(
                vector_dim=config.vector_dim,
                num_locations=config.num_locations,
                access_radius=config.access_radius
            )
    
    return _memory_instances[key]

@router.post("/init", response_model=MemoryResponse)
async def initialize_memory(config: MemoryConfig):
    """Initialize a new memory instance with given configuration"""
    try:
        memory = get_or_create_memory(config)
        
        return MemoryResponse(
            success=True,
            message=f"Memory initialized in {config.mode} mode",
            data={
                "vector_dim": config.vector_dim,
                "num_locations": config.num_locations,
                "access_radius": config.access_radius,
                "mode": config.mode
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/store", response_model=MemoryResponse)
async def store_pattern(pattern: PatternInput, config: MemoryConfig = Depends()):
    """Store a pattern in memory"""
    try:
        memory = get_or_create_memory(config)
        
        # Validate vector dimensions
        if len(pattern.vector) != config.vector_dim:
            raise HTTPException(
                status_code=400,
                detail=f"Vector dimension mismatch. Expected {config.vector_dim}, got {len(pattern.vector)}"
            )
        
        # Validate vector values based on mode
        if pattern.mode == "binary":
            if not all(v in [0, 1] for v in pattern.vector):
                raise HTTPException(status_code=400, detail="Binary mode requires values in {0, 1}")
        else:  # ternary
            if not all(v in [-1, 0, 1] for v in pattern.vector):
                raise HTTPException(status_code=400, detail="Ternary mode requires values in {-1, 0, 1}")
        
        # Store pattern
        vector = np.array(pattern.vector)
        activated = memory.write(vector, strength=pattern.strength)
        logger.info(
            "STORE | mode=%s dim=%d activated=%d",
            pattern.mode,
            config.vector_dim,
            activated
        )
        return MemoryResponse(
            success=True,
            message="Pattern stored successfully",
            data={
                "activated_locations": activated,
                "activation_rate": activated / config.num_locations,
                "pattern_sparsity": float(np.mean(np.abs(vector) > 0))
            }
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception(
            "STORE FAILED | mode=%s dim=%s vector_len=%s",
            getattr(pattern, "mode", None),
            getattr(config, "vector_dim", None),
            len(pattern.vector) if hasattr(pattern, "vector") else None
        )
        raise HTTPException(status_code=500, detail="Store failed")

@router.post("/recall", response_model=PatternResponse)
async def recall_pattern(query: PatternQuery, pattern: PatternInput, config: MemoryConfig = Depends()):
    """Recall a pattern from memory"""
    try:
        memory = get_or_create_memory(config)
        
        # Validate vector
        if len(query.vector) != config.vector_dim:
            raise HTTPException(
                status_code=400,
                detail=f"Vector dimension mismatch. Expected {config.vector_dim}, got {len(query.vector)}"
            )
        
        # Recall pattern
        query_vec = np.array(query.vector)
        recalled_vec, confidence = memory.read(query_vec)
        
        # Calculate match ratio
        match_ratio = float(np.mean(query_vec == recalled_vec))
        
        # Get last read stats
        stats = memory.read_stats[-1] if memory.read_stats else {}
        
        return PatternResponse(
            recalled_vector=recalled_vec.tolist(),
            confidence=float(confidence),
            match_ratio=match_ratio,
            activated_locations=stats.get('activated_locations', 0),
            mode=config.mode
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.info(
            "RECALL | mode=%s activated=%d confidence=%.3f",
            config.mode,
            stats.get("activated_locations", 0),
            confidence
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=MemoryStats)
async def get_memory_stats(pattern: PatternInput, config: MemoryConfig = Depends()):
    """Get current memory statistics"""
    try:
        memory = get_or_create_memory(config)
        stats = memory.get_memory_statistics()
        
        return MemoryStats(
            memory_utilization=float(stats['memory_utilization']),
            avg_access_count=float(stats['avg_access_count']),
            max_access_count=int(stats['max_access_count']),
            total_patterns_stored=len(stats['write_stats']),
            mode=config.mode,
            vector_dim=config.vector_dim,
            num_locations=config.num_locations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=MemoryResponse)
async def generate_random_pattern(pattern: PatternInput, config: MemoryConfig = Depends()):
    """Generate a random sparse pattern for testing"""
    try:
        if config.mode == "binary":
            vector = generate_sparse_vector(config.vector_dim, config.target_sparsity)
        else:  # ternary
            vector = generate_ternary_vector(config.vector_dim, config.target_sparsity)
        
        return MemoryResponse(
            success=True,
            message=f"Generated random {config.mode} pattern",
            data={
                "vector": vector.tolist(),
                "sparsity": float(np.mean(np.abs(vector) > 0)),
                "mode": config.mode
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_memory(pattern: PatternInput, config: MemoryConfig = Depends()):
    """Clear memory instance"""
    try:
        key = f"{config.mode}_{config.vector_dim}_{config.num_locations}_{config.access_radius}"
        if key in _memory_instances:
            del _memory_instances[key]
            return MemoryResponse(
                success=True,
                message="Memory cleared successfully"
            )
        else:
            return MemoryResponse(
                success=True,
                message="No memory instance found to clear"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
