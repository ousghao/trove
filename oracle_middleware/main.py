from flask import Flask, request, jsonify
import oracle_manager
import signal
import sys
import logging
import os

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

@app.route("/deploy_oracle", methods=["POST"])
def deploy_oracle():
    data = request.get_json()
    name = data.get("name", "oracle_default")
    logger.info("Creating Oracle instance: %s", name)
    result = oracle_manager.create_oracle_instance(name)
    logger.info("Instance creation result: %s", result)
    return jsonify(result)

@app.route("/status/<container_id>", methods=["GET"])
def status(container_id):
    logger.info("Checking status for container: %s", container_id)
    result = oracle_manager.get_status(container_id)
    return jsonify(result)

@app.route("/delete/<container_id>", methods=["DELETE"])
def delete(container_id):
    logger.info("Deleting container: %s", container_id)
    result = oracle_manager.delete_instance(container_id)
    return jsonify(result)

if __name__ == "__main__":
    # Ensure log directory exists
    os.makedirs('/var/log/trove', exist_ok=True)
    
    # Start the service
    logger.info("Starting Oracle middleware service")
    app.run(host="0.0.0.0", port=8000)
