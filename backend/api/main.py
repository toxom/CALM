from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .encode.routes import router as encode_router
from .store.routes import router as store_router
from .query.routes import router as query_router
from backend.api.tests.memory_test.routes import router as memory_test_router
from backend.api.tests.benchmark_results import router as benchmark_router
from backend.api.memory import router as memory_router
from backend.api.config import router as config_router
from backend.api.llm import router as llm_router
from dotenv import load_dotenv

import os

load_dotenv() 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

app.include_router(encode_router, prefix="/encode", tags=["encode"])
app.include_router(store_router, prefix="/store", tags=["store"])
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(memory_test_router, prefix="/test/memory", tags=["tests"])
app.include_router(benchmark_router, prefix="/benchmark", tags=["benchmark"])
app.include_router(memory_router, prefix="/memory", tags=["memory"])
app.include_router(config_router, prefix="/config", tags=["config"])
app.include_router(llm_router, prefix="/llm", tags=["llm"])
