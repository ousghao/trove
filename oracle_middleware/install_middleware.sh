#!/bin/bash

# Exit on any error
set -e

# Create log directory if it doesn't exist
sudo mkdir -p /var/log/trove
sudo chown stack:stack /var/log/trove

# Copy service file
sudo cp /opt/stack/trove/oracle_middleware/oracle-middleware.service /etc/systemd/system/

# Ensure service is stopped before reconfiguring
sudo systemctl stop oracle-middleware || true

# Reload systemd
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable oracle-middleware
sudo systemctl start oracle-middleware

# Wait for service to be ready
echo "Waiting for Oracle middleware to start..."
for i in {1..60}; do
    if curl -s http://localhost:8000/status/test > /dev/null; then
        echo "Oracle middleware is running!"
        # Verify service status
        if systemctl is-active --quiet oracle-middleware; then
            echo "Oracle middleware service is active and running"
            exit 0
        else
            echo "Service is not active despite being reachable"
            exit 1
        fi
    fi
    echo "Waiting for service to start... (attempt $i/60)"
    sleep 2
done

echo "Failed to start Oracle middleware"
exit 1 