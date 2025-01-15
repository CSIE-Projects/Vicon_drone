#!/bin/bash

# Check if the first argument is "--autorun"
if [[ "$1" == "--autorun" ]]; then
    sudo ./service_creator.sh
fi

# Proceed with the rest of your script
PATH="${PATH:+${PATH}:}$HOME/.local/bin"
pip install MAVProxy
pip install -r requirements.txt
