from fastapi.responses import JSONResponse
import json
import numpy as np
from fastapi import APIRouter, Query, HTTPException
from backend.core.sdm.memory import run_sdm_memory_test

router = APIRouter()

def convert_to_serializable(obj):
    """Convert numpy types to Python native types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    return obj

@router.get("/run")
def test_memory(
    vector_dim: int = Query(32, ge=8, le=1024),
    num_locations: int = Query(3000, ge=100, le=10000),
    access_radius: int = Query(18, ge=1),
    reinforce: int = Query(30, ge=1, le=100)
):
    if access_radius >= vector_dim:
        raise HTTPException(status_code=400, detail="access_radius must be less than vector_dim")
    
    result = run_sdm_memory_test(vector_dim, num_locations, access_radius, reinforce)
    
    # Convert all numpy types to JSON-serializable types
    serializable_result = convert_to_serializable(result)
    
    return JSONResponse(
        content=serializable_result,
        media_type="application/json"
    )