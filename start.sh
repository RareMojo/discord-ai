#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Update pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Launch src/main.py
python src/main.py

# Deactivate the virtual environment
deactivate