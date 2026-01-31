from flask import Blueprint, request, jsonify, send_file
from utils.response import success, error
from services.report_service import generate_pdf_report

report_bp = Blueprint("report", __name__)

@report_bp.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    user_id = data.get("user_id", "guest")
    report_data = data.get("report", {})
    pdf_path = generate_pdf_report(user_id, report_data)
    return jsonify(success({"pdf_path": pdf_path})), 200

@report_bp.route("/download/<path:fname>", methods=["GET"])
def download(fname):
    # serve generated pdf from reports/ folder
    return send_file(f"reports/{fname}", as_attachment=True)
