#!/bin/bash
# Install venv if you don’t have it
sudo apt install python3-venv -y

# Create a new environment
python3 -m venv myenv

# Activate it
source myenv/bin/activate

# Now pip works normally
pip install pandas



