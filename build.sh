#!/bin/bash

# Install Python 3.11
pyenv install 3.11.9 --skip-existing
pyenv global 3.11.9

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create a .python-version file
echo "3.11.9" > .python-version
