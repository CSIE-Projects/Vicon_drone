from flask import Flask, render_template_string, request, jsonify
import json
import os
import subprocess
import threading
import platform

app = Flask(__name__)

DRONES_FILE = 'drones_list.json'
drones = []  # Global variable to hold the drone list

def load_drones():
    """Load drones from the file."""
    if os.path.exists(DRONES_FILE):
        with open(DRONES_FILE, 'r') as f:
            loaded_drones = json.load(f)
            for drone in loaded_drones:
                drone.setdefault('drone_enabled', True)  # Default to True if not present
            return loaded_drones
    return []

def save_drones(drones):
    """Save drones to the file."""
    drones_to_save = []
    for drone in drones:
        drone_copy = {
            'name': drone['name'],
            'ip': drone['ip'],  # Keep the IP
            'port': drone['port'],
            'drone_enabled': drone.get('drone_enabled', True)  # Include drone_enabled
        }
        drones_to_save.append(drone_copy)
    with open(DRONES_FILE, 'w') as f:
        json.dump(drones_to_save, f)

def kill_mavproxy_processes():
    """Kill all mavproxy.py processes."""
    if os.name == 'nt':
        subprocess.call(['taskkill', '/IM', 'python.exe', '/F'])
    else:
        os.system('pkill -9 mavproxy')
        subprocess.call(['pkill', '-f', 'mavproxy.py'])

def ping(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]
    
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        return {'success': True, 'message': 'Active'}
    except subprocess.CalledProcessError:
        return {'success': False, 'message': 'Inactive'}

@app.route('/', methods=['GET', 'POST'])
def index():
    global drones

    if request.method == 'POST':
        drone_data = request.get_json()
        if drone_data:
            drones = [{'name': d['name'], 'ip': d['ip'], 'port': d['port'], 'drone_enabled': d.get('drone_enabled', True)} for d in drone_data]
            save_drones(drones)  # Save the updated drones
            return jsonify({'message': 'Drones saved successfully!'})
        return jsonify({'message': 'No drone data provided.'}), 400

    drones = load_drones()

    # Render the HTML template with loaded drones
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Drone Management Interface</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            .drone-item {
                border: 1px solid #ddd;
                padding: 15px;
                margin: 10px 0;
            }
            #drone-container {
                margin-top: 20px;
            }
            #status {
                font-weight: bold;
            }
            .active {
                color: green;
            }
            .inactive {
                color: red;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mt-5">Drone Management Interface</h1>

            <div id="drone-container">
                {% for drone in drones %}
                <div class="drone-item">
                    <div class="form-group">
                        <label>Drone Name:</label>
                        <input type="text" name="drone_names" class="form-control" value="{{ drone.name }}" placeholder="Drone">
                    </div>
                    <div class="form-group">
                        <label>Drone IP:</label>
                        <input type="text" name="drone_ips" class="form-control" value="{{ drone.ip }}" placeholder="Last Part of IP">
                    </div>
                    <div class="form-group">
                        <label>Port:</label>
                        <select name="drone_ports" class="form-control">
                            {% for port in range(14550, 14600) %}
                            <option value="{{ port }}" {% if port == drone.port|int %}selected{% endif %}>{{ port }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Enabled:</label>
                        <input type="checkbox" name="drone_enabled" {% if drone.drone_enabled %}checked{% endif %}>
                    </div>
                    <button type="button" class="btn btn-danger" onclick="removeDrone(this)">Remove Drone</button>
                    <button type="button" class="btn btn-primary" onclick="openWebPage(this)">Open Web Page</button>
                    <button type="button" class="btn btn-info" onclick="pingDrone(this)">Ping Drone</button>
                    <p id="status" class="inactive">Inactive</p>
                </div>
                {% endfor %}
            </div>

            <div class="text-center">
                <button type="button" class="btn btn-primary" onclick="addDrone()">Add Drone</button>
                <button type="button" class="btn btn-success" onclick="saveDrones()">Save Drones</button>
                <button type="button" class="btn btn-info" onclick="loadDrones()">Load Drones</button>
                <button type="button" class="btn btn-danger" onclick="killMavproxy()">Kill MAVProxy Processes</button>
                <button type="button" class="btn btn-warning" onclick="runMavproxy()">Run MAVProxy</button>
                <button type="button" class="btn btn-secondary" onclick="exitServer()">Exit</button>
            </div>

            <script>
                function addDrone() {
                    const droneContainer = document.getElementById('drone-container');
                    const newDroneItem = document.createElement('div');
                    newDroneItem.className = 'drone-item';
                    const existingPorts = Array.from(droneContainer.querySelectorAll('select[name="drone_ports"]'))
        .map(select => parseInt(select.value));
    const maxPort = existingPorts.length > 0 ? Math.max(...existingPorts) : 14550; // Start from 14550 if none exist

    newDroneItem.innerHTML = `
        <div class="form-group">
            <label>Drone Name:</label>
            <input type="text" name="drone_names" class="form-control" placeholder="Drone">
        </div>
        <div class="form-group">
            <label>Drone IP:</label>
            <input type="text" name="drone_ips" class="form-control" value="192.168.15." placeholder="Last Part of IP">
        </div>
        <div class="form-group">
            <label>Port:</label>
            <select name="drone_ports" class="form-control">
                <option value="${maxPort + 1}">${maxPort + 1}</option>
                ${Array.from({ length: 50 }, (_, i) => maxPort + 2 + i).map(port => `
                    <option value="${port}">${port}</option>
                `).join('')}
            </select>
        </div>
        <div class="form-group">
            <label>Enabled:</label>
            <input type="checkbox" name="drone_enabled">
        </div>
        <button type="button" class="btn btn-danger" onclick="removeDrone(this)">Remove Drone</button>
        <button type="button" class="btn btn-primary" onclick="openWebPage(this)">Open Web Page</button>
        <button type="button" class="btn btn-info" onclick="pingDrone(this)">Ping Drone</button>
        <p id="status" class="inactive">Inactive</p>
    `;
    droneContainer.appendChild(newDroneItem);
    autoPingDrones();
}

                function pingDrone(button) {
        const droneItem = button.closest('.drone-item');
        const ip = droneItem.querySelector('input[name="drone_ips"]').value;
        const statusText = droneItem.querySelector('#status');

        fetch('/ping', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip })
        })
        .then(response => response.json())
        .then(result => {
            statusText.textContent = result.message;
            statusText.className = result.success ? 'active' : 'inactive';
        })
        .catch(error => {
            console.error('Error pinging drone:', error);
        });
    }
    function autoPingDrones() {
        const droneItems = document.querySelectorAll('.drone-item');
        droneItems.forEach((droneItem, index) => {
            setInterval(() => {
                const pingButton = droneItem.querySelector('.btn-info');
                pingDrone(pingButton);
            }, 5000 * (index + 1)); // Delay each drone ping by 5 seconds multiplied by its index
        });
    }

                function removeDrone(button) {
                    const droneItem = button.closest('.drone-item');
                    if (droneItem) {
                        droneItem.remove();
                    }
                }

                function saveDrones() {
                    const drones = [];
                    document.querySelectorAll('.drone-item').forEach(drone => {
                        const name = drone.querySelector('input[name="drone_names"]').value;
                        const ip = drone.querySelector('input[name="drone_ips"]').value;
                        const port = drone.querySelector('select[name="drone_ports"]').value;
                        const enabled = drone.querySelector('input[name="drone_enabled"]').checked;
                        drones.push({ name, ip, port, drone_enabled: enabled });
                    });

                    fetch('/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(drones)
                    })
                    .then(response => response.json())
                    .then(data => alert(data.message))
                    .catch(error => console.error('Error saving drones:', error));
                }

                function openWebPage(button) {
                    const ipAddress = button.closest('.drone-item').querySelector('input[name="drone_ips"]').value;
                    if (ipAddress) {
                        window.open(`http://${ipAddress}:5000`, '_blank'); 
                    } else {
                        alert('No IP address provided for this drone.');
                    }
                }

                function loadDrones() {
                    fetch('/load_drones')
                        .then(response => response.json())
                        .then(drones => {
                            const droneContainer = document.getElementById('drone-container');
                            droneContainer.innerHTML = '';  // Clear the existing list
                            drones.forEach(drone => {
                                const droneItem = document.createElement('div');
                                droneItem.className = 'drone-item';
                                droneItem.innerHTML = `
                                    <div class="form-group">
                                        <label>Drone Name:</label>
                                        <input type="text" name="drone_names" class="form-control" value="${drone.name}" placeholder="Drone">
                                    </div>
                                    <div class="form-group">
                                        <label>Drone IP:</label>
                                        <input type="text" name="drone_ips" class="form-control" value="${drone.ip}" placeholder="Last Part of IP">
                                    </div>
                                    <div class="form-group">
                                        <label>Port:</label>
                                        <select name="drone_ports" class="form-control">
                                            ${Array.from({length: 50}, (_, i) => 14550 + i).map(port => `
                                                <option value="${port}" ${port == drone.port ? 'selected' : ''}>${port}</option>
                                            `).join('')}
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label>Enabled:</label>
                                        <input type="checkbox" name="drone_enabled" ${drone.drone_enabled ? 'checked' : ''}>
                                    </div>
                                    <button type="button" class="btn btn-danger" onclick="removeDrone(this)">Remove Drone</button>
                                    <button type="button" class="btn btn-primary" onclick="openWebPage(this)">Open Web Page</button>
                                    <button type="button" class="btn btn-info" onclick="pingDrone(this)">Ping Drone</button>
                                    <p id="status" class="inactive">Inactive</p>
                                `;
                                droneContainer.appendChild(droneItem);
                            });
                        })
                        .catch(error => console.error('Error loading drones:', error));
                }

                function killMavproxy() {
                    fetch('/kill_mavproxy', { method: 'POST' })
                        .then(response => response.text())
                        .then(data => alert(data));
                }
                autoPingDrones();

                function runMavproxy() {
                    const drones = [];
                    document.querySelectorAll('.drone-item').forEach(drone => {
                        const name = drone.querySelector('input[name="drone_names"]').value;
                        const port = drone.querySelector('select[name="drone_ports"]').value;
                        const enabled = drone.querySelector('input[name="drone_enabled"]').checked;

                        if (enabled) {
                            drones.push({ name, port });
                        }
                    });

                    drones.forEach(drone => {
                        fetch(`/run_mavproxy`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(drone)
                        })
                        .then(response => response.json())
                        .then(data => alert(data.message))
                        .catch(error => console.error('Error running MAVProxy:', error));
                    });
                }

                function exitServer() {
                    if (confirm("Are you sure you want to exit?")) {
                        fetch('/exit', { method: 'POST' })
                            .then(response => response.text())
                            .then(data => {
                                alert(data);
                                window.close();
                            });
                    }
                }
            </script>
        </div>
    </body>
    </html>
    ''', drones=drones)

@app.route('/load_drones', methods=['GET'])
def load_drones_route():
    """Load drones from the file."""
    return jsonify(load_drones())

@app.route('/ping', methods=['POST'])
def ping_route():
    data = request.json
    ip = data.get('ip')
    result = ping(ip)
    return jsonify(result)

@app.route('/kill_mavproxy', methods=['POST'])
def kill_mavproxy_route():
    kill_mavproxy_processes()
    return 'MAVProxy processes terminated successfully!'

@app.route('/exit', methods=['POST'])
def exit_route():
    """Save drones, kill MAVProxy processes, and exit the server."""
    save_drones(drones)  # Save the current drones
    kill_mavproxy_processes()  # Kill MAVProxy processes
    shutdown_server()  # Shutdown the Flask server
    return 'Server is shutting down...'

def shutdown_server():
    """Shutdown the Flask server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/run_mavproxy', methods=['POST'])
def run_mavproxy_route():
    """Run MAVProxy for the specified drone."""
    data = request.json
    drone_name = data['name']
    port = data['port']

    command = f"/usr/local/bin/mavproxy.py --master=udpin:192.168.15.10:{port} --cmd=\"module load vicon; vicon set object_name {drone_name}; vicon start\""

    try:
        subprocess.Popen(command, shell=True)
        return jsonify({'message': f'MAVProxy started for {drone_name} on port {port}.'})
    except Exception as e:
        return jsonify({'message': f'Error starting MAVProxy: {str(e)}'}), 500

# Start the application
drones = load_drones()

if __name__ == '__main__':
    app.run(debug=True, host='192.168.15.10')
