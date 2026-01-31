from utils.response import success
from utils.audio_utils import extract_audio_features

def analyze_audio(path):
    features = extract_audio_features(path)
    return success("Audio analyzed", features)
