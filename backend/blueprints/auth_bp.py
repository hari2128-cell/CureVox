from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from utils.security_utils import generate_token

load_dotenv()
auth_bp = Blueprint('auth', __name__)

USERS_DB = {}  # Production: Replace with PostgreSQL/Redis

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email in USERS_DB and check_password_hash(USERS_DB[email]['password'], password):
        token = generate_token(email)
        session['user'] = email
        return jsonify({'token': token, 'user': email})
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email in USERS_DB:
        return jsonify({'error': 'User exists'}), 400
    
    USERS_DB[email] = {
        'password': generate_password_hash(password),
        'analyses': []
    }
    token = generate_token(email)
    session['user'] = email
    return jsonify({'token': token, 'user': email})
