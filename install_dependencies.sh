#!/bin/bash

echo "Installing Locavox dependencies..."

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed or not in PATH"
    exit 1
fi

# Install base requirements
echo "Installing base requirements..."
pip install -r requirements.txt

# Check for PostgreSQL usage
if grep -q "DATABASE_URL=postgresql" .env 2>/dev/null || [ "$DATABASE_TYPE" = "postgresql" ]; then
    echo "PostgreSQL configuration detected, installing asyncpg..."
    pip install asyncpg

    # On some systems, additional system dependencies might be needed
    if [ "$(uname)" = "Linux" ]; then
        echo "You may need to install PostgreSQL development libraries if not already installed."
        echo "On Debian/Ubuntu: sudo apt-get install libpq-dev"
        echo "On RHEL/CentOS/Fedora: sudo dnf install postgresql-devel"
    elif [ "$(uname)" = "Darwin" ]; then
        echo "You may need to install PostgreSQL if not already installed."
        echo "With Homebrew: brew install postgresql"
    fi
fi

echo "Dependencies installed successfully."
echo "You can now start the application."
