# CALM SDM SDK

This SDK provides tools for interacting with the Sparse Distributed Memory (SDM) system in CALM.

## Components

- `cli.py`: Command-line tool for encoding, storing, and querying vectors.
- `server.py`: Minimal REST API exposing SDM functionality.
- `examples/`: Example scripts demonstrating common operations.

## Usage

Run CLI commands:

```bash
python cli.py encode "Hello world"
python cli.py store <vector>
python cli.py query <vector>