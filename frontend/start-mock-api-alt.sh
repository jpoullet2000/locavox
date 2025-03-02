#!/bin/bash
cd "$(dirname "$0")"

# Color variables for nice output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default port changed from 8000 to 8080
DEFAULT_PORT=8080

# Function to check if a port is in use - without relying on netstat
is_port_in_use() {
    local port=$1
    # Try different methods to check if port is in use
    if command -v lsof >/dev/null 2>&1; then
        lsof -i:"$port" >/dev/null 2>&1
        return $?
    elif command -v ss >/dev/null 2>&1; then
        ss -tuln | grep ":$port " >/dev/null 2>&1
        return $?
    else
        # Try a direct approach by attempting to bind to the port
        (echo >/dev/tcp/localhost/$port) >/dev/null 2>&1
        # If the above command succeeds, the port is in use
        if [ $? -eq 0 ]; then
            return 0
        else
            return 1
        fi
    fi
}

# Try to find an available port starting from the default port
PORT=$DEFAULT_PORT
MAX_PORT=$((DEFAULT_PORT + 20)) # Try 20 ports

echo -e "${YELLOW}Looking for available port starting from $PORT...${NC}"

while is_port_in_use $PORT && [ $PORT -lt $MAX_PORT ]; do
    echo -e "${YELLOW}Port $PORT is in use, trying next port${NC}"
    PORT=$((PORT + 1))
done

if [ $PORT -ge $MAX_PORT ]; then
    echo -e "${RED}Could not find an available port between $DEFAULT_PORT and $MAX_PORT.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting Mock API Server on port $PORT...${NC}"

# Update the .env.local file to use this port
if [ -f ".env.local" ]; then
    echo "Updating .env.local with the new port"
    if grep -q "VITE_API_BASE_URL" .env.local; then
        # Use perl instead of sed for better cross-platform compatibility
        perl -i -pe "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=http://localhost:$PORT|g" .env.local
    else
        # Add new entry
        echo "VITE_API_BASE_URL=http://localhost:$PORT" >> .env.local
    fi
else
    # Create new .env.local
    echo "VITE_API_BASE_URL=http://localhost:$PORT" > .env.local
    echo "Created .env.local with port $PORT"
fi

# Use environment variable to specify the port when starting the server
export PORT=$PORT

# Try to use the CJS version if it exists
if [ -f "mock-api/server.cjs" ]; then
    node mock-api/server.cjs || true
else
    # Fall back to the original (ESM) version
    node mock-api/server.js || true
fi

echo -e "${RED}Server stopped.${NC}"
