# services/rash_service.py
from PIL import Image
import io

def analyze_rash_image(filestorage):
    # returns a simple analysis using average redness
    img = Image.open(filestorage.stream).convert("RGB").resize((200,200))
    pixels = list(img.getdata())
    avg_r = sum([p[0] for p in pixels]) / len(pixels)
    avg_g = sum([p[1] for p in pixels]) / len(pixels)
    avg_b = sum([p[2] for p in pixels]) / len(pixels)
    # heuristic: if red is significantly higher than green/blue -> inflammation
    red_score = max(0, (avg_r - (avg_g+avg_b)/2))
    severity = "normal"
    if red_score > 25:
        severity = "mild redness"
    if red_score > 45:
        severity = "moderate redness"
    if red_score > 80:
        severity = "severe redness - recommend consult"
    return {"avg_r": round(avg_r,1), "avg_g": round(avg_g,1), "avg_b": round(avg_b,1), "severity": severity}
