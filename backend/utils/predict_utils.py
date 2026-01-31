# utils/predict_utils.py
import os, tempfile, hashlib

def safe_text_classify(text):
    t = text.lower()
    tags = []
    tscore = 0
    if "cough" in t: tags.append("cough")
    if "fever" in t or "temperature" in t: tags.append("fever")
    if "rash" in t or "skin" in t: tags.append("rash")
    # basic severity heuristic
    if any(w in t for w in ["severe","difficulty","bleeding","chest pain","shortness"]):
        severity = "high"
    else:
        severity = "low"
    return {"tags": tags or ["general"], "severity": severity, "raw": text[:400]}

def safe_audio_check(filestorage, mode="cough"):
    # small deterministic result: hash file length etc.
    content = filestorage.read()
    filestorage.stream.seek(0)
    h = hashlib.sha1(content).hexdigest()
    length = len(content)
    # heuristic
    if length == 0:
        return {"mode": mode, "result": "no audio", "confidence": 0.0}
    # simple mapping to demo predictions
    if length % 3 == 0:
        label = "normal"
        conf = 0.85
    elif length % 3 == 1:
        label = "possible abnormality"
        conf = 0.66
    else:
        label = "needs review"
        conf = 0.5
    return {"mode": mode, "label": label, "confidence": conf, "sample_hash": h[:10]}
