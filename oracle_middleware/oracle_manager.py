import subprocess
import uuid
import os

# Path to store container mappings
containers_file = "containers.txt"

# Internal helper to store new container mapping
def _save_container(name, cid):
    with open(containers_file, "a") as f:
        f.write(f"{name}:{cid}\n")

# Load all saved container mappings
def _load_containers():
    if not os.path.exists(containers_file):
        return {}
    with open(containers_file, "r") as f:
        return dict(
            line.strip().split(":", 1) for line in f if ":" in line
        )

# Create a new Oracle container
def create_oracle_instance(name):
    container_name = f"{name}-{uuid.uuid4().hex[:6]}"

    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "-e", "ORACLE_PASSWORD=oracle123",
        "-p", "0:1521", "-p", "0:5500",
        "gvenzl/oracle-xe"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("🚨 Docker run failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return {
            "id": container_name,
            "cid": None,
            "ip": "",
            "status": "docker_run_failed"
        }

    cid = result.stdout.strip()
    _save_container(container_name, cid)

    # 🔁 Try to get IP up to 5 times
    container_ip = ""
    for attempt in range(5):
        ip_result = subprocess.run([
            "docker", "inspect", "-f",
            "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", cid
        ], capture_output=True, text=True)
        container_ip = ip_result.stdout.strip()

        if container_ip:
            break
        time.sleep(2)  # Wait a bit before retrying

    return {
        "id": container_name,
        "cid": cid,
        "ip": container_ip,
        "status": "created"
    }




# Get current status of a running container
def get_status(container_id):
    cmd = ["docker", "inspect", "-f", "{{.State.Status}}", container_id]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "id": container_id,
            "status": "not_found"
        }

    status = result.stdout.strip()
    return {
        "id": container_id,
        "status": status
    }

# Delete an Oracle container by ID
def delete_instance(container_id):
    result = subprocess.run(["docker", "rm", "-f", container_id], capture_output=True, text=True)
    
    if result.returncode != 0:
        return {
            "id": container_id,
            "status": "delete_failed",
            "error": result.stderr.strip()
        }

    return {
        "id": container_id,
        "status": "deleted"
    }
