from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class LLMRequest(BaseModel):
    """Request for LLM + SDM hybrid processing"""
    query: str = Field(..., description="User query or prompt")
    use_sdm: bool = Field(default=True, description="Whether to use SDM for retrieval")
    use_llm: bool = Field(default=True, description="Whether to use LLM for reasoning")  # Add this
    sdm_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence threshold for SDM results")
    mode: Literal["binary", "ternary"] = Field(default="binary", description="SDM mode")
    
class SDMContext(BaseModel):
    """SDM retrieval context"""
    patterns: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float
    source: Literal["sdm", "none"] = "sdm"

class LLMResponse(BaseModel):
    """Response from LLM + SDM system"""
    answer: str
    sdm_context: Optional[SDMContext] = None
    processing_mode: Literal["sdm_only", "llm_only", "hybrid"]
    reasoning_steps: Optional[List[str]] = None
    confidence: float

class PatternStore(BaseModel):
    """Store text as SDM pattern"""
    text: str
    metadata: Optional[Dict[str, Any]] = None
    mode: Literal["binary", "ternary"] = Field(default="binary", description="SDM mode")

class PatternRecall(BaseModel):
    """Recall patterns similar to query"""
    query: str
    top_k: int = Field(default=5, ge=1, le=20, description="Number of patterns to recall")
    mode: Literal["binary", "ternary"] = Field(default="ternary")

class HybridResponse(BaseModel):
    """Hybrid System 1 + System 2 response"""
    system1_result: Optional[Dict[str, Any]] = None  # Fast SDM recall
    system2_result: Optional[str] = None  # LLM reasoning
    combined_answer: str
    processing_time_ms: float
    used_sdm: bool
    used_llm: bool
