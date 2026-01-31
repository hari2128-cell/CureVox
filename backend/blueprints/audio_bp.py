# blueprints/audio_bp.py
from flask import Blueprint, request, jsonify
from services.predict_service import analyze_cough, analyze_breath
from utils.response import success, error

audio_bp = Blueprint("audio", __name__)

@audio_bp.route("/cough", methods=["POST"])
def cough():
    if "file" not in request.files:
        return jsonify(error("no file uploaded")), 400
    f = request.files["file"]
    result = analyze_cough(f)
    return jsonify(success(result))

@audio_bp.route("/breath", methods=["POST"])
def breath():
    if "file" not in request.files:
        return jsonify(error("no file uploaded")), 400
    f = request.files["file"]
    result = analyze_breath(f)
    return jsonify(success(result))
