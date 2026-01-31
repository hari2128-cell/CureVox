# utils/file_utils.py
import os
def save_file(storage, folder="uploads", prefix="f"):
    os.makedirs(folder, exist_ok=True)
    filename = storage.filename or f"{prefix}.bin"
    path = os.path.join(folder, filename)
    storage.save(path)
    return path
