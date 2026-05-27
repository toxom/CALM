# backend/api/llm/routes.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from backend.core.config_state import get_config
import numpy as np
import hashlib
import time
import aiohttp
import os
import traceback
import logging

from .models import (
    LLMRequest, PatternStore, PatternRecall, HybridResponse
)
from backend.core.sdm.memory import SparseDistributedMemory, generate_sparse_vector
from backend.core.sdm.ternary_memory import TernarySparseDistributedMemory, generate_ternary_vector

config = get_config()
logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = config.llm_model if hasattr(config, "llm_model") else "qwen2.5:7b"

router = APIRouter()

# In-memory pattern storage with metadata
_pattern_storage: Dict[str, Dict] = {}
_memory_instances: Dict[str, object] = {}

async def get_embedding(text: str) -> np.ndarray:
    """
    Get semantic embedding from Ollama
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text
            }
        ) as response:
            if response.status != 200:
                raise Exception(f"Embedding API error: {response.status}")
            data = await response.json()
            embedding = np.array(
                data["embedding"],
                dtype=np.float32
            )
            return embedding

async def text_to_vector(
    text: str,
    mode: str = "ternary",
    sparsity: float = 0.05
) -> np.ndarray:

    embedding = await get_embedding(text)
    embedding = np.array(embedding, dtype=np.float32)

    # normalize
    norm = np.linalg.norm(embedding)

    if norm == 0:
        return np.zeros_like(embedding, dtype=np.int8)

    embedding = embedding / norm
    sparse = np.zeros_like(embedding, dtype=np.int8)
    mean = np.mean(embedding)
    std = np.std(embedding)
    pos_threshold = mean + 0.5 * std
    neg_threshold = mean - 0.5 * std

    if mode == "binary":
        sparse[embedding >= pos_threshold] = 1
    else:  # ternary
        sparse[embedding >= pos_threshold] = 1
        sparse[embedding <= neg_threshold] = -1
    logger.info(
        "VECTOR mode=%s nonzero=%d pos=%d neg=%d",
        mode,
        int(np.count_nonzero(sparse)),
        int(np.sum(sparse == 1)),
        int(np.sum(sparse == -1))
    )
    return sparse


def get_memory(mode: str):
    config = get_config()

    vector_dim = config.embedding.dimension
    params = config.memory_params

    key = f"{mode}_{vector_dim}_{params.num_locations}"

    if key not in _memory_instances:
        access_radius = int(vector_dim * 0.25)
        if mode == "binary":
            _memory_instances[key] = SparseDistributedMemory(
                vector_dim=vector_dim,
                num_locations=params.num_locations,
                access_radius=access_radius
            )
        else:
            _memory_instances[key] = TernarySparseDistributedMemory(
                vector_dim=vector_dim,
                num_locations=params.num_locations,
                access_radius=access_radius
            )

    return _memory_instances[key]


async def _call_ollama(
    query: str, 
    sdm_context: Optional[Dict],
    model: str = DEFAULT_MODEL
) -> str:
    """Call Ollama API for LLM response"""
    try:
        # Build prompt with SDM context if available
        if sdm_context and sdm_context.get("patterns"):
            context_text = "\n".join([f"- {p['text']}" for p in sdm_context["patterns"]])
            prompt = f"""You have access to these relevant memories:
{context_text}

User query: {query}

Provide a helpful answer using the above context when relevant."""
        else:
            prompt = query
        
        # Call Ollama API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "No response from LLM")
                else:
                    return f"Error calling Ollama: {response.status}"
    
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


@router.post("/store", response_model=Dict)
async def store_pattern(request: PatternStore):
    """Store text as an SDM pattern (System 1 memory)"""
    try:
        # STEP 1: compute embeddings ONCE per mode
        binary_vec = await text_to_vector(request.text, mode="binary")
        ternary_vec = await text_to_vector(request.text, mode="ternary")

        # STEP 2: store in SDM
        results = []

        memory_b = get_memory("binary")
        activated_b = memory_b.write(binary_vec, strength=5)
        results.append(("binary", activated_b))

        memory_t = get_memory("ternary")
        activated_t = memory_t.write(ternary_vec, strength=5)
        results.append(("ternary", activated_t))

        # STEP 3: metadata store (reuse already computed vectors)
        pattern_id = hashlib.sha256(request.text.encode()).hexdigest()[:16]

        _pattern_storage[pattern_id] = {
            "text": request.text,
            "vectors": {
                "binary": binary_vec.tolist(),
                "ternary": ternary_vec.tolist()
            },
            "metadata": request.metadata or {},
            "timestamp": time.time()
        }

        return {
            "success": True,
            "pattern_id": pattern_id,
            "activated_locations": sum(r[1] for r in results),
            "message": "Pattern stored in both binary and ternary modes"
        }

    except Exception as e:
        logger.error("LLM STORE FAILED: %s", str(e))
        logger.error(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=f"Store failed: {str(e)}"
        )
    
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Cosine similarity for sparse semantic vectors
    """
    
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    
    if denom == 0:
        return 0.0
    
    return float(np.dot(a, b) / denom)

async def text_to_binary_vector(text: str, sparsity=0.05):
    emb = await get_embedding(text)
    emb = emb / (np.linalg.norm(emb) + 1e-9)
    v = np.zeros_like(emb, dtype=np.int8)
    thr = np.percentile(emb, 100 - sparsity * 100)
    v[emb >= thr] = 1
    return v

async def text_to_ternary_vector(text: str, sparsity=0.05):
    emb = await get_embedding(text)
    emb = emb / (np.linalg.norm(emb) + 1e-9)

    v = np.zeros_like(emb, dtype=np.int8)
    pos = np.percentile(emb, 100 - sparsity * 50)
    neg = np.percentile(emb, sparsity * 50)

    v[emb >= pos] = 1
    v[emb <= neg] = -1
    return v

@router.post("/recall", response_model=Dict)

async def recall_patterns(request: PatternRecall):
    try:
        if request.mode == "binary":
            query_vector = await text_to_binary_vector(request.query)
        else:
            query_vector = await text_to_ternary_vector(request.query)
        memory = get_memory(request.mode)
        start_time = time.time()
        recalled_vector, confidence = memory.read(query_vector)
        recall_time = (time.time() - start_time) * 1000

        similar_patterns = []

        for pattern_id, pattern_data in _pattern_storage.items():
            stored_vec = np.array(pattern_data["vectors"][request.mode])

            similarity = cosine_similarity(stored_vec, recalled_vector)

            if similarity > 0.2:
                similar_patterns.append({
                    "pattern_id": pattern_id,
                    "text": pattern_data["text"],
                    "similarity": similarity,
                    "metadata": pattern_data["metadata"]
                })

        similar_patterns.sort(key=lambda x: x["similarity"], reverse=True)
        similar_patterns = similar_patterns[:request.top_k]

        return {
            "query": request.query,
            "recalled_patterns": similar_patterns,
            "confidence": float(confidence),
            "recall_time_ms": recall_time,
            "mode": request.mode
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/hybrid", response_model=HybridResponse)
async def hybrid_query(request: LLMRequest):
    """
    Hybrid System 1 + System 2 processing
    - System 1 (SDM): Fast associative recall
    - System 2 (Ollama LLM): Reasoning and generation
    """
    start_time = time.time()
    system1_result = None
    system2_result = None
    
    # SYSTEM 1: Fast SDM recall
    if request.use_sdm:
        try:
            query_vector = await text_to_vector(request.query, mode=request.mode)            
            memory = get_memory(request.mode)
            recalled_vector, confidence = memory.read(query_vector)
            
            relevant_patterns = []
            for pattern_id, pattern_data in _pattern_storage.items():
                stored_vec = np.array(pattern_data["vectors"][request.mode], dtype=np.int8)
                recalled_vec = recalled_vector.astype(np.int8)
                similarity = float(np.dot(stored_vec, recalled_vec) /
                                (np.linalg.norm(stored_vec) * np.linalg.norm(recalled_vec) + 1e-9))
                if confidence > 0.1:                    
                    relevant_patterns.append({
                        "text": pattern_data["text"],
                        "similarity": similarity
                    })
            relevant_patterns.sort(key=lambda x: x["similarity"], reverse=True)
            
            system1_result = {
                "confidence": float(confidence),
                "patterns": relevant_patterns[:3],
                "mode": request.mode
            }
        except Exception as e:
            system1_result = {"error": str(e)}
    
    # SYSTEM 2: LLM reasoning (only if requested)
    if request.use_llm:
        system2_result = await _call_ollama(request.query, system1_result)
        combined_answer = system2_result
    else:
        # System 1 only
        if system1_result and system1_result.get("patterns"):
            combined_answer = system1_result["patterns"][0]["text"]
        else:
            combined_answer = "No relevant patterns found in SDM."
    
    used_sdm = bool(system1_result and system1_result.get("patterns"))
    used_llm = request.use_llm
    
    processing_time = (time.time() - start_time) * 1000
    
    return HybridResponse(
        system1_result=system1_result,
        system2_result=system2_result if used_llm else None,
        combined_answer=combined_answer,
        processing_time_ms=processing_time,
        used_sdm=used_sdm,
        used_llm=used_llm
    )




@router.get("/patterns")
async def list_stored_patterns():
    """List all stored patterns"""
    return {
        "total_patterns": len(_pattern_storage),
        "patterns": [
            {
                "pattern_id": pid,
                "text": data["text"],
                "metadata": data.get("metadata", {})
            }
            for pid, data in _pattern_storage.items()
        ]
    }
@router.delete("/clear")
async def clear_all_patterns():
    """Clear all stored patterns"""
    global _pattern_storage, _memory_instances
    _pattern_storage.clear()
    _memory_instances.clear()
    
    return {"success": True, "message": "All patterns and memory cleared"}

@router.get("/models")
async def list_models():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{OLLAMA_BASE_URL}/api/tags") as resp:
            data = await resp.json()
    return {
        "models": [
            {
                "name": m["name"],
                "size": m.get("size"),
                "modified": m.get("modified_at")
            }
            for m in data.get("models", [])
        ]
    }