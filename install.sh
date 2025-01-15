#!/bin/bash

sudo ./service_creator.sh
PATH="${PATH:+${PATH}:}$HOME/.local/bin"
pip install MAVProxy
pip install -r requirements.txt
