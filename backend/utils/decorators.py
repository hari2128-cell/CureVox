from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt
import logging

logger = logging.getLogger(__name__)

def jwt_required(fn):
    """Decorator for JWT protected routes."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error': 'INVALID_TOKEN'
            }), 401
    return wrapper


def role_required(*required_roles):
    """Decorator for role-based access control."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                jwt_data = get_jwt()
                user_roles = jwt_data.get('roles', [])
                
                if not any(role in user_roles for role in required_roles):
                    return jsonify({
                        'success': False,
                        'message': 'Insufficient permissions',
                        'error': 'FORBIDDEN'
                    }), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Role check failed: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Authentication required',
                    'error': 'INVALID_TOKEN'
                }), 401
        return wrapper
    return decorator


def rate_limited(fn):
    """Decorator for rate limiting."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Rate limiting logic (Flask-Limiter handles this)
        return fn(*args, **kwargs)
    return wrapper


def validate_content_type(*allowed_types):
    """Validate request content type."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            content_type = request.content_type or ''
            
            if not any(allowed_type in content_type for allowed_type in allowed_types):
                return jsonify({
                    'success': False,
                    'message': f'Unsupported media type. Expected: {", ".join(allowed_types)}',
                    'error': 'UNSUPPORTED_MEDIA_TYPE'
                }), 415
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator