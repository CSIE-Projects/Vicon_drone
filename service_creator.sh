#!/bin/bash
# Determine the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the systemd service file using the dynamic path
SERVICE_FILE="/etc/systemd/system/vicon_manager.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Reboot message systemd service.

[Service]
Type=simple
ExecStart=/bin/bash ${SCRIPT_DIR}/Alpha/launch.sh

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable rebootmessage.service
sudo systemctl start rebootmessage.service
