from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def store_vector(vector: list[int]):
    # Placeholder: replace with actual store logic
    return {"status": "stored", "vector_length": len(vector)}