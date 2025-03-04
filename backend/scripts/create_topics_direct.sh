#!/bin/bash

# This script directly creates topics using a hardcoded token that we'll generate
# to avoid any issues with token generation

# Generate a fresh token and save it to use in this script
TOKEN=$(python3 -c "
import sys, os, datetime
from datetime import timedelta, timezone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname('$0'), '..')))
from locavox import config
from jose import jwt

# Create admin data
admin_data = {
    'sub': 'admin-user-123',
    'username': 'admin',
    'email': 'admin@example.com',
    'is_admin': True,
    'exp': datetime.datetime.now(timezone.utc) + timedelta(days=7)
}

# Print the token
print(jwt.encode(admin_data, config.SECRET_KEY, algorithm=config.ALGORITHM))
")

# Show the first part of the token
echo "Using token: ${TOKEN:0:20}..."

# Create the topic
curl -v -X 'POST' 'http://localhost:8000/topics/' \
    -H "Authorization: Bearer $TOKEN" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"title": "Festival", "description": "Gather festival activities", "category": "Community", "image_url": "string"}'

echo ""
