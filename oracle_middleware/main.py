from flask import Flask, request, jsonify
import oracle_manager

app = Flask(__name__)

@app.route("/deploy_oracle", methods=["POST"])
def deploy_oracle():
    data = request.get_json()
    name = data.get("name", "oracle_default")
    result = oracle_manager.create_oracle_instance(name)
    print("returning from create:",result)
    return jsonify(result)

@app.route("/status/<container_id>", methods=["GET"])
def status(container_id):
    result = oracle_manager.get_status(container_id)
    return jsonify(result)

@app.route("/delete/<container_id>", methods=["DELETE"])
def delete(container_id):
    result = oracle_manager.delete_instance(container_id)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
