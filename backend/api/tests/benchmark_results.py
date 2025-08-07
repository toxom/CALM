from pathlib import Path
import csv
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/results")
async def get_benchmark_results():
    # Path relative to this file
    csv_output_path = Path(__file__).parent / "sdm_benchmark_results.csv"

    if not csv_output_path.exists():
        raise HTTPException(status_code=404, detail="Benchmark results not found")

    with open(csv_output_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    return {"results": rows}