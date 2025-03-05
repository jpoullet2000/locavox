#!/usr/bin/env python
"""
Utility script to generate JWT tokens for testing the Locavox backend API.

Examples:

python backend/scripts/generate_test_token.py --user-id admin-123 --username admin --email admin@example.com --admin --days 90
"""
import sys
import os
from datetime import timedelta
import argparse

# Add the parent directory to the path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from locavox.services.auth_service import create_access_token

def create_test_token(user_id, username, email, is_admin=False, expire_days=30):
    """Create a JWT token for testing"""
    # Create payload data
    data = {
        "sub": user_id,
        "username": username,
        "email": email,
        "is_admin": is_admin
    }
    
    # Create token with specified expiration
    expires = timedelta(days=expire_days)
    token = create_access_token(data, expires_delta=expires)
    
    return token

def main():
    parser = argparse.ArgumentParser(description="Generate JWT tokens for testing")
    parser.add_argument("--user-id", default="test-user-123", help="User ID to include in token")
    parser.add_argument("--username", default="testuser", help="Username to include in token")
    parser.add_argument("--email", default="test@example.com", help="Email to include in token")
    parser.add_argument("--admin", action="store_true", help="Make this an admin token")
    parser.add_argument("--days", type=int, default=30, help="Token validity in days")
    
    args = parser.parse_args()
    
    # Generate token
    token = create_test_token(
        user_id=args.user_id,
        username=args.username,
        email=args.email,
        is_admin=args.admin,
        expire_days=args.days
    )
    
    # Print output in a useful format
    print("\n=== JWT TOKEN ===")
    print(f"\nToken (valid for {args.days} days):")
    print(token)
    print("\nAuthorization header format:")
    print(f"Authorization: Bearer {token}")
    print("\nCurl example:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/topics/')
    
    if args.admin:
        print("\nThis token has ADMIN privileges")

if __name__ == "__main__":
    main()
