import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
import jwt
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import firebase_admin
from firebase_admin import credentials, auth
from werkzeug.utils import secure_filename
import uuid
import json
from pathlib import Path
import sqlite3

# Load environment variables
load_dotenv()

# Configure logging
# Create logs directory if it doesn't exist
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
           static_folder='frontend',
           template_folder='frontend')

# SQLite Configuration Class
class SQLiteConfig:
    # Security
    # Security (STRICT)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    if not SECRET_KEY or not JWT_SECRET_KEY:
        raise RuntimeError("SECRET_KEY and JWT_SECRET_KEY must be set")
    
    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///curevox.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite specific settings for better performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,  # Allow multiple threads
            'timeout': 30,  # Timeout for database locks
        },
        'poolclass': None,  # SQLite doesn't need connection pooling
    }
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800)))
    JWT_TOKEN_LOCATION = ['headers']
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'm4a'}
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')
    
    # Session
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Apply configuration
app.config.from_object(SQLiteConfig)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Initialize rate limiter (in-memory for SQLite setup)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"],  # Increased limits
    storage_uri="memory://",  # In-memory storage for SQLite setup
    strategy="fixed-window"
)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize Firebase Admin
try:
    # Try to load Firebase credentials from environment or file
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    if firebase_creds_json:
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
    elif os.path.exists('firebase_admin.json'):
        cred = credentials.Certificate('firebase_admin.json')
    else:
        logger.warning("Firebase Admin SDK not initialized - running without Firebase")
        cred = None
    
    if cred:
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")
    logger.warning("Running without Firebase authentication")

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    
    # Profile fields
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    
    # Medical info
    allergies = db.Column(db.Text, nullable=True)
    chronic_conditions = db.Column(db.Text, nullable=True)
    current_medications = db.Column(db.Text, nullable=True)
    
    # Emergency contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    emergency_contact_relation = db.Column(db.String(50), nullable=True)
    
    # Account
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'blood_group': self.blood_group,
            'height': self.height,
            'weight': self.weight,
            'allergies': self.allergies,
            'chronic_conditions': self.chronic_conditions,
            'current_medications': self.current_medications,
            'emergency_contact': {
                'name': self.emergency_contact_name,
                'phone': self.emergency_contact_phone,
                'relation': self.emergency_contact_relation
            } if self.emergency_contact_name else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    diagnosis_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    symptoms = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    doctor_note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='diagnoses')
    
    def to_dict(self):
        return {
            'id': self.id,
            'diagnosis_type': self.diagnosis_type,
            'title': self.title,
            'description': self.description,
            'symptoms': self.symptoms,
            'severity': self.severity,
            'confidence_score': self.confidence_score,
            'recommendations': self.recommendations,
            'doctor_note': self.doctor_note,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

# Helper functions
def validate_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Content-Type must be application/json',
                'error': 'INVALID_CONTENT_TYPE'
            }), 400
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Initialize database
def init_database():
    """Initialize SQLite database with proper settings."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Optimize SQLite database
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if db_path.startswith('/'):
            # Absolute path
            db_full_path = db_path
        else:
            # Relative path
            db_full_path = os.path.join(app.root_path, db_path)
        
        # Apply SQLite optimizations
        try:
            conn = sqlite3.connect(db_full_path)
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute('PRAGMA foreign_keys = ON')
            
            # Set journal mode to WAL for better concurrency
            cursor.execute('PRAGMA journal_mode = WAL')
            
            # Increase cache size
            cursor.execute('PRAGMA cache_size = -2000')  # 2MB cache
            
            # Set synchronous mode to NORMAL for better performance
            cursor.execute('PRAGMA synchronous = NORMAL')
            
            # Enable memory-mapped I/O
            cursor.execute('PRAGMA mmap_size = 268435456')  # 256MB
            
            conn.commit()
            conn.close()
            
            logger.info(f"SQLite database initialized and optimized at {db_full_path}")
        except Exception as e:
            logger.warning(f"Could not optimize SQLite database: {str(e)}")
        
        logger.info("Database tables created successfully")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found',
        'error': 'NOT_FOUND'
    }), 404

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        'success': False,
        'message': 'Too many requests. Please try again later.',
        'error': 'RATE_LIMIT_EXCEEDED'
    }), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'error': 'INTERNAL_SERVER_ERROR'
    }), 500

# Serve frontend files
@app.route('/')
@app.route('/login')
def serve_login():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/home')
def serve_home():
    return send_from_directory(app.static_folder, 'home.html')

@app.route('/audio-analysis')
def serve_audio_analysis():
    return send_from_directory(app.static_folder, 'audio-analysis.html')

@app.route('/rash-analysis')
def serve_rash_analysis():
    return send_from_directory(app.static_folder, 'rash-analysis.html')

@app.route('/chat')
def serve_chat():
    return send_from_directory(app.static_folder, 'chat.html')

@app.route('/reports')
def serve_reports():
    return send_from_directory(app.static_folder, 'reports.html')

@app.route('/about')
def serve_about():
    return send_from_directory(app.static_folder, 'about.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/<path:filename>')
@limiter.exempt  # ADD THIS LINE - exempt static files from rate limiting
def serve_static(filename):
    """Serve static files (HTML, CSS, JS, images)."""
    try:
        return send_from_directory(app.static_folder, filename)
    except:
        return jsonify({
            'success': False,
            'message': 'File not found',
            'error': 'NOT_FOUND'
        }), 404

# API Routes
@app.route('/api/config/firebase', methods=['GET'])
@limiter.exempt  # ADD THIS LINE - exempt from rate limiting
def get_firebase_config():
    """Return Firebase configuration for frontend."""
    try:
        config = {
            'apiKey': os.environ.get('FIREBASE_API_KEY', 'AIzaSyDgFn1QhRF03fmkKSKYH5iUf8yIb8RZZUU'),
            'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN', 'curevox-2e0b5.firebaseapp.com'),
            'projectId': os.environ.get('FIREBASE_PROJECT_ID', 'curevox-2e0b5'),
            'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'curevox-2e0b5.firebasestorage.app'),
            'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '606613902975'),
            'appId': os.environ.get('FIREBASE_APP_ID', '1:606613902975:web:1492a99459ee64e59f114a')
        }
        
        return jsonify(config), 200
        
    except Exception as e:
        logger.error(f"Error getting Firebase config: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to load configuration',
            'error': 'CONFIG_ERROR'
        }), 500

@app.route('/api/init', methods=['GET'])
@limiter.exempt
def init_check():
    """Simple endpoint to check if server is ready."""
    return jsonify({
        'success': True,
        'ready': True,
        'timestamp': datetime.utcnow().isoformat()
    })

@jwt.unauthorized_loader
def missing_token_callback(reason):
    return jsonify({
        "authenticated": False,
        "error": "Missing or invalid token",
        "reason": reason
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({
        "authenticated": False,
        "error": "Invalid token",
        "reason": reason
    }), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "authenticated": False,
        "error": "Token expired"
    }), 401


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status without requiring JWT."""
    try:
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            # Try to verify JWT token
            token = auth_header.split(' ')[1]
            try:
                current_user = get_jwt_identity()
                user = User.query.get(current_user)
                if user:
                    return jsonify({
                        'success': True,
                        'authenticated': True,
                        'user': user.to_dict()
                    })
            except:
                # Token is invalid/expired
                pass
        
        # Check for token in cookies (alternative)
        token = request.cookies.get('access_token')
        if token:
            try:
                current_user = get_jwt_identity()
                user = User.query.get(current_user)
                if user:
                    return jsonify({
                        'success': True,
                        'authenticated': True,
                        'user': user.to_dict()
                    })
            except:
                pass
        
        # Not authenticated
        return jsonify({
            'success': True,
            'authenticated': False,
            'message': 'Not authenticated'
        })
        
    except Exception as e:
        logger.error(f"Auth status error: {str(e)}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': 'SERVER_ERROR'
        }), 500

@app.route('/api/auth/complete-profile', methods=['POST'])
@limiter.limit("5 per minute")
@validate_json
def complete_profile():
    """Complete user profile after Firebase authentication."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone_number', 'id_token']
        missing = [field for field in required_fields if not data.get(field)]
        
        if missing:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing)}',
                'error': 'MISSING_FIELDS'
            }), 400
        
        # Validate email
        if '@' not in data['email'] or '.' not in data['email'].split('@')[1]:
            return jsonify({
                'success': False,
                'message': 'Invalid email address',
                'error': 'INVALID_EMAIL'
            }), 400
        
        # Verify Firebase token if Firebase is initialized
        firebase_uid = None
        if firebase_admin._apps:
            try:
                decoded_token = auth.verify_id_token(data['id_token'])
                firebase_uid = decoded_token['uid']
                
                # Verify phone number matches
                if decoded_token.get('phone_number') != data['phone_number']:
                    return jsonify({
                        'success': False,
                        'message': 'Phone number verification failed',
                        'error': 'PHONE_MISMATCH'
                    }), 401
            except Exception as e:
                logger.warning(f"Token verification failed: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Invalid authentication token',
                    'error': 'INVALID_TOKEN'
                }), 401
        else:
            # For development without Firebase, generate a mock UID
            firebase_uid = f"dev_{uuid.uuid4().hex}"
            logger.warning(f"Running without Firebase. Using mock UID: {firebase_uid}")
        
        # Check if user already exists
        existing_user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if existing_user:
            # Update last login
            existing_user.last_login = datetime.utcnow()
            existing_user.name = data['name']
            existing_user.email = data['email']
            db.session.commit()
            user = existing_user
        else:
            # Create new user
            user = User(
                firebase_uid=firebase_uid,
                name=data['name'],
                email=data['email'],
                phone_number=data['phone_number'],
                last_login=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user created: {user.id} - {user.email}")
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'name': user.name,
                'email': user.email,
                'roles': ['user']
            }
        )
        
        # Store session info
        session_data = {
            'user_id': user.id,
            'ip_address': request.remote_addr,
            'login_time': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'session': session_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile completion error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.',
            'error': 'SERVER_ERROR'
        }), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'error': 'USER_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch profile',
            'error': 'SERVER_ERROR'
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user."""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'error': 'USER_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch user',
            'error': 'SERVER_ERROR'
        }), 500

@app.route('/api/diagnosis/rash/upload', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def upload_rash_image():
    """Upload rash/skin image for analysis."""
    try:
        current_user_id = get_jwt_identity()
        
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided',
                'error': 'NO_FILE'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No selected file',
                'error': 'NO_FILE'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF',
                'error': 'INVALID_FILE_TYPE'
            }), 400
        
        # Generate secure filename
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        secure_filename_base = secure_filename(file.filename.rsplit('.', 1)[0])
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename_base}.{original_ext}"
        
        # Create user-specific directory
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user_id), 'images')
        os.makedirs(user_dir, exist_ok=True)
        
        filepath = os.path.join(user_dir, unique_filename)
        file.save(filepath)
        
        # Mock analysis (replace with actual ML model)
        analysis_result = {
            'condition': 'Possible Dermatitis',
            'confidence': 78.5,
            'description': 'The image shows signs of mild dermatitis with redness and slight swelling.',
            'recommendations': [
                'Apply hydrocortisone cream 2-3 times daily',
                'Avoid scratching the affected area',
                'Keep the area clean and dry',
                'Schedule follow-up in 3 days if no improvement'
            ],
            'severity': 'low',
            'requires_doctor': False
        }
        
        # Create diagnosis record
        diagnosis = Diagnosis(
            user_id=current_user_id,
            diagnosis_type='rash',
            title='Skin Rash Analysis',
            description=analysis_result['description'],
            symptoms='Redness, swelling, irritation',
            severity=analysis_result['severity'],
            confidence_score=analysis_result['confidence'],
            recommendations='\n'.join(analysis_result['recommendations'])
        )
        
        db.session.add(diagnosis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded and analyzed successfully',
            'analysis': analysis_result,
            'diagnosis_id': diagnosis.id,
            'file_url': f'/uploads/{current_user_id}/images/{unique_filename}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Rash upload error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to process image',
            'error': 'PROCESSING_ERROR'
        }), 500

@app.route('/api/diagnosis/history', methods=['GET'])
@jwt_required()
def get_diagnosis_history():
    """Get user's diagnosis history."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query diagnoses
        diagnoses_query = Diagnosis.query.filter_by(user_id=current_user_id)
        
        # Get total count
        total = diagnoses_query.count()
        
        # Get paginated results
        diagnoses = diagnoses_query.order_by(Diagnosis.created_at.desc()) \
                                  .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'diagnoses': [d.to_dict() for d in diagnoses.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': diagnoses.pages,
                'has_next': diagnoses.has_next,
                'has_prev': diagnoses.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch history',
            'error': 'SERVER_ERROR'
        }), 500

@app.route('/api/auth/verify-token', methods=['POST', 'GET'])
@limiter.exempt  # Prevent rate limiting issues
def verify_token():
    """Verify JWT token without requiring @jwt_required decorator."""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'authenticated': False,
                'error': 'No token provided'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token using flask_jwt_extended
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        
        # This verifies the token and sets the context
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'success': False,
                'authenticated': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone_number': user.phone_number
            }
        }), 200
        
    except Exception as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': 'Invalid or expired token'
        }), 401

@app.route('/api/health', methods=['GET'])
@limiter.exempt
def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check upload directory
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        
        # Test write permission
        test_file = os.path.join(upload_dir, '.test_write')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': 'connected',
                'storage': 'writable',
                'firebase': 'initialized' if firebase_admin._apps else 'not_initialized'
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except:
        return jsonify({
            'success': False,
            'message': 'File not found',
            'error': 'NOT_FOUND'
        }), 404

# Service worker with correct MIME type
@app.route('/sw.js')
def service_worker():
    response = make_response("""
console.log('Service Worker loaded');

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', event => {
    event.waitUntil(clients.claim());
});

// DO NOT INTERCEPT FETCH
self.addEventListener('fetch', () => {});
""")
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response


@app.route('/api/admin/backup', methods=['POST'])
@jwt_required()
def backup_database():
    """Create a backup of the SQLite database."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Simple admin check (in production, use proper role-based auth)
        if user.id != 1:  # Assuming first user is admin
            return jsonify({
                'success': False,
                'message': 'Unauthorized',
                'error': 'UNAUTHORIZED'
            }), 403
        
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not db_path.startswith('/'):
            db_path = os.path.join(app.root_path, db_path)
        
        backup_path = f"{db_path}.backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        import shutil
        shutil.copy2(db_path, backup_path)
        
        return jsonify({
            'success': True,
            'message': 'Backup created successfully',
            'backup_path': backup_path,
            'size': os.path.getsize(backup_path)
        }), 200
        
    except Exception as e:
        logger.error(f"Backup error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Backup failed',
            'error': 'BACKUP_FAILED'
        }), 500

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
def no_cache(response):
    if request.path.endswith('login.html'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
    return response


# Main entry point
if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Get configuration
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"""
    🚀 CureVox Medical Assistant
    ============================
    📁 Database: SQLite
    🌐 Server: {host}:{port}
    🔧 Mode: {'Development' if debug else 'Production'}
    
    📍 Endpoints:
    - Frontend: http://{host}:{port}/
    - API: http://{host}:{port}/api/
    - Health: http://{host}:{port}/api/health
    - Init Check: http://{host}:{port}/api/init
    - Firebase Config: http://{host}:{port}/api/config/firebase
    
    🔑 Firebase: {'Configured' if firebase_admin._apps else 'Not configured'}
    💾 Uploads: {app.config['UPLOAD_FOLDER']}
    📊 Database: {app.config['SQLALCHEMY_DATABASE_URI']}
    """)
    
    # Run the app
    app.run(host=host, port=port, debug=debug, threaded=True)