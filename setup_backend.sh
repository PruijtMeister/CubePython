#!/bin/bash
# Setup script for backend virtual environment

echo "Setting up backend virtual environment..."

# Check if venv exists
if [ -d "backend/venv" ]; then
    echo "Virtual environment already exists at backend/venv"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf backend/venv
    else
        echo "Using existing virtual environment"
        exit 0
    fi
fi

# Create virtual environment
cd backend
python3 -m venv venv

# Activate and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Backend virtual environment setup complete!"
echo "To activate: cd backend && source venv/bin/activate"
