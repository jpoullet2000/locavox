#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Mock API Server on port 8080..."

# Try to use the CJS version if it exists
if [ -f "mock-api/server.cjs" ]; then
  node mock-api/server.cjs
else
  # Fall back to the original (ESM) version
  node mock-api/server.js
fi
