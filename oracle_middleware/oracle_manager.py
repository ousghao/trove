import subprocess
import uuid
import os
import time
from datetime import datetime

# Path to store container mappings
containers_file = "containers.txt"

# Internal helper to store new container mapping
def _save_container(name, cid, created_at):
    with open(containers_file, "a") as f:
        f.write(f"{name}:{cid}:{created_at}\n")

# Load all saved container mappings
def _load_containers():
    if not os.path.exists(containers_file):
        return {}
    with open(containers_file, "r") as f:
        containers = {}
        for line in f:
            if ":" in line:
                parts = line.strip().split(":", 2)
                if len(parts) == 3:
                    name, cid, created_at = parts
                    containers[name] = {"cid": cid, "created_at": created_at}
        return containers

# Create a new Oracle container
def create_oracle_instance(name):
    container_name = f"{name}-{uuid.uuid4().hex[:6]}"
    created_at = datetime.utcnow().isoformat()

    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "-e", "ORACLE_PASSWORD=oracle123",
        "-p", "0:1521", "-p", "0:5500",
        "gvenzl/oracle-xe"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "id": container_name,
            "name": name,
            "status": "ERROR",
            "created": created_at,
            "updated": created_at,
            "datastore": {
                "type": "oracle",
                "version": "1.0"
            },
            "fault": {
                "message": result.stderr.strip(),
                "created": created_at
            }
        }

    cid = result.stdout.strip()
    _save_container(container_name, cid, created_at)

    # Get container IP
    container_ip = ""
    for attempt in range(5):
        ip_result = subprocess.run([
            "docker", "inspect", "-f",
            "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", cid
        ], capture_output=True, text=True)
        container_ip = ip_result.stdout.strip()

        if container_ip:
            break
        time.sleep(2)

    return {
        "id": container_name,
        "name": name,
        "status": "BUILD",
        "created": created_at,
        "updated": created_at,
        "datastore": {
            "type": "oracle",
            "version": "1.0"
        },
        "addresses": [{
            "type": "private",
            "address": container_ip
        }]
    }

# Get current status of a running container
def get_status(container_id):
    cmd = ["docker", "inspect", "-f", "{{.State.Status}}", container_id]
    result = subprocess.run(cmd, capture_output=True, text=True)

    containers = _load_containers()
    container_info = containers.get(container_id, {})
    created_at = container_info.get("created_at", datetime.utcnow().isoformat())

    if result.returncode != 0:
        return {
            "id": container_id,
            "status": "ERROR",
            "created": created_at,
            "updated": datetime.utcnow().isoformat(),
            "datastore": {
                "type": "oracle",
                "version": "1.0"
            },
            "fault": {
                "message": "Container not found",
                "created": datetime.utcnow().isoformat()
            }
        }

    status = result.stdout.strip()
    trove_status = {
        "running": "ACTIVE",
        "created": "BUILD",
        "exited": "SHUTDOWN",
        "paused": "PAUSED"
    }.get(status, "ERROR")

    return {
        "id": container_id,
        "status": trove_status,
        "created": created_at,
        "updated": datetime.utcnow().isoformat(),
        "datastore": {
            "type": "oracle",
            "version": "1.0"
        }
    }

# Delete an Oracle container by ID
def delete_instance(container_id):
    result = subprocess.run(["docker", "rm", "-f", container_id], capture_output=True, text=True)
    
    if result.returncode != 0:
        return {
            "id": container_id,
            "status": "ERROR",
            "fault": {
                "message": result.stderr.strip(),
                "created": datetime.utcnow().isoformat()
            }
        }

    return {
        "id": container_id,
        "status": "DELETED"
    }
