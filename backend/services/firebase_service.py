import os
import firebase_admin
from firebase_admin import credentials, auth, exceptions
from google.auth.exceptions import GoogleAuthError
from ..models import db, User, UserSession
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    """Service for Firebase authentication and user management."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase Admin SDK."""
        try:
            cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase_admin.json')
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                # For production, use environment variable or default credentials
                firebase_admin.initialize_app()
                logger.info("Firebase Admin SDK initialized with default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    def verify_id_token(self, id_token):
        """Verify Firebase ID token."""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except exceptions.InvalidIdTokenError as e:
            logger.warning(f"Invalid ID token: {str(e)}")
            raise ValueError("Invalid authentication token")
        except exceptions.ExpiredIdTokenError as e:
            logger.warning(f"Expired ID token: {str(e)}")
            raise ValueError("Authentication token expired")
        except GoogleAuthError as e:
            logger.error(f"Google auth error: {str(e)}")
            raise ValueError("Authentication service error")
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise ValueError("Failed to verify authentication token")
    
    def get_or_create_user(self, firebase_uid, user_data):
        """Get existing user or create new user."""
        try:
            # Check if user exists
            user = User.query.filter_by(firebase_uid=firebase_uid).first()
            
            if user:
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                logger.info(f"User {firebase_uid} logged in")
                return user
            
            # Create new user
            user = User(
                firebase_uid=firebase_uid,
                name=user_data.get('name'),
                email=user_data.get('email'),
                phone_number=user_data.get('phone_number'),
                last_login=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user created: {firebase_uid}")
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating/getting user: {str(e)}")
            raise
    
    def create_user_session(self, user_id, session_token, request_info):
        """Create a new user session."""
        try:
            session = UserSession(
                user_id=user_id,
                session_token=session_token,
                ip_address=request_info.get('ip_address'),
                user_agent=request_info.get('user_agent'),
                device_info=request_info.get('device_info'),
                login_time=datetime.utcnow()
            )
            
            db.session.add(session)
            db.session.commit()
            
            return session
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def invalidate_session(self, session_token):
        """Invalidate user session."""
        try:
            session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if session:
                session.is_active = False
                session.logout_time = datetime.utcnow()
                db.session.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating session: {str(e)}")
            raise