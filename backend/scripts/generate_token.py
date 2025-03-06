#!/usr/bin/env python3
"""
Generate a fresh JWT token for testing the Locavox API.
"""

import sys
import os
import datetime
from datetime import timedelta, timezone

# Add the parent directory to the path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from locavox.services.auth_service import create_access_token


def main():
    # Create data for an admin user
    admin_data = {
        "sub": "admin-user-123",
        "username": "admin",
        "email": "admin@example.com",
        "is_superuser": True,
    }

    # Create token with 7 days expiration
    expires_delta = timedelta(days=7)
    token = create_access_token(admin_data, expires_delta=expires_delta)

    # Print the token
    print("# Generated Admin Bearer Token:")
    print(f'BEARER_TOKEN="{token}"')
    print("\n# Example usage with curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/topics/')

    # Print expiration information
    now = datetime.datetime.now(timezone.utc)
    expiry = now + expires_delta
    print(f"\n# Token will expire on: {expiry}")


if __name__ == "__main__":
    main()
