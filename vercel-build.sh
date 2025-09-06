#!/bin/bash

# Install Python 3.11
pyenv install 3.11.9 --skip-existing
pyenv global 3.11.9

# Update pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Create runtime.txt if it doesn't exist
if [ ! -f runtime.txt ]; then
    echo "python-3.11.9" > runtime.txt
fi
