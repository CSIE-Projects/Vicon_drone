# drone_management/utils.py

import subprocess
import platform
import os
from flask import request

def ping(ip):
    """Ping an IP address and return whether it's active."""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]

    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        return {'success': True, 'message': 'Active'}
    except subprocess.CalledProcessError:
        return {'success': False, 'message': 'Inactive'}

def kill_mavproxy_processes():
    """Kill all mavproxy.py processes."""
    if os.name == 'nt':
        # Windows
        subprocess.call(['taskkill', '/IM', 'python.exe', '/F'])
    else:
        # Linux/Mac
        os.system('pkill -9 mavproxy')
        subprocess.call(['pkill', '-f', 'mavproxy.py'])

def shutdown_server():
    """Shutdown the Flask server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
