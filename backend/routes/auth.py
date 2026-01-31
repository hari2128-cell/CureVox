from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from ..models import db, User
from ..services.firebase_service import FirebaseService
from ..utils.decorators import jwt_required, validate_content_type
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__, url_prefix='/api/auth')
firebase_service = FirebaseService()

@bp.route('/complete-profile', methods=['POST'])
@validate_content_type('multipart/form-data', 'application/x-www-form-urlencoded')
def complete_profile():
    """Complete user profile after Firebase phone authentication."""
    try:
        data = request.form
        id_token = data.get('id_token')
        
        if not id_token:
            return jsonify({
                'success': False,
                'message': 'Authentication token required',
                'error': 'MISSING_TOKEN'
            }), 400
        
        # Verify Firebase token
        decoded_token = firebase_service.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
        
        # Get user data from form
        user_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'phone_number': data.get('phone_number')
        }
        
        # Validate required fields
        if not all(user_data.values()):
            return jsonify({
                'success': False,
                'message': 'All fields are required',
                'error': 'MISSING_FIELDS'
            }), 400
        
        # Get or create user
        user = firebase_service.get_or_create_user(firebase_uid, user_data)
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'name': user.name,
                'email': user.email,
                'roles': ['user']
            }
        )
        
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Create session
        request_info = {
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string,
            'device_info': request.headers.get('User-Agent')
        }
        
        firebase_service.create_user_session(user.id, access_token, request_info)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except ValueError as e:
        logger.warning(f"Profile completion failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'error': 'AUTHENTICATION_FAILED'
        }), 401
    except Exception as e:
        logger.error(f"Profile completion error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.',
            'error': 'SERVER_ERROR'
        }), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required
def refresh_token():
    """Refresh access token."""
    try:
        # Refresh token logic
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'message': 'User not found or inactive',
                'error': 'USER_INACTIVE'
            }), 401
        
        new_access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'name': user.name,
                'email': user.email,
                'roles': ['user']
            }
        )
        
        return jsonify({
            'success': True,
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to refresh token',
            'error': 'REFRESH_FAILED'
        }), 500


@bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """Logout user and invalidate session."""
    try:
        # Get token from request
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            firebase_service.invalidate_session(token)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Logout failed',
            'error': 'LOGOUT_FAILED'
        }), 500


@bp.route('/profile', methods=['GET'])
@jwt_required
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


@bp.route('/profile', methods=['PUT'])
@jwt_required
def update_profile():
    """Update user profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'error': 'USER_NOT_FOUND'
            }), 404
        
        data = request.json
        
        # Update allowed fields
        updatable_fields = [
            'name', 'date_of_birth', 'gender', 'blood_group',
            'height', 'weight', 'allergies', 'chronic_conditions',
            'current_medications', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relation'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update profile',
            'error': 'UPDATE_FAILED'
        }), 500