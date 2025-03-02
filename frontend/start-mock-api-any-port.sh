#!/bin/bash
cd "$(dirname "$0")"

# Color variables for nice output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default port
DEFAULT_PORT=8080

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -i:"$port" >/dev/null 2>&1
        return $?
    else
        # Try netstat if lsof is not available
        if command -v netstat >/dev/null 2>&1; then
            netstat -tuln | grep ":$port " >/dev/null 2>&1
            return $?
        else
            # If neither is available, just assume port is free
            return 1
        fi
    fi
}

# Function to find and kill process on a specific port
kill_process_on_port() {
    local port=$1
    echo -e "${YELLOW}Attempting to kill process on port $port...${NC}"
    
    if command -v lsof >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        if [ -n "$pid" ]; then
            echo -e "${YELLOW}Killing process $pid on port $port${NC}"
            kill -9 $pid
            sleep 1
            return 0
        fi
    elif command -v fuser >/dev/null 2>&1; then
        fuser -k $port/tcp >/dev/null 2>&1
        sleep 1
        return 0
    fi
    
    echo -e "${RED}Could not kill process on port $port${NC}"
    return 1
}

# Try to kill any existing process on the default port if user wishes
if is_port_in_use $DEFAULT_PORT; then
    echo -e "${YELLOW}Port $DEFAULT_PORT is already in use.${NC}"
    read -p "Do you want to try to kill the process using port $DEFAULT_PORT? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill_process_on_port $DEFAULT_PORT
        # Check if port is now free
        if ! is_port_in_use $DEFAULT_PORT; then
            echo -e "${GREEN}Successfully freed port $DEFAULT_PORT.${NC}"
        else
            echo -e "${RED}Port $DEFAULT_PORT is still in use. Will try a different port.${NC}"
        fi
    else
        echo -e "${YELLOW}Will try a different port.${NC}"
    fi
fi

# Find an available port starting from the default port
PORT=$DEFAULT_PORT
MAX_PORT=$((DEFAULT_PORT + 100))  # Try 100 ports

while is_port_in_use $PORT && [ $PORT -lt $MAX_PORT ]; do
    PORT=$((PORT + 1))
done

if [ $PORT -ge $MAX_PORT ]; then
    echo -e "${RED}Could not find an available port between $DEFAULT_PORT and $MAX_PORT.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting Mock API Server on port $PORT...${NC}"

# Update the .env.local file to use this port
if [ -f ".env.local" ]; then
    # Check if VITE_API_BASE_URL exists and update it
    if grep -q "VITE_API_BASE_URL" .env.local; then
        # Use sed to replace the port in VITE_API_BASE_URL
        if [ "$(uname)" == "Darwin" ]; then
            # macOS requires a different sed syntax
            sed -i '' "s|VITE_API_BASE_URL=http://localhost:[0-9]\+|VITE_API_BASE_URL=http://localhost:$PORT|g" .env.local
        else
            # Linux
            sed -i "s|VITE_API_BASE_URL=http://localhost:[0-9]\+|VITE_API_BASE_URL=http://localhost:$PORT|g" .env.local
        fi
        echo -e "${GREEN}Updated .env.local with new API port: $PORT${NC}"
    else
        # Add the VITE_API_BASE_URL if it doesn't exist
        echo "VITE_API_BASE_URL=http://localhost:$PORT" >> .env.local
        echo -e "${GREEN}Added VITE_API_BASE_URL to .env.local${NC}"
    fi
else
    # Create the .env.local file if it doesn't exist
    echo "VITE_API_BASE_URL=http://localhost:$PORT" > .env.local
    echo -e "${GREEN}Created .env.local with API port: $PORT${NC}"
fi

# Use environment variable to specify the port when starting the server
export PORT=$PORT

# Try to use the CJS version if it exists
if [ -f "mock-api/server.cjs" ]; then
    node mock-api/server.cjs
else
    # Fall back to the original (ESM) version
    node mock-api/server.js
fi
