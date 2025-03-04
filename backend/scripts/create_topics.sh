#!/bin/bash

# Source the token from the token file if it exists, otherwise generate it
TOKEN_FILE="$(dirname "$0")/admin_token.txt"

if [ ! -f "$TOKEN_FILE" ] || [ "$(find "$TOKEN_FILE" -mtime +1)" ]; then
    # Token doesn't exist or is older than 1 day, generate a new one
    echo "Generating new admin token..."
    python3 "$(dirname "$0")/generate_token.py" | grep "^BEARER_TOKEN=" > "$TOKEN_FILE"
fi

# Source the token
source "$TOKEN_FILE"

# Check if the token is set
if [ -z "$BEARER_TOKEN" ]; then
    echo "Error: BEARER_TOKEN not set. Please run generate_token.py manually."
    exit 1
fi

echo "Using token: ${BEARER_TOKEN:0:20}..."

# Create the topic
curl -X 'POST' 'http://localhost:8000/topics/' \
    -H "Authorization: Bearer $BEARER_TOKEN" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"title": "Festival", "description": "Gather festival activities", "category": "Community", "image_url": "string"}'

echo ""