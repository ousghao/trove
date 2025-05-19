#!/bin/bash

set -e

echo "[+] Setting up Oracle middleware..."

cd /opt/stack/trove/oracle_middleware

# Log directory
sudo mkdir -p /var/log/trove
sudo chown -R stack:stack /var/log/trove
sudo chmod 755 /var/log/trove

# Correct ownership
sudo chown -R stack:stack .

# Recreate venv to avoid architecture errors
rm -rf venv
python3 -m venv venv
chmod +x venv/bin/python

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip --break-system-packages
pip install --break-system-packages -r requirements.txt

# Write or overwrite systemd service
cat <<EOF | sudo tee /etc/systemd/system/oracle-middleware.service > /dev/null
[Unit]
Description=Oracle Middleware Service for Trove
After=network.target

[Service]
Type=simple
User=stack
Group=stack
WorkingDirectory=/opt/stack/trove/oracle_middleware
ExecStart=/opt/stack/trove/oracle_middleware/venv/bin/python /opt/stack/trove/oracle_middleware/main.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/trove/oracle-middleware.log
StandardError=append:/var/log/trove/oracle-middleware.log

[Install]
WantedBy=multi-user.target
EOF

# Permissions
sudo chmod 644 /etc/systemd/system/oracle-middleware.service

# Reload and launch
echo "[+] Reloading systemd and starting service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl stop oracle-middleware || true
sudo systemctl enable oracle-middleware
sudo systemctl restart oracle-middleware

# Check status
echo "[+] Waiting for Oracle middleware to respond..."
for i in {1..10}; do
    if curl -s http://localhost:8000/status/test > /dev/null; then
        echo "[✓] Oracle middleware is running!"
        if systemctl is-active --quiet oracle-middleware; then
            echo "[✓] Service is active and healthy"
            exit 0
        else
            echo "[!] Middleware reachable but systemd reports inactive"
            sudo journalctl -u oracle-middleware -n 50 --no-pager
            exit 1
        fi
    fi
    echo "  ... waiting ($i/10)"
    sleep 2
done

echo "[✗] Middleware did not respond on port 8000"
sudo journalctl -u oracle-middleware -n 50 --no-pager
exit 1
