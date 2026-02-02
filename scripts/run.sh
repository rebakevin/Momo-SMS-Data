#!/bin/bash
# Start the Momo SMS Data API server with virtual environment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Momo SMS Data API...${NC}\n"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv and check dependencies
source venv/bin/activate

# Check if requirements are installed
if ! python3 -c "import apispec" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓ Dependencies installed${NC}\n"
fi

# Stop any existing server
pkill -f "python3 main.py" 2>/dev/null

# Start the server
echo -e "${GREEN}Server starting...${NC}\n"
python3 main.py
