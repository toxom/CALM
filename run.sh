#!/bin/bash

# CALM - Continual Associative Learning Model
# Startup script for the SDM API server

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}   CALM - Continual Associative Learning Model${NC}"
echo -e "${BLUE}   SDM API Server${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

echo ""
echo -e "${GREEN}Starting CALM API Server...${NC}"
echo -e "${BLUE}API Documentation: ${NC}http://localhost:8000/docs"
echo -e "${BLUE}Test Endpoint:     ${NC}http://localhost:8000/test/memory/run"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo ""

# Start the server
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
