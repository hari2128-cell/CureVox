from flask import Blueprint, jsonify
from utils.response import success

health_bp = Blueprint("health", __name__)

@health_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify(success("pong"))
