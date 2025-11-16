#!/bin/bash
# Setup script for scripts virtual environment

echo "Setting up scripts virtual environment..."

# Check if venv exists
if [ -d "scripts/venv" ]; then
    echo "Virtual environment already exists at scripts/venv"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf scripts/venv
    else
        echo "Using existing virtual environment"
        exit 0
    fi
fi

# Create virtual environment
cd scripts
python3 -m venv venv

# Activate and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Scripts virtual environment setup complete!"
echo "To activate: cd scripts && source venv/bin/activate"
