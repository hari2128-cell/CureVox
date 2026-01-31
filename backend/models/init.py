from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model with common fields."""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Import models after db initialization
from .user import User
from .diagnosis import Diagnosis, RashAnalysis, AudioAnalysis
from .session import UserSession
from .report import HealthReport

__all__ = ['db', 'User', 'Diagnosis', 'RashAnalysis', 'AudioAnalysis', 'UserSession', 'HealthReport']