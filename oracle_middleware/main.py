from flask import Flask, request, jsonify
import oracle_manager
import signal
import sys
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oracle-middleware')

app = Flask(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal %d", signum)
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

@app.route("/v1.0/<project_id>/instances", methods=["GET"])
def list_instances(project_id):
    """List all Oracle instances."""
    logger.info("Listing instances for project: %s", project_id)
    containers = oracle_manager._load_containers()
    instances = []
    
    for name, info in containers.items():
        status = oracle_manager.get_status(name)
        instances.append(status)
    
    return jsonify({"instances": instances})

@app.route("/v1.0/<project_id>/datastores", methods=["GET"])
def list_datastores(project_id):
    """List available datastores."""
    logger.info("Listing datastores for project: %s", project_id)
    return jsonify({
        "datastores": [{
            "id": "oracle",
            "name": "Oracle",
            "versions": [{
                "id": "1.0",
                "name": "Oracle XE",
                "active": True
            }]
        }]
    })

@app.route("/v1.0/<project_id>/datastore_versions", methods=["GET"])
def list_datastore_versions(project_id):
    """List available datastore versions."""
    logger.info("Listing datastore versions for project: %s", project_id)
    return jsonify({
        "versions": [{
            "id": "1.0",
            "name": "Oracle XE",
            "datastore": "oracle",
            "active": True
        }]
    })

@app.route("/v1.0/<project_id>/instances", methods=["POST"])
def create_instance(project_id):
    """Create a new Oracle instance."""
    data = request.get_json()
    name = data.get("name", "oracle_default")
    logger.info("Creating Oracle instance: %s", name)
    result = oracle_manager.create_oracle_instance(name)
    logger.info("Instance creation result: %s", result)
    return jsonify(result)

@app.route("/v1.0/<project_id>/instances/<instance_id>", methods=["GET"])
def get_instance(project_id, instance_id):
    """Get instance details."""
    logger.info("Getting instance details: %s", instance_id)
    result = oracle_manager.get_status(instance_id)
    return jsonify({"instance": result})

@app.route("/v1.0/<project_id>/instances/<instance_id>", methods=["DELETE"])
def delete_instance(project_id, instance_id):
    """Delete an instance."""
    logger.info("Deleting instance: %s", instance_id)
    result = oracle_manager.delete_instance(instance_id)
    return jsonify(result)

@app.route("/status/<container_id>", methods=["GET"])
def status(container_id):
    """Get container status (internal endpoint)."""
    logger.info("Checking status for container: %s", container_id)
    result = oracle_manager.get_status(container_id)
    return jsonify(result)

if __name__ == "__main__":
    # Ensure log directory exists
    os.makedirs('/var/log/trove', exist_ok=True)
    
    # Start the service
    logger.info("Starting Oracle middleware service")
    app.run(host="0.0.0.0", port=8000)
