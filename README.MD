# CALM — Continual Associative Learning Model

CALM is a modular hybrid AI system based on Sparse Distributed Memory (SDM), inspired by biological cognition. It allows fast, continual, and adaptive learning using high-dimensional binary vectors and associative recall.

This system does **not** rely on transformers — but is compatible with hybrid setups.


## Goals & Use Cases

- Continual learning with no catastrophic forgetting
- High-speed personalization per user
- Interpretable associative recall
- Offline + online memory fusion
- Human-like abstraction (object models from transitions)

## Architecture Overview
```
CALM/
├── backend/               # Core logic and API backend
│   ├── api/               # FastAPI endpoints to interact with SDM
│   │   └── main.py
│   ├── core/              # Core computational modules
│   │   └── sdm/           # Sparse Distributed Memory components
│   │       ├── memory.py      # Memory read/write, voting, recall
│   │       ├── encoder.py     # Converts inputs into binary HD vectors
│   │       └── utils.py       # Hamming distance, vector ops, etc.
│   └── experiments/      # Jupyter notebooks or demos
│       └── notebooks/
│
├── sdk/                  # Optional standalone SDM SDK
│   └── standalone/
│       ├── cli.py            # Command-line usage of SDM
│       └── server.py         # Lightweight REST server (FastAPI/Flask)
│
├── requirements.txt      # Quick install of dependencies
├── pyproject.toml        # Project metadata, dependencies, build config
├── README.md             # Project overview and instructions
```

## Processing Flow

1. **Input Encoding**
    - `encoder.py` converts raw inputs (e.g., text) into high-dimensional binary vectors.
    - These can be:
        - Tokens (e.g., words or phrases)
        - Pairs or triplets for transition modeling

2. **Memory Write**
    - `memory.py` stores encoded vectors using sparse, distributed addressing.
    - Writes can be done offline (pretraining) or online (user interaction).

3. **Memory Query (Recall)**
    - When new input is processed, similar stored vectors are retrieved via **Hamming distance**.
    - Multiple partial matches “vote” for the most probable recall.

4. **Output Generation**
    - Recalled memory can be returned directly or passed to higher logic (e.g., summarization, decision-making).
    - Optionally, the response can be formatted as natural language (if language encoder is used).


## Planned Modules

| Module       | Description                                |
|--------------|--------------------------------------------|
| encoder.py   | Converts text to binary HD vectors          |
| memory.py    | Stores and retrieves using SDM logic        |
| utils.py     | Vector ops, distance functions, helpers     |
| cli.py       | Simple CLI to test/inspect SDM              |
| server.py    | REST interface for embedding into apps      |
| main.py      | FastAPI app exposing SDM endpoints          |
| notebooks/   | Test ideas, data generation, visualizations |

---

## Training Strategy

Hybrid training approach uses:
  - Offline pretraining: initialize memory from large corpus (e.g., language data).
  - Online updates: new experiences stored immediately without retraining entire model.



## How to Run

> Requires Python 3.10+

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run standalone CLI
python sdk/standalone/cli.py
```

CALM is designed to offer an alternative to transformer-only models, with better adaptability, personalization, and biological inspiration.


## License

Apache 2.0

