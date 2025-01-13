# drone_management/routes.py

import subprocess
from flask import request, jsonify, render_template, Blueprint

from .data_access import load_drones, save_drones
from .utils import kill_mavproxy_processes, ping, shutdown_server

def init_routes(app):
    """
    Registers all routes/endpoints on the given Flask app.
    """

    # We'll keep a "global-like" variable at this level.
    drones = load_drones()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        nonlocal drones  # So that POST changes can persist in memory

        if request.method == 'POST':
            drone_data = request.get_json()
            if drone_data:
                # Update the global drones list
                drones = [
                    {
                        'name': d['name'],
                        'ip': d['ip'],
                        'port': d['port'],
                        'drone_enabled': d.get('drone_enabled', True)
                    } for d in drone_data
                ]
                save_drones(drones)
                return jsonify({'message': 'Drones saved successfully!'})
            return jsonify({'message': 'No drone data provided.'}), 400

        # If GET, reload drones from file (in case they've changed externally)
        drones = load_drones()
        return render_template('index.html', drones=drones)

    @app.route('/load_drones', methods=['GET'])
    def load_drones_route():
        """Endpoint to return the drones from JSON file."""
        return jsonify(load_drones())

    @app.route('/ping', methods=['POST'])
    def ping_route():
        """Endpoint to ping a given IP."""
        data = request.json
        ip = data.get('ip')
        return jsonify(ping(ip))

    @app.route('/kill_mavproxy', methods=['POST'])
    def kill_mavproxy_route():
        """Endpoint to kill all MAVProxy processes."""
        kill_mavproxy_processes()
        return 'MAVProxy processes terminated successfully!'

    @app.route('/exit', methods=['POST'])
    def exit_route():
        """
        Saves current drones to file, kills MAVProxy processes,
        and shuts down the Flask server.
        """
        save_drones(drones)
        kill_mavproxy_processes()
        shutdown_server()
        return 'Server is shutting down...'

    @app.route('/run_mavproxy', methods=['POST'])
    def run_mavproxy_route():
        """Endpoint to start MAVProxy for a given drone."""
        data = request.json
        drone_name = data.get('name')
        port = data.get('port')

        command = (
            f"/usr/local/bin/mavproxy.py --master=udpin:192.168.15.10:{port} "
            f"--cmd=\"module load vicon; vicon set object_name {drone_name}; vicon start\""
        )

        try:
            # Run the command in the background
            subprocess.Popen(command, shell=True)
            return jsonify({'message': f'MAVProxy started for {drone_name} on port {port}.'})
        except Exception as e:
            return jsonify({'message': f'Error starting MAVProxy: {str(e)}'}), 500
