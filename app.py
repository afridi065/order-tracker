import json
import logging
import os
import uuid

import boto3
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Temporary local copy. DynamoDB replaces this later.
orders = {}

QUEUE_URL = os.environ.get("QUEUE_URL")
sqs = boto3.client("sqs", region_name=os.environ.get("AWS_REGION", "ap-south-1"))


def send_to_queue(order):
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(order))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    for field in ("customer", "item", "quantity"):
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    if not isinstance(data["quantity"], int) or data["quantity"] <= 0:
        return jsonify({"error": "quantity must be a positive integer"}), 400

    order_id = str(uuid.uuid4())
    order = {
        "order_id": order_id,
        "customer": data["customer"],
        "item": data["item"],
        "quantity": data["quantity"],
        "status": "RECEIVED",
    }

    try:
        send_to_queue(order)
    except Exception:
        app.logger.exception("Failed to enqueue order %s", order_id)
        return jsonify({"error": "Could not queue order, try again"}), 503

    orders[order_id] = order
    app.logger.info("Order %s queued", order_id)
    return jsonify({"order_id": order_id, "status": "RECEIVED"}), 202


@app.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
