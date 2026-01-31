import os  # ← THIS LINE WAS MISSING!

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-production'

def generate_token():
    return "temp-jwt-token-for-testing"
