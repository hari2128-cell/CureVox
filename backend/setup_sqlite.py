#!/usr/bin/env python3
"""
SQLite Setup Script for CureVox
Run this script to set up everything for SQLite database.
"""

import os
import secrets
import json
from pathlib import Path

def generate_secret_key(length=64):
    """Generate a secure secret key."""
    return secrets.token_hex(length // 2)

def setup_environment():
    """Set up environment variables and configuration."""
    
    print("🔧 Setting up CureVox with SQLite Database...")
    print("=" * 50)
    
    # Create necessary directories
    directories = ['logs', 'uploads', 'instance']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Generate secure keys
    secret_key = generate_secret_key(64)
    jwt_secret_key = generate_secret_key(64)
    
    # Create .env file
    env_content = f"""# ============================================
# CUREVOX - SQLITE CONFIGURATION
# ============================================

# Application Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY={secret_key}

# Database Configuration - SQLite
DATABASE_URL=sqlite:///curevox.db

# JWT Configuration
JWT_SECRET_KEY={jwt_secret_key}
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Firebase Configuration (REQUIRED - Get from Firebase Console)
FIREBASE_API_KEY=AIzaSyDgFn1QhRF03fmkKSKYH5iUf8yIb8RZZUU
FIREBASE_AUTH_DOMAIN=curevox-2e0b5.firebaseapp.com
FIREBASE_PROJECT_ID=curevox-2e0b5
FIREBASE_STORAGE_BUCKET=curevox-2e0b5.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=606613902975
FIREBASE_APP_ID=1:606613902975:web:1492a99459ee64e59f114a

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,mp3,wav,m4a

# CORS Configuration
CORS_ORIGINS=http://localhost:5000

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with generated secrets")
    
    # Create requirements.txt if not exists
    if not os.path.exists('requirements.txt'):
        requirements = """Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
python-dotenv==1.0.0
firebase-admin==6.3.0
Werkzeug==3.0.1
Pillow==10.1.0
"""
        
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        print("✅ Created requirements.txt")
    
    # Create firebase_admin.example.json
    firebase_example = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY