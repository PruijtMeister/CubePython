#!/bin/bash
# Setup script for backend virtual environment using UV

echo "Setting up backend virtual environment with UV..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "Please restart your shell or run: source $HOME/.cargo/env"
    exit 1
fi

cd backend

# Check if venv exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Syncing dependencies..."
    uv sync
else
    echo "Creating virtual environment and installing dependencies..."
    uv venv
    uv sync
fi

echo ""
echo "Backend virtual environment setup complete!"
echo "To activate: cd backend && source .venv/bin/activate"
