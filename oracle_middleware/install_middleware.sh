#!/bin/bash

set -e

echo "[+] Setting up Oracle middleware..."

# Create log directory
sudo mkdir -p /var/log/trove
sudo chown stack:stack /var/log/trove

# Setup Python environment
cd /opt/stack/trove/oracle_middleware

if [ ! -d "venv" ]; then
    echo "[+] Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install --break-system-packages -r requirements.txt

# Copy systemd service
sudo cp oracle-middleware.service /etc/systemd/system/

# Reload and restart the service
sudo systemctl stop oracle-middleware || true
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable oracle-middleware
sudo systemctl start oracle-middleware

# Wait for service to be ready
echo "[+] Waiting for Oracle middleware to start..."
for i in {1..60}; do
    if curl -s http://localhost:8000/status/test > /dev/null; then
        echo "[✓] Oracle middleware is running!"
        systemctl is-active --quiet oracle-middleware && {
            echo "[✓] Systemd service is active"
            exit 0
        }
        echo "[!] Service reachable but not marked active"
        exit 1
    fi
    echo "  ... waiting ($i/60)"
    sleep 2
done

echo "[✗] Failed to start Oracle middleware"
exit 1
