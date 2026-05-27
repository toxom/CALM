from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PatternInput(BaseModel):
    """Input pattern for storage"""
    vector: List[int] = Field(..., description="Pattern vector (binary: 0/1 or ternary: -1/0/+1)")
    mode: Literal["binary", "ternary"] = Field(default="binary", description="Memory mode")
    strength: int = Field(default=1, ge=1, le=100, description="Write strength (reinforcement)")

class PatternQuery(BaseModel):
    """Query pattern for retrieval"""
    vector: List[int] = Field(..., description="Query vector")
    mode: Literal["binary", "ternary"] = Field(default="binary", description="Memory mode")

class PatternResponse(BaseModel):
    """Response from pattern recall"""
    recalled_vector: List[int]
    confidence: float
    match_ratio: Optional[float] = None
    activated_locations: int
    mode: str

class MemoryConfig(BaseModel):
    """Memory configuration"""
    vector_dim: int = Field(default=128, ge=8, le=2048, description="Vector dimension")
    num_locations: int = Field(default=1000, ge=100, le=10000, description="Number of memory locations")
    access_radius: int = Field(default=25, ge=1, description="Access radius")
    mode: Literal["binary", "ternary"] = Field(default="binary", description="Memory mode")
    target_sparsity: float = Field(default=0.03, ge=0.01, le=0.5, description="Target sparsity")

class MemoryStats(BaseModel):
    """Memory statistics"""
    memory_utilization: float
    avg_access_count: float
    max_access_count: int
    total_patterns_stored: int
    mode: str
    vector_dim: int
    num_locations: int

class MemoryResponse(BaseModel):
    """Response wrapper"""
    success: bool
    message: str
    data: Optional[dict] = None
