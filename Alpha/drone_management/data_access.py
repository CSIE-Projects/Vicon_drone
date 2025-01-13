# drone_management/data_access.py

import json
import os
from .config import DRONES_FILE

def load_drones():
    """Load drones from the JSON file."""
    if os.path.exists(DRONES_FILE):
        with open(DRONES_FILE, 'r') as f:
            loaded_drones = json.load(f)
            # Default to True if 'drone_enabled' is missing
            for drone in loaded_drones:
                drone.setdefault('drone_enabled', True)
            return loaded_drones
    return []

def save_drones(drones):
    """Save drones to the JSON file."""
    drones_to_save = []
    for drone in drones:
        drones_to_save.append({
            'name': drone.get('name'),
            'ip': drone.get('ip'),
            'port': drone.get('port'),
            'drone_enabled': drone.get('drone_enabled', True)
        })

    with open(DRONES_FILE, 'w') as f:
        json.dump(drones_to_save, f)
