from fastapi import FastAPI

from .encode.routes import router as encode_router
from .store.routes import router as store_router
from .query.routes import router as query_router
from backend.api.tests.memory_test.routes import router as memory_test_router
from backend.api.tests.benchmark_results import router as benchmark_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to CALM API"}

app.include_router(encode_router, prefix="/encode", tags=["encode"])
app.include_router(store_router, prefix="/store", tags=["store"])
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(memory_test_router, prefix="/test/memory", tags=["tests"])
app.include_router(benchmark_router, prefix="/benchmark", tags=["benchmark"])