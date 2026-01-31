import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# Directory to store generated reports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "..", "reports")
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_pdf_report(user_id: str, report_data: str) -> str:
    """
    Generate a production-grade PDF health report.

    Args:
        user_id (str): Unique identifier of the user
        report_data (str): Structured health summary text

    Returns:
        str: Generated PDF filename
    """

    timestamp = int(datetime.utcnow().timestamp())
    filename = f"report_{user_id}_{timestamp}.pdf"
    filepath = os.path.join(REPORT_DIR, filename)

    # Create PDF
    pdf = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    x_margin = 2 * cm
    y_position = height - 2 * cm

    # Header
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(x_margin, y_position, "CureVox Health Report")

    y_position -= 1.2 * cm
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x_margin, y_position, f"User ID: {user_id}")

    y_position -= 0.6 * cm
    pdf.drawString(
        x_margin,
        y_position,
        f"Generated (UTC): {datetime.utcnow().isoformat()}"
    )

    # Section Title
    y_position -= 1.2 * cm
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(x_margin, y_position, "Health Summary")

    # Body
    y_position -= 0.8 * cm
    pdf.setFont("Helvetica", 10)

    for line in report_data.splitlines():
        if y_position < 2 * cm:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = height - 2 * cm

        pdf.drawString(x_margin, y_position, line)
        y_position -= 0.45 * cm

    # Finalize PDF
    pdf.showPage()
    pdf.save()

    return filename
