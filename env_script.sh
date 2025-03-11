#!/bin/bash

# Load user environment variables (cron runs in a minimal environment)
source /home/pi/.bashrc

# Source Conda script
source /home/pi/miniconda3/etc/profile.d/conda.sh

# Activate Conda environment
conda run -n Raspitouille python /home/pi/Raspitouille/Team3/frontend/sp_recognition.py



