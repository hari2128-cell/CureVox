from flask import Blueprint, request, jsonify
from utils.response import success, error

rash_bp = Blueprint("rash", __name__)

@rash_bp.route("/detect", methods=["POST"])
def detect():
    if 'file' not in request.files:
        return jsonify(error("image missing (form-data key 'file')")), 400
    f = request.files['file']
    # stub
    return jsonify(success({"condition": "eczema", "confidence": 0.74})), 200
