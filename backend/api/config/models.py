# backend/api/config/models.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any

class LLMConfig(BaseModel):
    base_url: str = Field(
        default="http://localhost:11434"
    )
    model: str = Field(
        default="qwen2.5:7b"
    )

class SystemMode(BaseModel):
    """System memory mode configuration"""
    mode: Literal["binary", "ternary"] = Field(default="binary", description="Memory representation mode")
    
class MemoryParameters(BaseModel):
    """Memory hyperparameters"""
    vector_dim: int = Field(default=128, ge=8, le=2048, description="Vector dimension")
    num_locations: int = Field(default=1000, ge=100, le=10000, description="Number of memory locations")
    access_radius: int = Field(default=25, ge=1, description="Hamming/Ternary distance threshold")
    target_sparsity: float = Field(default=0.03, ge=0.01, le=0.5, description="Target pattern sparsity")

class EmbeddingConfig(BaseModel):
    model: str = Field(
        default="nomic-embed-text",
        description="Embedding model used for SDM encoding"
    )
    dimension: int = Field(
        default=768,
        description="Embedding dimension (must match model output)"
    )


class SystemConfig(BaseModel):
    """Complete system configuration"""
    mode: Literal["binary", "ternary"] = Field(default="binary")
    memory_params: MemoryParameters = Field(default_factory=MemoryParameters)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    auto_reinforce: bool = Field(default=True, description="Auto-reinforce patterns on write")
    reinforce_strength: int = Field(default=1, ge=1, le=100, description="Default reinforcement strength")
    
class ConfigResponse(BaseModel):
    """Configuration response"""
    success: bool
    message: str
    config: Optional[SystemConfig] = None

class PerformanceMetrics(BaseModel):
    """Performance comparison between binary and ternary"""
    binary_performance: Optional[Dict[str, float]] = None
    ternary_performance: Optional[Dict[str, float]] = None
    recommendation: Optional[str] = None

class QuickConfig(BaseModel):
    """Preset configurations for common use cases"""
    preset: Literal["small", "medium", "large", "swarm", "llm"] = Field(
        description="Preset configuration profiles"
    )
    mode: Optional[Literal["binary", "ternary"]] = None


