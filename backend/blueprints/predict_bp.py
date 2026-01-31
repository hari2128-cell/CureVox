from flask import Blueprint, request, jsonify
from utils.response import success, error

predict_bp = Blueprint("predict", __name__)

# For demo: accept file upload via form-data under 'file' or JSON (url)
@predict_bp.route("/cough", methods=["POST"])
def cough():
    # TODO: replace with real model code
    # Accept file
    if 'file' not in request.files:
        return jsonify(error("file missing (form-data key 'file')")), 400
    f = request.files['file']
    # stub: respond with random class
    return jsonify(success({"diagnosis": "cough_detected", "confidence": 0.82})), 200

@predict_bp.route("/breath", methods=["POST"])
def breath():
    if 'file' not in request.files:
        return jsonify(error("file missing (form-data key 'file')")), 400
    f = request.files['file']
    return jsonify(success({"pattern": "normal", "confidence": 0.91})), 200
