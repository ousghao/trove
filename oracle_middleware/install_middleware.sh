#!/bin/bash

set -e

echo "[+] Setting up Oracle middleware..."

# Create log directory with proper permissions
sudo mkdir -p /var/log/trove
sudo chown -R stack:stack /var/log/trove
sudo chmod 755 /var/log/trove

# Setup Python environment
cd /opt/stack/trove/oracle_middleware

# Ensure proper ownership
sudo chown -R stack:stack .

if [ ! -d "venv" ]; then
    echo "[+] Creating Python virtual environment..."
    python3 -m venv venv
    sudo chown -R stack:stack venv
fi

# Always ensure venv/bin/python is a symlink to python3
if [ ! -f "venv/bin/python" ] || [ ! -x "venv/bin/python" ]; then
    ln -sf python3 venv/bin/python
fi

chmod +x venv/bin/python3
chmod +x venv/bin/python
chmod +x main.py

source venv/bin/activate
pip install --upgrade pip --break-system-packages
pip install --break-system-packages -r requirements.txt


# Copy systemd service
sudo cp oracle-middleware.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/oracle-middleware.service
sudo chmod 644 /etc/systemd/system/oracle-middleware.service

# Reload and restart the service
echo "[+] Reloading systemd..."
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
        if systemctl is-active --quiet oracle-middleware; then
            echo "[✓] Systemd service is active"
            exit 0
        else
            echo "[!] Service reachable but not marked active"
            echo "[!] Checking logs..."
            sudo journalctl -u oracle-middleware -n 50 --no-pager
            exit 1
        fi
    fi
    echo "  ... waiting ($i/60)"
    sleep 2
done

echo "[✗] Failed to start Oracle middleware"
echo "[!] Checking logs..."
sudo journalctl -u oracle-middleware -n 50 --no-pager
exit 1
