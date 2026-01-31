# services/predict_service.py
import json
from utils.predict_utils import safe_text_classify, safe_audio_check

def analyze_symptoms(symptoms_text: str):
    # Simple deterministic mock classification
    return safe_text_classify(symptoms_text)

def analyze_cough(filestorage):
    # filestorage is werkzeug FileStorage
    # Save temporarily and run quick heuristic (placeholder)
    return safe_audio_check(filestorage, mode="cough")

def analyze_breath(filestorage):
    return safe_audio_check(filestorage, mode="breath")
