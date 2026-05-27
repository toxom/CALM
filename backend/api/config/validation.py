# backend/api/config/validation.py

from backend.api.config.models import SystemConfig

def validate_embedding_contract(config: SystemConfig):
    """
    Ensures SDM + embedding + LLM consistency
    This enforces cognitive architecture constraints
    """

    # 1. SDM ↔ embedding dimension contract
    if config.embedding.dimension != config.memory_params.vector_dim:
        raise ValueError(
            f"Embedding dimension ({config.embedding.dimension}) "
            f"must match SDM vector_dim ({config.memory_params.vector_dim})"
        )

    # 2. SDM geometry constraint
    if config.memory_params.access_radius >= config.memory_params.vector_dim:
        raise ValueError(
            "access_radius must be smaller than vector_dim"
        )

    # 3. LLM sanity check (IMPORTANT for reproducibility)
    if not config.llm.model:
        raise ValueError("LLM model must be defined")

    if not config.llm.base_url.startswith("http"):
        raise ValueError("LLM base_url must be a valid URL")

    # 4. Optional but HIGH VALUE: ternary semantic mode constraint
    if config.mode == "ternary":
        if config.embedding.dimension < 128:
            raise ValueError(
                "Ternary mode requires sufficiently large embedding space (>=128 recommended)"
            )

    return True