#!/bin/bash

set -e  # Exit on any error

echo "Setting up virtual environment for RAG Chatbot backend..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "Virtual environment setup complete!"
echo "Virtual environment created in: $(pwd)/venv"
echo "Dependencies installed from requirements.txt"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"