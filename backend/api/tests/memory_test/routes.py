from fastapi.responses import JSONResponse
import json
from fastapi import APIRouter, Query, HTTPException
from backend.core.sdm.memory import run_sdm_memory_test

router = APIRouter()

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
    # Return compact JSON response
    return JSONResponse(
        content=result,
        media_type="application/json",
        dumps=lambda obj, *, default=None: json.dumps(obj, separators=(',', ':'))
    )