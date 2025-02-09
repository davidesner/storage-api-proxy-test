#!/bin/bash

# Exit on error
set -e

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "Installing project dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your actual configuration values."
fi

# Create data directory for SQLite database
mkdir -p data

echo "Environment setup complete!"
echo "Next steps:"
echo "1. Update the .env file with your configuration"
echo "2. Run 'poetry shell' to activate the virtual environment"
echo "3. Run 'poetry run uvicorn src.main:app --reload' to start the development server" 