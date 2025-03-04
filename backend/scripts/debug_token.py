#!/usr/bin/env python3
"""
Debug tool to diagnose JWT token issues with the Locavox API.
"""

import sys
import os
import datetime
from datetime import timedelta, timezone
import argparse
import json

# Add the parent directory to the path so we can import from locavox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the required modules
from locavox import config
from jose import jwt


def print_config_info():
    """Print relevant configuration values for debugging"""
    print("=== Configuration Information ===")
    print(f"SECRET_KEY: {config.SECRET_KEY[:5]}... (prefix shown for security)")
    print(f"ALGORITHM: {config.ALGORITHM}")
    print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {config.ACCESS_TOKEN_EXPIRE_MINUTES}")
    print("")


def create_token(is_admin=True, expires_days=7):
    """Create a JWT token directly using config values"""
    # Create data for a user
    user_data = {
        "sub": "admin-user-123" if is_admin else "regular-user-456",
        "username": "admin" if is_admin else "user",
        "email": "admin@example.com" if is_admin else "user@example.com",
        "is_admin": is_admin,
    }

    # Create expiration time using timezone-aware datetime
    expire = datetime.datetime.now(timezone.utc) + timedelta(days=expires_days)
    user_data.update({"exp": expire})

    # Encode the JWT
    token = jwt.encode(user_data, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token, user_data


def decode_token(token):
    """Decode a JWT token using config values"""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload, None
    except Exception as e:
        return None, str(e)


def main():
    parser = argparse.ArgumentParser(description="Debug JWT token issues")
    parser.add_argument("--admin", action="store_true", help="Generate an admin token")
    parser.add_argument("--decode", help="Decode an existing token")
    parser.add_argument("--days", type=int, default=7, help="Token validity in days")

    args = parser.parse_args()

    # Print config information
    print_config_info()

    # Decode an existing token if provided
    if args.decode:
        print(f"=== Decoding Provided Token ===")
        payload, error = decode_token(args.decode)
        if payload:
            print("Token is valid with payload:")
            print(json.dumps(payload, indent=2))

            # Calculate and display expiration date
            if "exp" in payload:
                exp_datetime = datetime.datetime.fromtimestamp(payload["exp"])
                print(f"Token expires: {exp_datetime}")
                print(f"Is expired: {datetime.datetime.utcnow() > exp_datetime}")
        else:
            print(f"Token is invalid: {error}")
        print("")

    # Generate a new token
    print(f"=== Generating New {'Admin' if args.admin else 'Regular'} Token ===")
    token, data = create_token(is_admin=args.admin, expires_days=args.days)

    # Print the token and information
    print(f"Token: {token}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    print(f"Expires: {datetime.datetime.fromtimestamp(data['exp'])}")
    print("")

    # Provide ready-to-use export command
    print("=== Usage Examples ===")
    print(f"# Export as environment variable:")
    print(f"export BEARER_TOKEN='{token}'")
    print("")
    print(f"# For use in create_topics.sh:")
    print(f"BEARER_TOKEN='{token}'")
    print("")
    print(f"# For curl:")
    print(f"curl -H 'Authorization: Bearer {token}' http://localhost:8000/topics/")


if __name__ == "__main__":
    main()
