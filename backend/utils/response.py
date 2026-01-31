def success(data):
    return {"status": "success", "data": data}

def error(msg):
    return {"status": "error", "message": msg}
