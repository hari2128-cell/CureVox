from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
diagnosis_bp = Blueprint('diagnosis', __name__, url_prefix='/api/diagnosis')
reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
health_bp = Blueprint('health', __name__, url_prefix='/api/health')

# Import routes after blueprints are created
from . import auth, diagnosis, reports, chat, health

__all__ = ['auth_bp', 'diagnosis_bp', 'reports_bp', 'chat_bp', 'health_bp']